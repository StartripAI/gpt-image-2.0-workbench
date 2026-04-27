<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Gallery

The gallery is a paste-ready, runtime-free surface for the workbench's
prompt templates. Every template is shown twice — once compiled to
`zh-CN`, once to `en` — directly in markdown. Open a domain page, find a
template, copy the block, paste into web ChatGPT.

## V1 domains

Each domain ships four templates. The four `<domain>.md` pages below are
the canonical entry points:

- [Business](./business.md) — boardroom-grade SWOT cards, pitch slides,
  LinkedIn carousels, and data dashboards for working professionals.
- [Academic](./academic.md) — scientific diagrams, chalkboard proofs,
  multilingual education posters, and journal-style research posters.
- [UI / UX](./uiux.md) — iOS app mockups, web dashboards, design-system
  cards, and Xiaohongshu-flavored social covers for product designers.
- [Anime](./anime.md) — character reference sheets, 8-panel comics,
  editorial city posters, and CCD-style candid portraits.

## How this gallery is generated

The four `<domain>.md` files are **not hand-written**. They are
auto-generated from `templates/<domain>/*.yml` by the L2 compiler:

```bash
i2w gallery build
```

(If the `gallery build` verb is not yet wired up in your checkout, it is
landing in V1.5 — until then the per-domain pages are produced manually
by running `i2w template render <id> --lang zh,en --export markdown` and
concatenating the output.)

Each render walks the seven-section DSL, substitutes the template's
default variables, and writes one fenced block per declared
`language_target`. The build then concatenates the per-template files
into the per-domain page, so the gallery never drifts from the runtime —
when a template's YAML changes, the next build refreshes the gallery
from the same canonical source.

## Two paths to a finished image

The gallery supports both of the workbench's delivery paths:

- **Path A — web ChatGPT, copy-paste.** Open a domain page, copy the
  prompt block in your preferred language, paste it into a ChatGPT
  conversation that has image generation enabled, and replace the
  `<angle-bracket>` placeholders before sending. No Python required.
  Full walkthrough in [`../chatgpt-web-mode.md`](../chatgpt-web-mode.md).
- **Path B — CLI workflow.** Drive the compiler and the OpenAI API
  directly via `i2w template render` and `i2w render generate` for
  reproducible artifacts, batch generation, and CI integration. Full
  walkthrough in [`../getting-started.en.md`](../getting-started.en.md)
  (or [`../getting-started.zh.md`](../getting-started.zh.md)).

## License

The gallery markdown is **CC BY 4.0**. See
[`../licensing.md`](../licensing.md) for attribution guidance when
reusing prompts in derivative work.
