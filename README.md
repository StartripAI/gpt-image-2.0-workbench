<!--
SPDX-License-Identifier: CC-BY-4.0
-->

# image2-workbench

> **image2-workbench is more than a prompt collection: it is a
> spec-first production workbench around OpenAI's `gpt-image-2`.** It
> turns prompt packs into reproducible CLI, Skill, and web ChatGPT
> workflows, with cost estimates, preflight validation, and a run ledger.

> **Status:** v0.2.0 GitHub source-checkout release. APIs and template
> formats may still change while the workbench is alpha; PyPI/wheel
> packaging is left to v0.3.

中文版：[README.zh.md](./README.zh.md)

## Why more than a prompt collection?

Curated prompt lists are useful: they are great inspiration and a fast
way to learn what the model responds to. They become harder to use when
you need repeatable outputs across templates, sizes, costs, and model
snapshots. Three workbench pillars close that gap:

- **Cost predictability (`i2w cost` + `i2w batch`).** Two-track cost
  model — official `(size, quality)` table plus a pixel-area heuristic
  fallback — with a token-track estimator and a Batch API discount path
  (50% off, up to 24h). See [`docs/cost-modeling.md`](./docs/cost-modeling.md).
- **Granular errors (`i2w preflight` + structured envelopes).** Seven
  exit codes (`AUTH`, `RATE_LIMIT`, `MODERATION_BLOCKED`, `VALIDATION`,
  `API_OTHER`, `INTERNAL`, `OK`) and stable `code` strings, so shell
  wrappers can branch without parsing prose. Local validation and
  pre-moderation refuse bad calls before they hit OpenAI. See
  [`docs/error-codes.md`](./docs/error-codes.md).
- **Observability (the ledger).** Every render, edit, preflight, and
  batch call appends one JSONL row. `i2w ledger query` aggregates by
  template / snapshot, prints success rate and p50/p95 latency, and
  `i2w ledger drift` compares two snapshots in one command.

Prompt collections help you explore. image2-workbench keeps that value,
then makes the prompts executable, auditable, bilingual, and batchable.
For the full positioning thesis, see
[`docs/positioning.md`](./docs/positioning.md).

## Three form factors

| Layer | Where it runs | What you ship |
|-------|---------------|---------------|
| **L1 — Skill bundle** | Codex, Claude Code, Anthropic Skills, any agent that loads `SKILL.md` | A thin SKILL bundle in [`skills/gpt-image/`](./skills/gpt-image/) that calls into the CLI |
| **L2 — Python CLI / SDK** | Local terminals, CI, your own agent | The `i2w` command from this checkout (`image2-workbench` package name) |
| **L3 — Prompt-only templates** | Web ChatGPT, mobile, anywhere there's no Python | Compiled bilingual markdown under [`docs/gallery/`](./docs/gallery/) — copy into a chat box and go |

L1 is a thin wrapper around L2. L3 is a build artifact of L2's compiler — the
same template definitions yield both a runnable command and a paste-ready
prompt.

## Quick start

After cloning your fork (or working from a local checkout):

```bash
cd image2-workbench && pip install -e ".[dev]"

i2w --help                 # list verbs
i2w doctor capabilities    # probe what your account / org / model supports
pytest -q                  # run unit and smoke tests
```

If you're reading from a fork, replace with your fork URL.

See [`docs/getting-started.en.md`](./docs/getting-started.en.md) for a longer
walkthrough.

## V1 scope (4 domains, 16 templates)

- **business** — SWOT cards, pitch slides, LinkedIn carousels, data dashboards
- **academic** — scientific diagrams, chalkboard proofs, multilingual education posters, journal posters
- **uiux** — iOS app mockups, web dashboards, design system cards, social covers (XHS-style)
- **anime** — character reference sheets, 8-panel comics, editorial city posters, candid CCD-style portraits

V0.3 will focus on packaging the templates for wheel/PyPI installs and
expanding the prompt atlas / verified corpus / Skill-pack story. V2 will
add `industrial`, `ecommerce`, automatic ingestion, plugin distribution,
and a TypeScript shim.

## Status of features

| Component | State |
|-----------|-------|
| Project scaffolding, license layering, CI | shipped |
| CLI surface (`i2w` with 11 commands) | shipped |
| API runtimes (Images API + Responses API) | shipped |
| Spec-first template DSL & compiler | shipped |
| Domain templates (4 × 4 = 16) | shipped |
| Catalog + provenance store | shipped |
| Eval rubrics (text / layout / edit / continuity) | shipped |
| Costing (official token track + heuristic) | shipped |
| Docs + gallery export | shipped |

## Licensing

Code (`src/`, `tests/`, `scripts/`, `.github/`) is licensed under
**Apache-2.0** — see [`LICENSE`](./LICENSE).

Templates and documentation (`templates/`, `docs/`, `README*`) are licensed
under **CC BY 4.0** — see [`LICENSE-CONTENT`](./LICENSE-CONTENT).

Third-party prompt records under `corpus/normalized/` carry per-record license
metadata; see [`corpus/manifests/source_registry.yml`](./corpus/manifests/source_registry.yml).

For attributions and methodological inspiration, see [`NOTICE`](./NOTICE).

## Contributing

Read [`AGENTS.md`](./AGENTS.md) first — it explains file ownership,
forbidden anti-patterns (don't copy from other repos, don't pass deprecated
parameters), and the definition of done for V1.

## Provenance

This project takes structural inspiration only — directory layout, the idea
of bundling a Skill + CLI + reference docs — from the public structure of
[`wuyoscar/gpt_image_2_skill`](https://github.com/wuyoscar/gpt_image_2_skill)
(CC BY 4.0). No source code, prompt text, or README prose was copied.
Correctness rules (parameter ranges, valid sizes, defaults) are derived from
OpenAI's public documentation. See `NOTICE` for full details.
