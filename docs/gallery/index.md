<!--
SPDX-License-Identifier: CC-BY-4.0
-->

# Gallery

The gallery is a paste-ready, runtime-free surface for the workbench's
prompt templates. Every template is shown twice — once compiled to
zh-CN, once to en — directly in markdown. Open a domain page, find a
template, copy the block, paste into web ChatGPT.

## V1 domains

- [Business](./business.md) — SWOT cards, pitch slides, LinkedIn
  carousels, data dashboards.
- [Academic](./academic.md) — scientific diagrams, chalkboard proofs,
  multilingual edu-posters, journal posters.
- [UI / UX](./uiux.md) — iOS app mockups, web dashboards, design-system
  cards, social covers (Xiaohongshu).
- [Anime](./anime.md) — character sheets, 8-panel comics, city posters,
  candid scenes.

## How this gallery is generated

The gallery is **not hand-written**. It is auto-generated from
`templates/<domain>/*.yml` by the L2 compiler:

```
i2w template render <id> --lang zh,en --export markdown
```

Each render walks the seven-section DSL, substitutes the template's
default variables, and writes one fenced block per declared
`language_target`. The build then concatenates the per-template files
into the per-domain page.

This means the gallery never drifts from the runtime: when a template
changes, the next build refreshes the gallery from the same canonical
YAML.

## How to use it

If you live in web ChatGPT, see
[`../chatgpt-web-mode.md`](../chatgpt-web-mode.md) for the full
workflow. The short version: open a domain page, copy the prompt block
in the language you want, paste it into a ChatGPT conversation that has
image generation enabled, and replace the `<angle-bracket>`
placeholders before sending.

## License

The gallery markdown is CC BY 4.0. See
[`../licensing.md`](../licensing.md) for attribution guidance.
