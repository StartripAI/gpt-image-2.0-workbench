<!--
SPDX-License-Identifier: CC-BY-4.0
-->

# AGENTS.md — image2-workbench Repository Conventions

> Source-of-truth plan: `/Users/star/.claude/plans/image-2-business-snappy-metcalfe.md`

## Project goal

Build a multi-surface OpenAI gpt-image-2 workbench (Skill + CLI + bilingual
prompt templates) covering four V1 domains: business / academic / uiux / anime.
The product targets three runtime environments simultaneously — Codex, Claude
Code, and web ChatGPT — through a layered form-factor design (L1 Skill,
L2 CLI/SDK, L3 prompt-only templates).

## Languages and tech stack

- **V1 is Python 3.11+ only.** No TypeScript in V1.
- **Required deps:** `openai>=1.55,<2`, `typer[all]>=0.12`, `pydantic>=2.6`,
  `pyyaml>=6`, `rich>=13`, `jinja2>=3.1`, `python-dotenv>=1.0`,
  `jsonschema>=4`.
- **Dev deps:** `pytest>=8`, `pytest-cov`, `ruff>=0.6`, `mypy>=1.10`.
- **No runtime additions** without updating `pyproject.toml` and noting the
  reason in the PR description.

## License layering

| Path                                | License                              | SPDX header to use         |
|-------------------------------------|--------------------------------------|----------------------------|
| `src/`, `tests/`, `scripts/`        | Apache-2.0                           | `Apache-2.0`               |
| `.github/`                          | Apache-2.0                           | `Apache-2.0`               |
| `skills/gpt-image/scripts/*.py`      | Apache-2.0                           | `Apache-2.0`               |
| `templates/`, `docs/`, `README*`    | CC BY 4.0                            | `CC-BY-4.0`                |
| `skills/gpt-image/SKILL.md`          | CC BY 4.0                            | `CC-BY-4.0`                |
| `AGENTS.md`, `SECURITY.md`, `NOTICE` | CC BY 4.0                           | `CC-BY-4.0`                |
| `corpus/manifests/`                 | CC BY 4.0                            | `CC-BY-4.0`                |
| `corpus/normalized/*.jsonl`         | Per-record (see source_registry.yml) | (record-level metadata)    |
| `corpus/harvested/`                 | Gitignored, never redistributed      | n/a                        |

Add an `SPDX-License-Identifier:` line at the top of new files when the
license is non-obvious.

## File ownership map (V1 build)

These boundaries are enforced during the parallel-agent V1 build. Stay in
your lane unless coordinating a cross-cutting change with the team.

| Owner agent | Path scope | Deliverable |
|-------------|------------|-------------|
| agent-1 | `pyproject.toml`, `README*`, `LICENSE*`, `NOTICE`, `AGENTS.md`, `.github/`, `.gitignore`, `src/image2_workbench/__init__.py`, all subpackage `__init__.py`, `tests/conftest.py`, `tests/unit/test_scaffold.py` | scaffold + governance |
| agent-2 | `src/image2_workbench/cli.py`, `commands/*.py` (excluding `__init__.py`), `tests/smoke/` | CLI surface |
| agent-3 | `runtimes/*.py` (excluding `__init__.py`), `artifacts/*.py` (excluding `__init__.py`) | API runtimes + artifact writers |
| agent-4 | `skills/gpt-image/SKILL.md`, `skills/gpt-image/scripts/run_skill.py` | Skill bundle |
| agent-5 | `compiler/*.py` (excluding `__init__.py`), `templates/_schema/template.schema.yml` | Template DSL & compiler |
| agent-6 | `templates/business/*.yml`, `templates/academic/*.yml` | Domain templates 1 |
| agent-7 | `templates/uiux/*.yml`, `templates/anime/*.yml` | Domain templates 2 |
| agent-8 | `catalog/*.py` (excluding `__init__.py`), `corpus/manifests/source_registry.yml`, `corpus/normalized/.gitkeep` | Catalog + provenance |
| agent-9 | `evals/runner.py`, `evals/report.py`, `evals/rubrics/*.py`, `costing/*.py`, `tests/golden/` | Evals + costing |
| agent-10 | `docs/*.md`, `docs/gallery/*.md` | Docs + gallery |

**Shared files (NEVER edit without coordination):** `pyproject.toml`,
`src/image2_workbench/__init__.py`, `README.md`, `README.zh.md`, `LICENSE`,
`LICENSE-CONTENT`, `NOTICE`, `AGENTS.md`. agent-1 owns these.

## Coding conventions

- Run `ruff check src tests` before committing; CI fails on lint errors.
- Use type hints on all public functions and class attributes.
- Use **pydantic v2** models for all configs, template specs, and API
  request/response shapes.
- Default to writing **no comments**. Add a one-liner only when the *why* is
  non-obvious — a hidden constraint, an OpenAI API quirk, a deliberate
  divergence from the obvious approach.
- Test new behavior with `pytest`. Smoke tests for CLI go under
  `tests/smoke/`; unit tests for individual modules go under `tests/unit/`;
  golden-set evaluation cases go under `tests/golden/`.
- Filenames are `snake_case.py`. CLI verbs are lowercase ASCII (`render`,
  `template`, `doctor`).

## Forbidden anti-patterns

- **Do not copy code, prompt text, or README prose** from
  `wuyoscar/gpt_image_2_skill` or any other prompt-collection repository.
  Structural inspiration is fine; redistribution is not.
- **Do not pass `input_fidelity`** to gpt-image-2 — the parameter is not
  supported on this model. The CLI must reject the flag with a clear error.
- **Do not pass `background: transparent`** — gpt-image-2 only supports
  `auto` and `opaque`. The validator must reject the value.
- **Do not default `moderation` to `low`.** The OpenAI default is `auto` and
  we follow it.
- **Do not hardcode "2K" as a maximum size.** The validator must allow up to
  `3840 × 2160` with `max_edge ≤ 3840`, multiples of 16, aspect ratio ≤ 3:1,
  and total pixels in `[655_360, 8_294_400]`. Sizes above `2560 × 1440` are
  flagged experimental.
- **Do not assume `thinking` is a public API parameter** of gpt-image-2.
  Treat it as a probed capability — `i2w doctor capabilities` reports
  whether the current account/org supports it; templates may *hint* at it,
  but runtimes must gracefully fall back when the parameter is rejected.
- **Do not commit secrets** (`.env`, API keys). The `.gitignore` excludes
  these by default; double-check before pushing.

## Definition of done (V1)

V1 is shippable when **all** of the following hold:

1. `pip install -e ".[dev]"` succeeds on a clean Python 3.11 environment.
2. `i2w --help` lists 11 commands: `catalog`, `template`, `render`, `batch`,
   `eval`, `cost`, `doctor`, `preflight`, `ledger`, `gallery`, `version`.
3. `pytest -q` is green (unit + smoke + golden subset).
4. All 16 V1 templates pass schema validation (`i2w template list` shows
   16 entries; each compiles without errors).
5. `i2w doctor capabilities` runs without crashing and reports the probe
   results clearly (even if API access is unavailable, it reports that
   gracefully).
6. The bilingual gallery (`docs/gallery/business.md`, `academic.md`,
   `uiux.md`, `anime.md`, `index.md`) is generated from the templates.
7. CI is green on Python 3.11 and 3.12.

Anything additional (live API tests, real eval pass-rate targets, plugin
distribution) is V2 territory.
