<!--
SPDX-License-Identifier: CC-BY-4.0
-->

# image2-workbench

A multi-surface OpenAI gpt-image-2 workbench: **Skill + CLI + bilingual prompt
templates** for `business / academic / UI-UX / anime` scenarios.

> **Status:** V1 alpha — under active development. APIs and template formats
> may change before the first tagged release.

中文版：[README.zh.md](./README.zh.md)

## Why this exists

- OpenAI's `gpt-image-2` (released 2026-04-21, snapshot
  `gpt-image-2-2026-04-21`) covers serious workloads — multilingual typography,
  reference-image edits, narrative continuity, UI mockups, scientific
  illustrations — but the public ecosystem is fragmented across loose
  collections of prompts.
- Existing prompt repositories tend to ship a flat list of strings without a
  template DSL, validation, eval rubrics, or cost estimation; many bake in
  defaults that disagree with OpenAI's docs (e.g. defaulting `moderation` to
  `low`, hard-coding "2K" as a max).
- Many users live in **web ChatGPT**, not a Python terminal. We need a
  template format that survives outside any runtime and can be pasted directly
  into a chat box.

## Three form factors

| Layer | Where it runs | What you ship |
|-------|---------------|---------------|
| **L1 — Skill bundle** | Codex, Claude Code, Anthropic Skills, any agent that loads `SKILL.md` | A thin SKILL bundle in [`skills/gpt-image/`](./skills/gpt-image/) that calls into the CLI |
| **L2 — Python CLI / SDK** | Local terminals, CI, your own agent | The `i2w` command, packaged as `image2-workbench` |
| **L3 — Prompt-only templates** | Web ChatGPT, mobile, anywhere there's no Python | Compiled bilingual markdown under [`docs/gallery/`](./docs/gallery/) — copy into a chat box and go |

L1 is a thin wrapper around L2. L3 is a build artifact of L2's compiler — the
same template definitions yield both a runnable command and a paste-ready
prompt.

## Quick start

```bash
git clone https://github.com/image2-workbench/image2-workbench.git
cd image2-workbench
pip install -e ".[dev]"

i2w --help                 # list verbs
i2w doctor capabilities    # probe what your account / org / model supports
pytest -q                  # run unit and smoke tests
```

See [`docs/getting-started.en.md`](./docs/getting-started.en.md) for a longer
walkthrough.

## V1 scope (4 domains, 16 templates)

- **business** — SWOT cards, pitch slides, LinkedIn carousels, data dashboards
- **academic** — scientific diagrams, chalkboard proofs, multilingual education posters, journal posters
- **uiux** — iOS app mockups, web dashboards, design system cards, social covers (XHS-style)
- **anime** — character reference sheets, 8-panel comics, editorial city posters, candid CCD-style portraits

V2 will add `industrial`, `ecommerce`, automatic ingestion, plugin
distribution, and a TypeScript shim.

## Status of features

| Component | State |
|-----------|-------|
| Project scaffolding, license layering, CI | shipped |
| CLI surface (`i2w` with 8 verbs) | in progress |
| API runtimes (Images API + Responses API) | in progress |
| Spec-first template DSL & compiler | in progress |
| Domain templates (4 × 4 = 16) | in progress |
| Catalog + provenance store | in progress |
| Eval rubrics (text / layout / edit / continuity) | in progress |
| Costing (official token track + heuristic) | in progress |
| Docs + gallery export | in progress |

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
