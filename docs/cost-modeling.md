<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Cost modeling

> **TL;DR.** image2-workbench triangulates dollar costs from two tracks
> (an official `(size, quality)` table and a pixel-area heuristic) and a
> token estimator. Numbers are forecasts; canonical billing always
> comes from OpenAI's pricing calculator. Use `i2w cost compare` to
> generate a matrix and `i2w cost budget` to gate sweeps before you
> spend.

## The two-track model

We deliberately maintain two independent cost tracks and label every
estimate with which track produced it. This is the same shape that
appears in the `CostEstimate.track` field
(`"official_table"` | `"heuristic_pixel"`).

### Track A — `official_table`

A small dictionary mapping documented `(size, quality)` pairs to per-image
USD prices, sourced from OpenAI's public pricing near the `gpt-image-2`
launch (2026-04). The rows we ship are:

| size      | low    | medium | high  |
|-----------|-------:|-------:|------:|
| 1024×1024 | 0.006  | 0.053  | 0.211 |
| 1024×1536 | 0.008  | 0.063  | 0.250 |
| 1536×1024 | 0.008  | 0.063  | 0.250 |
| 2048×2048 | 0.020  | 0.150  | 0.600 |

`quality="auto"` is treated as `medium` for forecasting purposes
(the modal pick in our internal traces) and an explicit note is added
to the `CostEstimate.note` field so callers do not silently mistake the
forecast for a guarantee.

### Track B — `heuristic_pixel`

When `(size, quality)` is **not** in the official table — for example a
non-canonical resolution like `1280×768` — we fall back to a pixel-area
heuristic. The shape of the heuristic, in pseudocode, is:

```
per_image = base_per_pixel * width * height * QUALITY_MULT[quality]
```

with `QUALITY_MULT = {low: 1, medium: 4, high: 16}` reflecting the
roughly-quartic step in image-output token consumption between quality
tiers. The result is labelled `track="heuristic_pixel"` so callers
know to verify against the calculator before forecasting at scale.

Both tracks return a `CostEstimate` with the same fields:

```python
class CostEstimate(BaseModel):
    size: str
    quality: Literal["low", "medium", "high", "auto"]
    n: int
    per_image_usd: float
    total_usd: float
    track: Literal["official_table", "heuristic_pixel"]
    note: str
```

## The token-track estimator

`--token-estimate` toggles a *third*, complementary view: instead of
giving you a dollar number, the estimator reports how many tokens of
each kind the planned job will consume.

The formulas are conservative — biased toward over-estimation:

```
text_tokens_in   ≈ ceil(len(prompt) / 4)               # English-leaning
image_tokens_in  =  image_inputs * 256                  # 256 per edit reference
image_tokens_out =  1024 * (W*H / 1024**2) * QUALITY_MULT[quality] * n
```

A `thinking` parameter, when set, adds a proportional surcharge to the
running total:

```
thinking_overhead = subtotal * THINKING_OVERHEAD_MULT[thinking]

  THINKING_OVERHEAD_MULT = {auto: 0.25, low: 0.25, medium: 1.00, high: 2.50}
```

The function returns a `TokenEstimate`:

```python
class TokenEstimate(BaseModel):
    text_tokens_in: int
    image_tokens_in: int
    image_tokens_out: int
    thinking_overhead: int
    total_tokens: int
    track: Literal["token_table", "heuristic"]
```

`estimate_dollar_cost(token_est, size, quality, n)` then folds the
thinking overhead into the official-table base:

```
dollar = base_total * (1 + thinking_overhead / (total - thinking_overhead))
```

This is the number printed by `i2w cost estimate --token-estimate`.

## Batch API discount math

The OpenAI Batch API runs the same workload at half the price in
exchange for up to a 24h turnaround. The `i2w cost` commands report
undiscounted Images API forecasts. To model a sweep that will be sent
through the Batch API, use `i2w batch sweep --route batch-api --dry-run`;
that command prints both the full estimate and the approximate discounted
total:

```
batch_total = base_total * 0.5
```

The discount applies uniformly across both cost tracks. A submitted
`batch-api` sweep records the discounted total in the ledger, so you can
compare the latency trade-off after the run.

## Worked example: 9-row comparison matrix

```bash
i2w cost compare --size 1024x1024,1536x1024,2048x2048 \
                 --quality low,medium,high
```

Prints (roughly):

| size      | quality | per_image_usd | total_usd | track          |
|-----------|---------|--------------:|----------:|----------------|
| 1024×1024 | low     |        0.0060 |    0.0060 | official_table |
| 1024×1024 | medium  |        0.0530 |    0.0530 | official_table |
| 1024×1024 | high    |        0.2110 |    0.2110 | official_table |
| 1536×1024 | low     |        0.0080 |    0.0080 | official_table |
| 1536×1024 | medium  |        0.0630 |    0.0630 | official_table |
| 1536×1024 | high    |        0.2500 |    0.2500 | official_table |
| 2048×2048 | low     |        0.0200 |    0.0200 | official_table |
| 2048×2048 | medium  |        0.1500 |    0.1500 | official_table |
| 2048×2048 | high    |        0.6000 |    0.6000 | official_table |

Multiply by `n` for a sweep. Use `i2w batch sweep --route batch-api
--dry-run` to preview the Batch API discount for a template sweep. Use
`i2w cost estimate --token-estimate` on a specific size/quality point to
see the underlying token counts.

## A worked budget gate

Create a YAML plan file:

```yaml
- size: 1024x1024
  quality: medium
  n: 200
```

```bash
i2w cost budget --plan budget.yml --max-usd 5.00
```

The estimator reports `200 × 0.053 = 10.60 USD`, which exceeds the
`--max-usd` cap, so the command exits non-zero. Wire this into your CI
to refuse runaway sweeps.

## Caveats

- **Numbers are estimates, not invoices.** OpenAI's pricing changes;
  the table at the top of this document is a snapshot near the
  `gpt-image-2` launch. The `track` field on every `CostEstimate` tells
  you which lane produced the number; if it says `heuristic_pixel`,
  check the calculator before billing.
- **Token-track is English-biased.** `text_tokens_in ≈ chars / 4`
  under-counts CJK and code-heavy prompts. We round up to compensate.
- **Thinking surcharge is empirical.** `medium=1.00x` and `high=2.50x`
  are reasonable working numbers; they are not contractual and can
  drift snapshot-to-snapshot.
- **Canonical pricing source:** [OpenAI pricing
  page](https://openai.com/api/pricing/) and the
  [calculator](https://platform.openai.com/docs/pricing). Always
  triangulate before forecasting at scale.

## See also

- [`positioning.md`](./positioning.md) — why cost predictability is one
  of the three pillars of the workbench.
- [`error-codes.md`](./error-codes.md) — exit codes and stable error
  identifiers used by `i2w cost`.
