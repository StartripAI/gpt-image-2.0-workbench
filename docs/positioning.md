<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Positioning: image2-workbench is a production workbench, not a prompt collection

> **One-line claim.** image2-workbench is a production workbench around
> OpenAI's `gpt-image-2`. It predicts cost before you spend, validates
> parameters before they fail, pre-screens prompts through moderation,
> and ledgers every call so you can see what fails and why.

## Why we need a different category

A flat list of clever prompts is a great starting point for a hobbyist,
but it is not a serious deliverable for a team that ships images at
production scale. By the time you have spent two weeks running real
workloads against `gpt-image-2`, your problems have shifted:

- You no longer ask "what's a good prompt for a SWOT card?" — you ask
  "what does a 1500-image rerun cost across two snapshots, and which
  templates regressed?"
- You no longer wonder whether `transparent` background works — you have
  hit the validation wall, googled it, and now want a tool that refuses
  the call locally before you waste a round-trip to OpenAI's API.
- You no longer trust ad-hoc Python notebooks — you want a CLI surface,
  a structured exit code, an append-only ledger, and a sidecar JSON
  next to every produced image.

The public ecosystem around image-generation models is saturated with
**prompt collections** — repos that publish curated `.md` files of clever
strings. They are useful as inspiration. They are not useful as the
backbone of a production pipeline.

## What "prompt collections" already cover

To be concrete, the four most-trafficked GitHub repositories near the
`gpt-image-2` keyword are roughly the following:

| Repo                         | Stars  | Shape                              |
|------------------------------|-------:|------------------------------------|
| `EvoLinkAI/awesome-gpt-image-1-prompts` | ~5500 | Curated prompt list (markdown)        |
| `YouMind/gpt-image-1-prompts`           | ~3000 | Curated prompt list (markdown + json) |
| `Anil-matcha/Awesome-GPT-Image-1`       | ~1700 | Curated prompt list (markdown)        |
| `wuyoscar/gpt_image_2_skill`            | ~700  | Skill bundle wrapping curated prompts |

(Numbers are approximate; the exact counts drift week to week.)

Every one of these is fundamentally a *flat collection* — a list of
strings, organized by domain, optimized for browsing and copy/paste.
They are not engineered tools. They do not estimate cost. They do not
validate parameters. They do not run preflight moderation. They do not
keep a ledger. They do not produce sidecar metadata. They do not
distinguish a transparent-background failure (exit 4) from a rate-limit
failure (exit 2) from an authentication failure (exit 1).

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

The right way to think about it: **a prompt collection helps a single
person on a single image; a workbench helps a team on a thousand
images**. Most users will start with the gallery and never need the
ledger; that is fine. But when the third person joins the team and the
first cost surprise lands, the ledger is what you reach for.

## What we are explicitly *not* trying to be

- We are not a prompt-marketing site. We do not curate "the 100 best
  prompts." Our gallery is auto-compiled from templates; it is a build
  artifact, not a hand-tuned list.
- We are not a model-agnostic image library. We bind tightly to
  `gpt-image-2` snapshots and refuse parameters that snapshot does not
  support (e.g. `transparent` background, `input_fidelity`).
- We are not a hosted SaaS. The ledger is a local file. There is no
  account, no upload, no telemetry. Your prompts and metrics stay on
  your machine.

## V1.5 status

The three pillars above are live as of V1.5. The companion docs:

- [`cost-modeling.md`](./cost-modeling.md) — formulas behind the cost
  forecasts, including the official-table track, pixel-heuristic
  fallback, token estimator, and Batch API discount math.
- [`error-codes.md`](./error-codes.md) — the seven granular exit codes
  and their stable `code` strings.

Both READMEs (`README.md` / `README.zh.md`) lead with the same claim:
this is a workbench, not a collection.
