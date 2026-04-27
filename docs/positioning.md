<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Positioning: more than a prompt collection

> **One-line claim.** image2-workbench turns prompt packs into
> reproducible CLI, Skill, and web ChatGPT workflows for OpenAI's
> `gpt-image-2`, with cost estimates, preflight validation, and a run
> ledger.

## Why we need a different category

Prompt collections are useful. They are the fastest way to learn what a
model can do, and the gallery in this repo intentionally keeps that
copy-paste path alive. The problem starts when prompts need to become
repeatable workflows. After you have spent time running real workloads
against `gpt-image-2`, your questions shift:

- You no longer ask "what's a good prompt for a SWOT card?" — you ask
  "what does a 1500-image rerun cost across two snapshots, and which
  templates regressed?"
- You no longer wonder whether `transparent` background works — you have
  hit the validation wall, googled it, and now want a tool that refuses
  the call locally before you waste a round-trip to OpenAI's API.
- You no longer trust ad-hoc Python notebooks — you want a CLI surface,
  a structured exit code, an append-only ledger, and a sidecar JSON
  next to every produced image.

The public ecosystem around image-generation models has many strong
**prompt collections**: curated `.md` files, prompt atlases, and
copy-paste examples. They are useful as inspiration. A workbench adds
the machinery needed when those prompts must be compiled, checked,
batched, measured, and explained.

## What prompt collections already cover

Most prompt collections are optimized for browsing and copy/paste:
domain categories, example outputs, and ready-made strings. That is a
real user need, and image2-workbench's gallery exists for the same
reason.

What those collections usually do not cover is the production workflow:
cost forecasting, local parameter validation, preflight moderation,
sidecar metadata, run history, and stable exit codes. They also usually
do not distinguish a transparent-background failure (exit 4) from a
rate-limit failure (exit 2) from an authentication failure (exit 1).

That is the gap.

## What a production workbench adds

We frame the workbench around three pillars:

### 1. Cost predictability (cost + batch)

`i2w cost compare --size 1024x1024,1536x1024,2048x2048 --quality low,medium,high`
prints a 9-row matrix with both the official-table price and a
pixel-heuristic fallback. `i2w cost budget` lets you set a ceiling and
get told *up front* whether a planned sweep blows it. Token-track
estimates (`--token-estimate`) triangulate against OpenAI's calculator.
The Batch API integration (`i2w batch sweep`) cuts cost in half for
workloads where you can wait.

### 2. Error granularity (preflight + structured envelopes)

`i2w preflight <prompt-file>` runs all the local-side validation we can
without spending a token: parameter ranges, size constraints, format
guards, and (optionally) a `/v1/moderations` call to flag likely
failures before the expensive image-generation call. When something
*does* fail, the workbench emits a structured `ErrorEnvelope` with a
stable `code` field and one of seven granular exit codes (see
[`error-codes.md`](./error-codes.md)). A wrapper script can branch on
the exit code without parsing prose.

### 3. Observability (the ledger)

Every render, edit, preflight, and batch call appends one JSONL row to
`~/.image2/ledger.jsonl` (overridable via `IMAGE2_LEDGER_PATH`).
`i2w ledger query` aggregates by template / snapshot / template+snapshot
and prints success rate, p50/p95 latency, total cost, and an
error-code breakdown. `i2w ledger drift` compares two snapshots; a
single command tells you whether the new model rev moved your numbers
or not.

## How to think about us versus alternatives

| You want…                                                  | Use…                                  |
|------------------------------------------------------------|---------------------------------------|
| Inspiration / quick prompts to copy into web ChatGPT       | A prompt collection (any of the above), or our gallery (`docs/gallery/`) |
| A reproducible CLI that fails loudly on invalid parameters | image2-workbench (this repo)          |
| Cost forecasting for a 1000+ image sweep                   | image2-workbench (`i2w cost compare`) |
| A 50% discount on non-urgent batch workloads               | image2-workbench (`i2w batch sweep`)  |
| Per-snapshot regression tracking                           | image2-workbench (`i2w ledger drift`) |
| A bilingual paste-ready prompt for the iOS app             | image2-workbench gallery (no Python required) |

The right way to think about it: **prompt collections help you explore;
image2-workbench keeps that value and makes the workflow executable,
auditable, bilingual, and batchable**. Many users will start with the
gallery and never need the ledger; that is fine. When repeatability,
cost, or debugging matters, the ledger and structured CLI are what you
reach for.

## What we are explicitly *not* trying to be

- We are not trying to win by adding the most prompts. Our gallery is
  auto-compiled from templates; it is a build artifact, not a hand-tuned
  list.
- We are not a model-agnostic image library. We bind tightly to
  `gpt-image-2` snapshots and refuse parameters that snapshot does not
  support (e.g. `transparent` background, `input_fidelity`).
- We are not a hosted SaaS. The ledger is a local file. There is no
  account, no upload, no telemetry. Your prompts and metrics stay on
  your machine.

## v0.2.0 status

The three pillars above are present in v0.2.0 as source-checkout alpha
features. The companion docs:

- [`cost-modeling.md`](./cost-modeling.md) — formulas behind the cost
  forecasts, including the official-table track, pixel-heuristic
  fallback, token estimator, and Batch API discount math.
- [`error-codes.md`](./error-codes.md) — the seven granular exit codes
  and their stable `code` strings.

What is intentionally not claimed yet: a large prompt atlas, a verified
prompt corpus, OCR/image-diff visual evals, multi-model routing, or
wheel/PyPI packaging of top-level templates. Those are v0.3+ work.

Both READMEs (`README.md` / `README.zh.md`) lead with the same claim:
this is more than a prompt collection because it makes prompt packs
executable, auditable, bilingual, and batchable.
