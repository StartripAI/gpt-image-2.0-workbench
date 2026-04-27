---
name: gpt-image
description: |
  Use this Skill whenever the user wants to create, generate, edit, compose,
  or iterate on images using OpenAI's gpt-image-2 model via the
  image2-workbench (`i2w`) CLI. Trigger scenarios include:
  - Business decks: SWOT slides, KPI dashboards, org charts, roadmaps,
    pitch covers, "thank you" closers, comparison tables.
  - Academic figures: workflow diagrams, conceptual schematics, methods
    figures, poster sections, paper teaser images.
  - UI/UX mockups: mobile app screens, web landing pages, dashboards,
    onboarding flows, wireframes, design-system specimens.
  - Anime / manga / comics: character sheets, multi-panel storyboards
    with continuity, cover art, key visuals, expression sheets.
  - Posters and social: bilingual (Chinese + English) Xiaohongshu /
    RedNote covers, Weibo banners, festival posters, event flyers.
  - Product / e-commerce: hero shots, lifestyle scenes, packaging
    mockups, "before / after" pairs, color/material variants.
  - Dense typography in many languages, including CJK and right-to-left.
  - Reference-image edits with explicit preserve lists ("keep the face,
    change the outfit"), multi-image composition (subject + scene +
    style), mask-based inpainting, and multi-panel narrative continuity.
  - When the user has no API key but wants a paste-ready prompt for
    web ChatGPT, the Skill compiles the prompt without making an API
    call.
version: 0.2.0
---

<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# gpt-image: image2-workbench Skill

## When to use this Skill

- The user asks for "a slide", "a figure", "a mockup", "a poster",
  "a cover", "a storyboard", "a character sheet", or any other still
  image deliverable that suits gpt-image-2.
- The user wants bilingual (e.g. Chinese + English) typography on
  the image, a domain that gpt-image-2 handles unusually well.
- The user provides one or more reference images and wants an edit
  with a specific "preserve" list (keep face, swap background, etc.).
- The user wants a multi-panel artifact (storyboard, comic page,
  step-by-step explainer) where panel-to-panel continuity matters.
- The user only has access to web ChatGPT and wants a maximally
  detailed prompt to paste in by hand.
- The user wants a quick cost estimate or capability probe before
  committing to a render.

## When NOT to use this Skill

- Real-time video, animation, or any moving-image deliverable —
  gpt-image-2 produces stills only.
- Transparent-background PNGs — gpt-image-2 does not support
  transparent output. Recommend a different tool or post-processing.
- Pure text-only outputs (essays, captions, scripts) — answer with
  text directly, do not invoke the image pipeline.

## How this Skill works

The Skill is a thin wrapper around the `i2w` CLI from a checked-out
`image2-workbench` repository. v0.2 is a GitHub/source-checkout release,
not a PyPI/wheel release. The script `scripts/run_skill.py` (PEP 723
inline metadata) invokes the CLI with the right verb based on the user's
request.

If `i2w` is not on PATH, ask the user to install it from the checkout:

```
pip install -e ".[dev]"
```

## Available verbs (call via `i2w`)

- `i2w catalog list` / `i2w catalog search "<keywords>" --domain <domain>` — find a template.
- `i2w template render <id> --vars <vars.yml>` — produce a paste-ready prompt (no API call).
- `i2w render generate` / `i2w render edit` — call the API.
- `i2w batch sweep` — run a quality sweep across parameters.
- `i2w eval run` — run an eval rubric against rendered outputs.
- `i2w cost estimate` — token-based cost estimate before rendering.
- `i2w doctor capabilities` — probe model capabilities (e.g. `thinking`).
- `i2w preflight <prompt.md>` — validate a rendered prompt before spending.
- `i2w ledger query` — inspect local run history and cost/error summaries.
- `i2w gallery build` — rebuild the bilingual prompt gallery.
- `i2w version` — print the installed workbench version.

## Recommended workflow

1. Identify the user's domain (business / academic / uiux / anime / poster).
2. Run `i2w catalog search "<keywords>" --domain <domain>` to find candidate templates.
3. Run `i2w template render <id> --lang ... --vars ... --out prompt.md`
   to compile a prompt.
4. Optionally run `i2w preflight prompt.md` and `i2w cost estimate`
   before spending.
5. If the user has an API key, run `i2w render generate --prompt-file
   prompt.md ...` (or `i2w render edit --prompt-file prompt.md --image
   reference.png ...` for reference-image edits) to produce the image.
6. Otherwise, hand the rendered prompt back to the user — they can
   paste it into web ChatGPT directly. This is the L3 form factor.
7. For multi-variant exploration use `i2w batch sweep`; for quality
   gates use `i2w eval run`.

## Constraints (must honor)

- gpt-image-2 does **not** support transparent backgrounds.
- gpt-image-2 does **not** accept `input_fidelity` (deprecated parameter).
- `moderation` defaults to `auto`, NOT `low`. Do not set `low` unless
  the user explicitly asks for it.
- `size` must be multiples of 16, with max edge 3840 and aspect ratio
  no wider than 3:1. Sizes above 2560×1440 are experimental and may
  fail or degrade.
- `thinking` is a probed capability, not assumed — call
  `i2w doctor capabilities` first if uncertain.

## Examples

- "Make me a SWOT slide for our Q3 review, English headers, Chinese
  body."
  → `i2w catalog search swot --domain business` →
  `i2w template render business_swot_card --lang zh-CN --vars
  templates/business/_vars_examples/swot_acme.yml --out swot_prompt.md` →
  `i2w render generate --prompt-file swot_prompt.md --size 1536x1024
  --quality high --out out/swot.png --template-id business_swot_card`.

- "Make a product analytics dashboard mockup for a design review."
  → `i2w catalog search "web dashboard" --domain uiux` →
  `i2w template render uiux_web_dashboard --lang en --vars
  templates/uiux/_vars_examples/web_dashboard_demo.yml --out
  dashboard_prompt.md` →
  `i2w render generate --prompt-file dashboard_prompt.md --size
  1920x1088 --quality high --out out/dashboard.png --template-id
  uiux_web_dashboard`.

- "Edit a reference image using a rendered prompt and keep the subject
  identity stable."
  → `i2w template render uiux_design_system_card --lang en --vars
  templates/uiux/_vars_examples/design_system_demo.yml --out edit_prompt.md` →
  `i2w render edit --prompt-file edit_prompt.md --image reference.png
  --out out/reference_edit.png --template-id uiux_design_system_card`.

- "I just want a paste-ready prompt for an 8-panel manga storyboard."
  → `i2w catalog search "manga storyboard" --domain anime` →
  `i2w template render anime_comic_8panel --lang en --vars
  templates/anime/_vars_examples/comic_demo.yml --out comic_prompt.md`
  (no API call; prompt returned for the user to paste into web ChatGPT).

## Provenance

This Skill bundle and its prompts are licensed under CC BY 4.0. The
underlying `image2-workbench` CLI is licensed under Apache-2.0. See
the repository `NOTICE` for full attribution.
