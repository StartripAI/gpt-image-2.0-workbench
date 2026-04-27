<!-- SPDX-License-Identifier: CC-BY-4.0 -->

<p align="center">
  <a href="./README.md">English</a> &nbsp;&middot;&nbsp; <a href="./README.zh.md">中文</a>
</p>

<h1 align="center">image2-workbench</h1>

<p align="center"><strong>A spec-first production workbench for OpenAI gpt-image-2.</strong><br/>52 executable templates &middot; 16 domains &middot; bilingual prompts &middot; cost / preflight / batch / ledger controls.</p>

<p align="center">
  <img src="docs/assets/hero.svg" alt="image2-workbench atlas hero" width="900" />
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white">
  <img alt="License code" src="https://img.shields.io/badge/code-Apache--2.0-blue">
  <img alt="License content" src="https://img.shields.io/badge/templates%2Fdocs-CC%20BY%204.0-lightgrey">
  <img alt="Domains" src="https://img.shields.io/badge/domains-16-1f6feb">
  <img alt="Templates" src="https://img.shields.io/badge/templates-52-238636">
  <img alt="Cards" src="https://img.shields.io/badge/domain%20cards-12-0d9488">
  <img alt="CLI" src="https://img.shields.io/badge/CLI-i2w%20%C2%B7%2011%20commands-334155">
  <img alt="Skill" src="https://img.shields.io/badge/Skill-7%20runtimes-7c3aed">
  <img alt="Bilingual" src="https://img.shields.io/badge/bilingual-EN%20%2B%20%E4%B8%AD%E6%96%87-d97706">
  <img alt="Tests" src="https://img.shields.io/badge/tests-420%20passing-15803d">
  <img alt="Status" src="https://img.shields.io/badge/status-v0.3%20alpha-ea580c">
</p>

<p align="center">
  <a href="#atlas--16-domains-52-templates"><strong>Explore Atlas &rarr;</strong></a>
  &nbsp;&middot;&nbsp;
  <a href="#quick-start"><strong>Quick Start &rarr;</strong></a>
  &nbsp;&middot;&nbsp;
  <a href="#showcase"><strong>Showcase &rarr;</strong></a>
  &nbsp;&middot;&nbsp;
  <a href="./skills/gpt-image/"><strong>View Skills &rarr;</strong></a>
  &nbsp;&middot;&nbsp;
  <a href="#faq"><strong>FAQ &rarr;</strong></a>
</p>

---

## Table of contents

