<!--
SPDX-License-Identifier: CC-BY-4.0
-->

# Getting started

This guide walks you from a clean checkout to a finished image. It assumes
nothing about your account beyond a working Python install.

## Prerequisites

- **Python 3.11 or newer.** Check with `python3 --version`. The compiler and
  runtime expect modern type-hint syntax, and CI is pinned to 3.11 and 3.12.
- **A POSIX shell.** Bash, zsh, or fish all work. Examples below use bash.
- **An OpenAI API key — optional.** Many subcommands (template rendering,
  capability probing, cost estimation) work entirely offline. Only
  `i2w render generate` and `i2w render edit` need a live key, and they also
  require that your organization is **verified** for image generation.

If you do plan to call the live API, export the key once per shell session:

```bash
export OPENAI_API_KEY="sk-..."
```

The CLI also reads `.env` files in the current directory via `python-dotenv`,
so you can drop `OPENAI_API_KEY=...` into a project-local `.env` and have it
loaded automatically.

## Install

From the repository root:

```bash
pip install -e ".[dev]"
```

The `-e` (editable) flag means changes to the source tree take effect
immediately. The `[dev]` extras pull `pytest`, `ruff`, and `mypy`.

If you prefer an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Verify

Two commands confirm the install is healthy:

```bash
i2w --help     # should list eight verbs
pytest -q      # unit + smoke tests should pass
```

You should see verbs `catalog`, `template`, `render`, `batch`, `eval`,
`cost`, `doctor`, and `version`. If `i2w` is not on your `PATH`, your venv
is probably not activated; re-run the activation step above.

## The first three commands you'll run

Run these in order. Only the third one cares about your local repository
state, and none of them call the OpenAI API.

### 1. Probe what your account can do

```bash
i2w doctor capabilities
```

This walks through the model's capability surface — supported sizes,
quality levels, moderation modes, output formats, whether your org is
verified, whether `thinking` is exposed — and prints a tidy report. With no
API key set, it falls back to static defaults derived from the published
model card and tells you which checks were skipped.

Use this command first whenever you're on a new machine or a new account.
It saves you from chasing 401s later.

### 2. List available templates

```bash
i2w template list --domain business
```

This is offline and instant. It scans `templates/business/*.yml`, validates
each against the V1 schema, and prints id + 1-line description. Drop
`--domain` to see all four domains at once. Add `--lang en` or `--lang zh`
to restrict to one language target.

### 3. Render a template into a paste-ready prompt

```bash
i2w template render business_swot_card \
    --lang en \
    --vars vars.yml \
    --out prompt.md
```

`vars.yml` is a small YAML file with the variables the template declared
(company name, the four quadrant strings, etc.). The compiler substitutes
them, runs the seven-section DSL pass, and writes a `.md` file you can:

- Paste into ChatGPT to get an image without ever calling the API yourself
  (path A below), or
- Feed back into `i2w render generate` to drive the API directly
  (path B below).

If `--vars` is omitted, the compiler renders with the template's documented
defaults so you can see the shape of the output.

## Two paths to a finished image

### Path A — Pure web ChatGPT

You don't need Python after rendering once. The output of step 3 is plain
markdown with a single fenced prompt block per language target. Open
`prompt.md`, copy the entire en or zh-CN block, and paste it into a
ChatGPT conversation that has image generation enabled (Plus / Pro / Team
accounts; gpt-image-2 is the model behind the "create image" tool).

This path:

- Requires no API key.
- Has no per-image cost beyond your existing ChatGPT subscription.
- Is the right answer for designers, students, and product folks who don't
  want to manage credentials.

For the full workflow with two worked examples, see
[`chatgpt-web-mode.md`](./chatgpt-web-mode.md).

### Path B — `i2w render generate`

When you want artifact files on disk, deterministic re-runs, batch
generation, or CI integration, drive the API yourself:

```bash
i2w render generate \
    --prompt prompt.md \
    --size 1536x1024 \
    --quality high \
    --out out/swot.png
```

Outputs are written next to the image:

- `out/swot.png` — the image bytes.
- `out/swot.png.json` — a sidecar with the request, the response usage
  block, and the resolved cost.

This path requires `OPENAI_API_KEY` plus a verified org. If your org isn't
verified yet, the API returns a 403 and the CLI surfaces it as a single
clear line — no stack trace.

## Troubleshooting

**`OPENAI_API_KEY is not set`.** Export it in your shell or drop it into a
local `.env` file. `i2w doctor capabilities` will tell you whether the key
is being picked up.

**`organization not verified for gpt-image-2`.** This is a one-time setup on
the OpenAI dashboard under Settings → Organization. Verification typically
takes minutes; until it lands, only template rendering and dry-run cost
estimation work for you.

**`background: transparent is not supported on gpt-image-2`.** The model
only accepts `auto` or `opaque`. The validator rejects `transparent` early
with a helpful message; remove the field or switch to `auto`.

**`size 3840x2160 is experimental`.** Anything above `2560×1440` is
allowed but flagged as experimental — gpt-image-2's quality at maximum
resolution is uneven. Confirm with `--accept-experimental` if you really
want it; otherwise pick a 2K size.

**`pytest -q` fails with import errors.** You likely installed without the
`[dev]` extras, or your venv isn't activated. Re-run
`pip install -e ".[dev]"` inside the venv.

## Where to go next

- [`prompt-craft.md`](./prompt-craft.md) — the seven-section DSL and how to
  write prompts the model actually obeys.
- [`form-factors.md`](./form-factors.md) — when to use the Skill bundle, the
  CLI, or the prompt-only gallery.
- [`chatgpt-web-mode.md`](./chatgpt-web-mode.md) — the no-Python path for
  web ChatGPT users.
- [`licensing.md`](./licensing.md) — how the layered Apache-2.0 + CC BY 4.0
  license works in practice.
- [`gallery/index.md`](./gallery/index.md) — the bilingual prompt gallery
  for all four V1 domains.
