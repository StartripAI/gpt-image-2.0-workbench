<!--
SPDX-License-Identifier: CC-BY-4.0
-->

# Form factors

`image2-workbench` ships in three layers, each aimed at a different runtime
environment. The same templates power all three; you pick the layer that
fits where your work happens.

| Layer | Where it runs | What you ship |
|-------|---------------|---------------|
| L1 — Skill bundle | Codex, Claude Code, any agent that loads `SKILL.md` | `skills/gpt-image/` |
| L2 — Python CLI / SDK | Local terminals, CI, custom agents | The `i2w` command |
| L3 — Prompt-only templates | Web ChatGPT, mobile, anywhere without Python | Compiled markdown under `docs/gallery/` |

L1 wraps L2. L3 is generated from L2's compiler. You don't need to choose
once and stick with it — most users move between layers depending on the
task.

## L1 — Skill bundle

**When to use it.** You're driving an agent that supports Anthropic Skills
or a compatible SKILL.md format — Claude Code, Codex, or any harness that
auto-discovers skills. The agent should treat image generation as a
*capability it can decide to use*, not as a manual workflow you walk
through.

**What's inside.** A thin bundle in `skills/gpt-image/` containing:

- `SKILL.md` — the prompt the agent reads to learn what the skill does,
  when to invoke it, and what arguments it expects.
- `scripts/run_skill.py` — the entry script the skill calls into,
  delegating to the L2 CLI under the hood.

**How to install.** Copy or symlink the bundle into the agent's skills
directory. For Claude Code:

```bash
cp -R skills/gpt-image /path/to/your/.claude/skills/
```

For Codex and other agents, follow that agent's skill-discovery
convention; usually it's "drop the directory into a known location and
restart the harness".

**What it gives you.** The agent can now make calls like "render a SWOT
card for this company" without you naming a template id by hand. The
skill resolves the right template, fills variables from conversational
context, and runs `i2w render generate`.

**What it doesn't give you.** Programmatic access from your own scripts —
that's L2's job.

## L2 — CLI / SDK

**When to use it.** You have Python and you want batch generation,
scriptable workflows, CI integration, or fine-grained control over every
parameter. You're building automation, not having a conversation.

**What's inside.** The installable package `image2-workbench` exposing
the `i2w` console script. Eight verbs:

- `i2w doctor` — capability probe and environment check.
- `i2w template` — list, render, validate templates.
- `i2w render` — `generate` from a prompt, `edit` against a reference image.
- `i2w batch` — run many templates over many variable rows.
- `i2w eval` — run rubric-based evaluations against golden outputs.
- `i2w cost` — estimate cost from request shapes without calling the API.
- `i2w catalog` — manage the corpus and provenance metadata.
- `i2w version` — print the installed version.

**Entry points.**

```bash
i2w --help                                   # top-level
i2w template render <id> --lang en           # offline render
i2w render generate --prompt prompt.md       # live API call
i2w batch run plan.yml                       # many at once
```

You can also import the package directly:

```python
from image2_workbench.compiler import render_template
from image2_workbench.runtimes import generate_image
```

**What it gives you.** Determinism, reproducibility, sidecar metadata,
batched runs, cost estimation before you spend, evaluation rubrics, and a
clean import surface for your own agents.

**What it doesn't give you.** A solution if you're not on a machine with
Python — for that, see L3.

## L3 — Prompt-only templates

**When to use it.** You're in web ChatGPT (Plus / Pro / Team) and there
is no Python available — you're on a phone, on a borrowed machine, in a
classroom, or you simply prefer the chat UI to the terminal.

**What's inside.** Static markdown files under `docs/gallery/`,
organised by domain:

- `docs/gallery/business.md`
- `docs/gallery/academic.md`
- `docs/gallery/uiux.md`
- `docs/gallery/anime.md`

Each file contains every template in that domain, compiled to both
zh-CN and en, ready to copy into a chat box. The L3 layer carries no
runtime — it's just text.

**How to use.** Open the file in your browser, find a template that
matches your scenario, copy the entire compiled prompt block, paste it
into ChatGPT (with image generation enabled), and tweak the
`<angle-bracket>` variables to your needs before sending. See
[`chatgpt-web-mode.md`](./chatgpt-web-mode.md) for the full walkthrough.

**What it gives you.** Zero install, zero credentials, the same template
quality as the CLI path.

**What it doesn't give you.** Sidecar metadata, batch generation,
deterministic re-runs, cost reporting. Web ChatGPT's "create image" tool
doesn't expose those surfaces.

## How L3 is generated from L2

L3 isn't hand-written. It's a build artifact of the same compiler that
L2 uses for live runs:

```
templates/<domain>/*.yml
            │
            ▼
   ┌────────────────┐
   │   compiler     │   (i2w template render --export markdown)
   │  (L2 internal) │
   └────────────────┘
            │
            ├─ runtime path → API call → image + sidecar      (L2 live)
            │
            └─ markdown export → docs/gallery/<domain>.md     (L3)
```

When a template changes upstream, the L3 markdown re-renders from the
same source. The two surfaces never drift, because they read from one
canonical YAML.

This is also why the gallery files include both languages of every
template: the compiler emits all `language_targets` declared on the
template in a single render pass, and the markdown export concatenates
them with shared headers.

## Picking a layer

A short rubric, not a hard rule:

- Building an agent or a skill-aware harness → **L1**.
- Writing scripts, CI, batch jobs, evaluations → **L2**.
- Living inside web ChatGPT, designing on the fly → **L3**.

Most contributors end up using L2 for development and L3 for one-off
work, with L1 reserved for the agent integrations they ship.