- [Why a workbench?](#why-a-workbench)
- [Quick start](#quick-start)
- [Atlas &mdash; 16 domains, 52 templates](#atlas--16-domains-52-templates)
- [Showcase](#showcase)
- [Capabilities](#capabilities)
- [Workflow](#workflow)
- [CLI surface](#cli-surface)
- [Skill ecosystem](#skill-ecosystem)
- [FAQ](#faq)
- [Project structure](#project-structure)
- [Licensing](#licensing)
- [Contributing](#contributing)

---

## Why a workbench?

Curated prompt lists are great for inspiration. They start to creak when you need:

- **Reproducible outputs** across templates, sizes, costs, and model snapshots.
- **Bilingual delivery** (EN + 中文) of the same spec without translation drift.
- **Pre-API validation** that catches a broken request before it bills you.
- **An audit trail** that survives a model snapshot change six months from now.

This repo turns prompt packs into auditable, executable, batchable workflows around three pillars:

<table>
<tr>
  <th align="left" width="22%">Pillar</th>
  <th align="left" width="48%">What it does</th>
  <th align="left" width="30%">CLI surface</th>
</tr>
<tr>
  <td><strong>Cost predictability</strong></td>
  <td>Two-track cost: official <code>(size, quality)</code> table + pixel-area heuristic + Batch API discount.</td>
  <td><code>i2w cost compare</code><br/><code>i2w cost estimate</code><br/><code>i2w cost budget</code><br/><code>i2w batch sweep</code></td>
</tr>
<tr>
  <td><strong>Granular errors</strong></td>
  <td>Seven exit codes (<code>OK</code>, <code>AUTH</code>, <code>RATE_LIMIT</code>, <code>MODERATION_BLOCKED</code>, <code>VALIDATION</code>, <code>API_OTHER</code>, <code>INTERNAL</code>) plus local validation and pre-moderation.</td>
  <td><code>i2w preflight</code><br/><code>i2w doctor capabilities</code></td>
</tr>
<tr>
  <td><strong>Observability</strong></td>
  <td>Append-only JSONL ledger; success rate, p50 / p95 latency, cost-per-output, snapshot drift.</td>
  <td><code>i2w ledger query</code><br/><code>i2w ledger top-failures</code><br/><code>i2w ledger drift</code><br/><code>i2w ledger export</code></td>
</tr>
</table>

[Full positioning &rarr;](docs/positioning.md)

---

## Quick start

<details open>
<summary><strong>Install (~30s)</strong></summary>

```bash
# After cloning your fork (or working from a local checkout):
git clone https://github.com/StartripAI/gpt-image-2.0-workbench.git
cd gpt-image-2.0-workbench

python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

i2w --help                  # 11 commands
i2w doctor capabilities     # probe parameter compatibility (no API key needed)
pytest -q                   # the workbench tests itself (420+ passing)
```

</details>

<details>
<summary><strong>Render your first prompt (no API key required)</strong></summary>

```bash
i2w template render business_swot_card --lang en \
  --vars templates/business/_vars_examples/swot_acme.yml \
  --out out/swot.en.md
cat out/swot.en.md   # paste-ready into web ChatGPT
```

Then paste the markdown into ChatGPT's image dialog and download the image. This is the L3 path &mdash; web-only, no spend, no API key.

</details>

<details>
<summary><strong>Render through the API (requires <code>OPENAI_API_KEY</code>)</strong></summary>

```bash
export OPENAI_API_KEY=sk-...

# Catch broken requests locally before any spend:
i2w preflight out/swot.en.md --template-id business_swot_card

# Compare cost across (size, quality) before committing:
i2w cost compare --size 1024x1024,1536x1024 --quality low,medium,high

# Render and write a ledger row:
i2w render generate --prompt-file out/swot.en.md \
  --template-id business_swot_card \
  --size 1536x1024 --quality medium --out out/swot.png

# Inspect what just happened:
i2w ledger query --template business_swot_card
```

</details>

<details>
<summary><strong>Run a Batch API sweep (50% discount)</strong></summary>

```bash
i2w batch sweep \
  --template business_swot_card \
  --vars templates/business/_vars_examples/swot_acme.yml \
  --route batch-api \
  --dry-run                                # preview JSONL payload, no spend

i2w batch sweep ... --route batch-api      # submit when ready
```

</details>

[Longer walkthrough &rarr;](docs/getting-started.en.md) &nbsp;&middot;&nbsp; [Cost modeling &rarr;](docs/cost-modeling.md) &nbsp;&middot;&nbsp; [Error codes &rarr;](docs/error-codes.md)

---

<!-- BEGIN GALLERY (auto-generated by `i2w gallery readme`; do not edit by hand) -->

## Atlas — 16 domains, 52 templates

<table>
<tr>
<td width="33%" valign="top">

### academic · 4

| template | size | grader |
|---|---|---|
| <strong>academic_chalkboard_proof</strong><br/>Photorealistic university chalkboard with a four-step mathematical proof and QED line. | 1920x1088 | text_fidelity_dense |
| <strong>academic_journal_poster</strong><br/>Vertical 3-column conference poster with intro, methods, results, conclusion. | 1088x1920 | text_fidelity_dense |
| <strong>academic_multilingual_eduposter</strong><br/>Multilingual education infographic. Designed for Korean / Japanese / Chinese / Arabic / Hindi educational posters; the image's text is in language_native_name, NOT the prompt language. | 1920x1088 | text_fidelity_dense |
| <strong>academic_scientific_diagram</strong><br/>Museum-style cross-section or labeled scientific illustration with five callouts. | 1536x1024 | text_fidelity_dense |

[**View all academic →**](docs/gallery/academic.md)

</td>
<td width="33%" valign="top">

### advertising · 3

| template | size | grader |
|---|---|---|
| <strong>advertising_billboard_mockup</strong><br/>Photoreal urban billboard mockup with the hero ad pasted on a real-feeling outdoor placement. | 1920x1088 | layout |
| <strong>advertising_campaign_key_visual</strong><br/>Premium production-grade brand campaign hero key-visual with tagline, product name, and call-to-action. | 1920x1088 | text_fidelity_dense |
| <strong>advertising_storyboard_3frame</strong><br/>Three-panel storyboard sketch for a 30-second commercial, with brand seal beneath the panels. | 1536x1024 | continuity |

[**View all advertising →**](docs/gallery/advertising.md)

</td>
<td width="33%" valign="top">

### anime · 4

| template | size | grader |
|---|---|---|
| <strong>anime_ccd_candid</strong><br/>复古 CCD 相机风格自拍 / Vintage CCD camera-style candid (a non-photoreal staged "authenticity"). | 1088x1920 | text_fidelity_sparse |
| <strong>anime_character_sheet</strong><br/>Concept-art character reference sheet with three-view turnaround, expression sheet, and prop detail. | 1920x1088 | continuity |
| <strong>anime_city_poster</strong><br/>双语城市旅行海报 / Bilingual editorial city travel poster mixing calligraphic skyline and premium typography. | 1088x1920 | text_fidelity_dense |
| <strong>anime_comic_8panel</strong><br/>Eight-panel sequential manga page rendered in black-and-white seinen ink with strict character continuity. | 1024x1536 | continuity |

[**View all anime →**](docs/gallery/anime.md)

</td>
</tr>
<tr>
<td width="33%" valign="top">

### architecture · 3

| template | size | grader |
|---|---|---|
| <strong>architecture_facade_concept</strong><br/>Conceptual exterior facade rendering for an architecture studio's project poster. | 1536x1024 | text_fidelity_dense |
| <strong>architecture_presentation_board</strong><br/>Multi-panel architecture presentation board combining concept, diagram, render, and short text. | 1920x1088 | layout |
| <strong>architecture_site_diagram</strong><br/>Site plan / urban-context diagram with three labeled zones, drawn in plan view. | 1920x1088 | text_fidelity_dense |

[**View all architecture →**](docs/gallery/architecture.md)

</td>
<td width="33%" valign="top">

### business · 4

| template | size | grader |
|---|---|---|
| <strong>business_data_dashboard</strong><br/>Light-theme analytics dashboard mockup with KPI tiles and two illustrative charts. | 1920x1088 | layout |
| <strong>business_linkedin_carousel</strong><br/>LinkedIn "by the numbers" carousel cover slide with bold dark-mode typography. | 1152x1440 | text_fidelity_dense |
| <strong>business_pitch_slide</strong><br/>Single-slide pitch deck cover with hero tagline and three headline metrics. | 1920x1088 | text_fidelity_dense |
| <strong>business_swot_card</strong><br/>Four-quadrant SWOT analysis card for executive briefings and quarterly reviews. | 1536x1024 | text_fidelity_dense |

[**View all business →**](docs/gallery/business.md)

</td>
<td width="33%" valign="top">

### ecommerce · 3

| template | size | grader |
|---|---|---|
| <strong>ecommerce_category_banner</strong><br/>Wide 16:9 storefront category banner with a row of product silhouettes, headline, sub-text, and CTA. | 1920x1088 | text_fidelity_dense |
| <strong>ecommerce_marketplace_card</strong><br/>Compact 1:1 marketplace tile — product, price, and a single trust badge — built for grid views. | 1024x1024 | layout |
| <strong>ecommerce_product_hero</strong><br/>Single-SKU hero card for a product detail page — large product silhouette, price tag, primary CTA. | 1024x1280 | layout |

[**View all ecommerce →**](docs/gallery/ecommerce.md)

</td>
</tr>
<tr>
<td width="33%" valign="top">

### fashion · 3

| template | size | grader |
|---|---|---|
| <strong>fashion_flatlay_board</strong><br/>Styled flatlay of garments and accessories arranged on a surface for editorial use. | 1024x1024 | layout |
| <strong>fashion_lookbook_page</strong><br/>Editorial lookbook page — single-look hero shot with brand caption and item credits. | 1024x1280 | text_fidelity_dense |
| <strong>fashion_runway_poster</strong><br/>Vertical runway / show poster — brutalist editorial fashion-week announcement. | 1088x1920 | text_fidelity_dense |

[**View all fashion →**](docs/gallery/fashion.md)

</td>
<td width="33%" valign="top">

### food · 3

| template | size | grader |
|---|---|---|
| <strong>food_menu_poster</strong><br/>Vertical restaurant menu wall poster — categorized dish list with prices and accent. | 1088x1920 | text_fidelity_dense |
| <strong>food_packaging_label</strong><br/>Packaged-goods label mock — branded coffee bag, bottle, or jar wrapper design. | 1152x1536 | text_fidelity_dense |
| <strong>food_recipe_card</strong><br/>Single-recipe card — image hero with recipe meta and key-ingredient callout. | 1024x1280 | text_fidelity_dense |

[**View all food →**](docs/gallery/food.md)

</td>
<td width="33%" valign="top">

### gaming · 3

| template | size | grader |
|---|---|---|
| <strong>gaming_hud_mockup</strong><br/>Fictional video-game HUD mockup with health and mana bars, minimap, mission objective overlay. | 1920x1088 | text_fidelity_dense |
| <strong>gaming_item_card</strong><br/>Vertical 3:4 collectible RPG/CCG-style item card with name, rarity ribbon, stat lines, and lore blurb. | 1152x1536 | text_fidelity_dense |
| <strong>gaming_map_panel</strong><br/>16:9 fantasy world-map / quest-map panel with three labeled regions and a parchment border. | 1920x1088 | layout |

[**View all gaming →**](docs/gallery/gaming.md)

</td>
</tr>
<tr>
<td width="33%" valign="top">

### industrial · 3

| template | size | grader |
|---|---|---|
| <strong>industrial_cutaway_view</strong><br/>Isometric cutaway / exploded view of an industrial machine with four labeled internal components. | 1536x1024 | text_fidelity_dense |
| <strong>industrial_process_diagram</strong><br/>Wide 16:9 industrial process-flow diagram with four labeled stages and connecting arrows. | 1920x1088 | text_fidelity_dense |
| <strong>industrial_safety_poster</strong><br/>Vertical 9:16 factory-floor safety / hazard / PPE notice for posting at line entry points. | 1088x1920 | text_fidelity_dense |

[**View all industrial →**](docs/gallery/industrial.md)

</td>
<td width="33%" valign="top">

### interior · 3

| template | size | grader |
|---|---|---|
| <strong>interior_before_after</strong><br/>Split-screen interior before/after edit; left panel preserves the original, right panel shows the renovation. | 1920x1088 | edit_locality |
| <strong>interior_material_board</strong><br/>Square material / finish / color board (4-6 swatches with named labels) for an interior project. | 1024x1024 | layout |
| <strong>interior_room_mockup</strong><br/>Photoreal single-room interior mockup (bedroom / living / kitchen) with one labelled accent zone. | 1536x1024 | text_fidelity_sparse |

[**View all interior →**](docs/gallery/interior.md)

</td>
<td width="33%" valign="top">

### photography · 3

| template | size | grader |
|---|---|---|
| <strong>photography_cinematic_still</strong><br/>Film-frame still — anamorphic cinematic look capturing a single narrative beat. | 1920x1088 | text_fidelity_sparse |
| <strong>photography_documentary_scene</strong><br/>Documentary photojournalism — natural, candid scene grounded in real-world observation. | 1536x1024 | text_fidelity_sparse |
| <strong>photography_editorial_portrait</strong><br/>Magazine-style editorial portrait — single subject, deliberate light and lens choice. | 1024x1280 | text_fidelity_sparse |

[**View all photography →**](docs/gallery/photography.md)

</td>
</tr>
<tr>
<td width="33%" valign="top">

### product · 3

| template | size | grader |
|---|---|---|
| <strong>product_comparison_board</strong><br/>Vertical 4:5 side-by-side comparison of three product variants with feature checkboxes by axis. | 1024x1280 | text_fidelity_dense |
| <strong>product_feature_callout</strong><br/>Hero shot of one product with three feature callouts arranged around it on a horizontal canvas. | 1920x1088 | layout |
| <strong>product_packaging_concept</strong><br/>Single-product packaging concept rendering — branded box / bottle / pouch on a minimal studio backdrop. | 1024x1024 | text_fidelity_dense |

[**View all product →**](docs/gallery/product.md)

</td>
<td width="33%" valign="top">

### social_media · 3

| template | size | grader |
|---|---|---|
| <strong>social_media_launch_post</strong><br/>1:1 feed-friendly Instagram or X launch announcement post for a new product, with date and CTA. | 1024x1024 | text_fidelity_dense |
| <strong>social_media_story_sequence</strong><br/>9:16 vertical Instagram-Story-style 3-frame mini-narrative grid stitched into one image. | 1088x1920 | continuity |
| <strong>social_media_thumbnail_grid</strong><br/>1:1 YouTube-style 3-up thumbnail grid for previewing alternate channel-cover thumbnail concepts. | 1024x1024 | layout |

[**View all social_media →**](docs/gallery/social_media.md)

</td>
<td width="33%" valign="top">

### travel · 3

| template | size | grader |
|---|---|---|
| <strong>travel_destination_poster</strong><br/>Vintage-style travel poster for a fictional or generic destination, with name, tagline, and year. | 1024x1536 | text_fidelity_dense |
| <strong>travel_itinerary_card</strong><br/>Single-page vertical itinerary card with day-by-day items for a short trip. | 1088x1920 | text_fidelity_dense |
| <strong>travel_map_guide</strong><br/>Illustrated tourist map with three numbered points of interest across a generic region. | 1920x1088 | layout |

[**View all travel →**](docs/gallery/travel.md)

</td>
</tr>
<tr>
<td width="33%" valign="top">

### uiux · 4

| template | size | grader |
|---|---|---|
| <strong>uiux_design_system_card</strong><br/>Square design-system showcase card highlighting a single component or token with prop rows. | 1024x1024 | text_fidelity_dense |
| <strong>uiux_ios_app_mockup</strong><br/>Hyper-realistic iPhone app screenshot mockup with native iOS chrome and a card-based content feed. | 1088x1920 | text_fidelity_dense |
| <strong>uiux_social_cover_xhs</strong><br/>中文小红书风格教程封面 / Chinese-language Xiaohongshu cover for tutorial or lifestyle topic. | 1152x1536 | text_fidelity_dense |
| <strong>uiux_web_dashboard</strong><br/>Clean B2B SaaS analytics dashboard mockup with sidebar nav, KPI grid, and a primary chart. | 1920x1088 | text_fidelity_dense |

[**View all uiux →**](docs/gallery/uiux.md)

</td>
<td width="33%" valign="top"></td>
<td width="33%" valign="top"></td>
</tr>
</table>

<details>
<summary><strong>Compose your own (CLI / Skill / web ChatGPT)</strong></summary>

```bash
# Compose a prompt locally and paste into web ChatGPT (no API key needed)
i2w template render <id> --lang en --vars <vars.yml> --out prompt.md
cat prompt.md  # ready to paste

# Render directly through the API (requires OPENAI_API_KEY)
i2w render generate --prompt-file prompt.md --size 1024x1024 --quality medium
```

</details>

<!-- END GALLERY -->

---

## Showcase

> Sample renders by template domain, produced with gpt-image-2 against the spec-first templates in this repo. Image slots are reserved; renders land in [`docs/assets/`](docs/assets/) as the workbench iterates.

<table>
<tr>
<td width="33%" align="center">
  <img src="docs/assets/showcase-business.webp" alt="business showcase" width="100%" /><br/>
  <strong>business</strong><br/>
  <sub>SWOT, dashboards, pitch slides</sub>
</td>
<td width="33%" align="center">
  <img src="docs/assets/showcase-academic.webp" alt="academic showcase" width="100%" /><br/>
  <strong>academic</strong><br/>
  <sub>posters, diagrams, chalkboard proofs</sub>
</td>
<td width="33%" align="center">
  <img src="docs/assets/showcase-uiux.webp" alt="uiux showcase" width="100%" /><br/>
  <strong>uiux</strong><br/>
  <sub>iOS mockups, web dashboards, design tokens</sub>
</td>
</tr>
<tr>
<td width="33%" align="center">
  <img src="docs/assets/showcase-anime.webp" alt="anime showcase" width="100%" /><br/>
  <strong>anime</strong><br/>
  <sub>character sheets, comic panels, posters</sub>
</td>
<td width="33%" align="center">
  <img src="docs/assets/showcase-ecommerce.webp" alt="ecommerce showcase" width="100%" /><br/>
  <strong>ecommerce</strong><br/>
  <sub>product hero, listing tile, lifestyle</sub>
</td>
<td width="33%" align="center">
  <img src="docs/assets/showcase-industrial.webp" alt="industrial showcase" width="100%" /><br/>
  <strong>industrial</strong><br/>
  <sub>machine drawings, exploded views, schematics</sub>
</td>
</tr>
<tr>
<td width="33%" align="center">
  <img src="docs/assets/showcase-advertising.webp" alt="advertising showcase" width="100%" /><br/>
  <strong>advertising</strong><br/>
  <sub>banners, OOH, campaign keys</sub>
</td>
<td width="33%" align="center">
  <img src="docs/assets/showcase-gaming.webp" alt="gaming showcase" width="100%" /><br/>
  <strong>gaming</strong><br/>
  <sub>splash art, item cards, UI</sub>
</td>
<td width="33%" align="center">
  <img src="docs/assets/showcase-photography.webp" alt="photography showcase" width="100%" /><br/>
  <strong>photography</strong><br/>
  <sub>editorial, lookbook, still life</sub>
</td>
</tr>
<tr>
<td width="33%" align="center">
  <img src="docs/assets/showcase-fashion.webp" alt="fashion showcase" width="100%" /><br/>
  <strong>fashion</strong><br/>
  <sub>flat lays, runway, mood boards</sub>
</td>
<td width="33%" align="center">
  <img src="docs/assets/showcase-architecture.webp" alt="architecture showcase" width="100%" /><br/>
  <strong>architecture</strong><br/>
  <sub>exteriors, sections, axonometrics</sub>
</td>
<td width="33%" align="center">
  <img src="docs/assets/showcase-food.webp" alt="food showcase" width="100%" /><br/>
  <strong>food</strong><br/>
  <sub>menu hero, recipe stills, table scenes</sub>
</td>
</tr>
</table>

<sub>Slots intentionally show alt-text only on first commit; renders are generated lazily by codex against the matching templates.</sub>

---

## Capabilities

<p align="center">
  <img src="docs/assets/production-controls.svg" alt="production controls capability matrix" width="100%" />
</p>

<table>
<tr>
  <th align="left">Feature</th>
  <th align="left">Status</th>
  <th align="left">Command</th>
</tr>
<tr><td>Spec-first DSL (seven sections)</td><td>shipped</td><td><code>i2w template render</code></td></tr>
<tr><td>Bilingual EN + 中文</td><td>shipped</td><td><code>--lang en | zh-CN</code></td></tr>
<tr><td>Cost predictability (official + heuristic)</td><td>shipped</td><td><code>i2w cost compare</code></td></tr>
<tr><td>Pre-API validation</td><td>shipped</td><td><code>i2w preflight</code></td></tr>
<tr><td>Capability probe</td><td>shipped</td><td><code>i2w doctor capabilities</code></td></tr>
<tr><td>Batch API (50% discount)</td><td>shipped</td><td><code>i2w batch sweep --route batch-api</code></td></tr>
<tr><td>Run ledger (JSONL)</td><td>shipped</td><td><code>i2w ledger query</code></td></tr>
<tr><td>Snapshot-drift report</td><td>shipped</td><td><code>i2w ledger drift</code></td></tr>
<tr><td>Skill bundle (7 runtimes)</td><td>shipped</td><td>see <a href="./skills/gpt-image/">skills/gpt-image/</a></td></tr>
<tr><td>OCR-based eval</td><td>V0.4</td><td><code>i2w eval run</code> (prompt-only today)</td></tr>
<tr><td>Multi-model fallback</td><td>V0.4</td><td>&mdash;</td></tr>
<tr><td>PyPI / wheel packaging</td><td>V0.4</td><td>&mdash;</td></tr>
</table>

---

## Workflow

<p align="center">
  <img src="docs/assets/workflow.svg" alt="image2-workbench workflow" width="100%" />
</p>

```
 spec.yml  ──►  i2w template render  ──►  prompt.md  ──►  Images API  ──►  image.png
                                                            │
                                                            └──►  i2w ledger entry
```

Three stages, one source of truth. The same `spec.yml` produces a paste-ready markdown prompt for web ChatGPT, drives the Images API for one-shot renders, and feeds Batch API JSONL for cost-efficient sweeps &mdash; without ever copy-editing the prompt by hand.

---

## CLI surface

<table>
<tr>
  <th align="left">Command</th>
  <th align="left">Purpose</th>
</tr>
<tr><td><code>i2w catalog</code></td><td>Browse and search the template / corpus catalog.</td></tr>
<tr><td><code>i2w template</code></td><td>List templates and compile YAML specs into bilingual prompts.</td></tr>
<tr><td><code>i2w render</code></td><td>Generate or edit images with local validation and sidecars.</td></tr>
<tr><td><code>i2w batch</code></td><td>Build safe sweeps and Batch API jobs with dry-run previews.</td></tr>
<tr><td><code>i2w eval</code></td><td>Run prompt-level rubric checks (OCR-eval coming in V0.4).</td></tr>
<tr><td><code>i2w cost</code></td><td>Estimate, compare, and budget Images API spend.</td></tr>
<tr><td><code>i2w doctor</code></td><td>Probe runtime parameter compatibility per account / org / model.</td></tr>
<tr><td><code>i2w preflight</code></td><td>Reject known-bad requests locally, before any API call.</td></tr>
<tr><td><code>i2w ledger</code></td><td>Query success rate, latency, cost, error distribution, snapshot drift.</td></tr>
<tr><td><code>i2w gallery</code></td><td>Build paste-ready markdown galleries from templates.</td></tr>
<tr><td><code>i2w version</code></td><td>Print the installed workbench version.</td></tr>
</table>

---

## Skill ecosystem

`image2-workbench` ships a portable Skill bundle in [`skills/gpt-image/`](skills/gpt-image/). Drop it into any agent runtime that loads `SKILL.md`-style manifests.

<table>
<tr>
  <th align="left">Runtime</th>
  <th align="left">Status</th>
  <th align="left">Manifest</th>
</tr>
<tr><td>Claude Code</td><td>tested</td><td><a href="./skills/gpt-image/manifests/claude.json"><code>claude.json</code></a></td></tr>
<tr><td>Anthropic Skills</td><td>tested</td><td><a href="./skills/gpt-image/manifests/claude.json"><code>claude.json</code></a></td></tr>
<tr><td>OpenAI Codex</td><td>tested</td><td><a href="./skills/gpt-image/manifests/codex.yml"><code>codex.yml</code></a></td></tr>
<tr><td>LangChain</td><td>shim ready</td><td><a href="./skills/gpt-image/manifests/langchain.py"><code>langchain.py</code></a></td></tr>
<tr><td>smolagents</td><td>shim ready</td><td><a href="./skills/gpt-image/manifests/smolagents.py"><code>smolagents.py</code></a></td></tr>
<tr><td>OpenClaw</td><td>theoretical</td><td><a href="./skills/gpt-image/manifests/openclaw.json"><code>openclaw.json</code></a></td></tr>
<tr><td>Hermes</td><td>theoretical</td><td><a href="./skills/gpt-image/manifests/hermes.yml"><code>hermes.yml</code></a></td></tr>
</table>

[Full skill compatibility matrix &rarr;](docs/skill-compatibility.md)

---

## FAQ

<details>
<summary><strong>How is this different from a curated prompt list?</strong></summary>

Prompt lists are markdown. This is a compiler. Templates are pydantic-validated YAML; outputs are auditable; the same template renders bilingual prompts <em>and</em> directly drives the API. See [`docs/positioning.md`](docs/positioning.md) for the long-form argument.

</details>

<details>
<summary><strong>Do I need an OpenAI API key?</strong></summary>

Not for the L3 path. `i2w template render` produces paste-ready markdown for web ChatGPT (no API key required). The L2 path (`i2w render generate`) needs `OPENAI_API_KEY` and a verified org. `doctor capabilities`, `cost`, `preflight`, `template`, `gallery`, and `catalog` all run offline.

</details>

<details>
<summary><strong>Why 16 domains and not "everything"?</strong></summary>

Each domain ships with a `DOMAIN_CARD.md` (FOR / NOT FOR / Key axes) so neighbouring domains stay distinct. We add a domain only when we can name 3 axes that no existing domain covers. Twelve cards live today; the remaining four ship as we publish more cross-cut workflows.

</details>

<details>
<summary><strong>Will it work in 中文?</strong></summary>

Yes. All 52 templates render bilingual; demo vars include CJK content where it makes sense. The compiler is language-aware (CJK punctuation, line-breaks, glyph density), not a string find-and-replace. Read the Chinese guide at [`README.zh.md`](README.zh.md) and [`docs/getting-started.zh.md`](docs/getting-started.zh.md).

</details>

<details>
<summary><strong>What about safety and moderation?</strong></summary>

`i2w preflight` runs local validation (size, background, quality, unsupported params) and an optional Moderation API pass before billing. `MODERATION_BLOCKED` is its own exit code (5) so CI can branch on it. We do not default `moderation: low`; opt in explicitly when you need it.

</details>

<details>
<summary><strong>Why three pillars (cost / preflight / ledger)?</strong></summary>

A workbench has to answer three questions a prompt list can't: <em>"how much will this cost?"</em>, <em>"will this even work before I pay?"</em>, and <em>"what happened across my last 1,000 runs?"</em>. Each pillar maps to one CLI command surface, one exit-code class, and one section of the JSONL ledger.

</details>

<details>
<summary><strong>How is content licensed?</strong></summary>

Code is Apache-2.0. Templates, docs, README files, and the Skill `SKILL.md` are CC BY 4.0. Corpus records are per-source (see [`source_registry.yml`](corpus/manifests/source_registry.yml)). See the [licensing](#licensing) section below.

</details>

---

## Project structure

```
image2-workbench/
├── src/image2_workbench/    # CLI + runtime + compiler + ledger + ...
├── templates/<domain>/       # 52 spec yaml + demo vars + DOMAIN_CARDs
├── skills/gpt-image/         # SKILL.md + 7 runtime manifests
├── docs/                     # gallery, positioning, cost-modeling, ...
├── corpus/                   # provenance-first prompt records
└── tests/                    # 420+ unit + smoke tests
```

[Repository conventions (`AGENTS.md`) &rarr;](AGENTS.md)

---

## Licensing

<table>
<tr>
  <th align="left">Path</th>
  <th align="left">License</th>
</tr>
<tr><td><code>src/</code>, <code>tests/</code>, <code>scripts/</code>, <code>.github/</code></td><td>Apache-2.0 (<a href="./LICENSE">LICENSE</a>)</td></tr>
<tr><td><code>templates/</code>, <code>docs/</code>, <code>README*</code>, <code>skills/gpt-image/SKILL.md</code></td><td>CC BY 4.0 (<a href="./LICENSE-CONTENT">LICENSE-CONTENT</a>)</td></tr>
<tr><td><code>corpus/normalized/*.jsonl</code></td><td>per-record (see <a href="./corpus/manifests/source_registry.yml"><code>source_registry.yml</code></a>)</td></tr>
</table>

Attributions and methodology in [`NOTICE`](NOTICE).

---

## Contributing

Read [`AGENTS.md`](AGENTS.md) &mdash; file ownership, anti-patterns (no `transparent` background by default, no `input_fidelity`, no `moderation: low` defaults), V1 definition-of-done.

Security disclosures &rarr; [`SECURITY.md`](SECURITY.md).

---

<p align="center">
  <a href="./README.zh.md"><strong>中文版 README &rarr;</strong></a>
</p>
