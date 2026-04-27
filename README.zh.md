<!-- SPDX-License-Identifier: CC-BY-4.0 -->

<p align="center">
  <a href="./README.md">English</a> &nbsp;&middot;&nbsp; <a href="./README.zh.md">中文</a>
</p>

<h1 align="center">image2-workbench</h1>

<p align="center"><strong>面向 OpenAI gpt-image-2 的规格先行（spec-first）生产工作台。</strong><br/>52 个可执行模板 &middot; 16 个领域 &middot; 双语 prompt &middot; 成本 / 预检 / 批量 / 审计四大控制面。</p>

<p align="center">
  <img src="docs/assets/hero.svg" alt="image2-workbench atlas hero" width="900" />
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white">
  <img alt="License code" src="https://img.shields.io/badge/code-Apache--2.0-blue">
  <img alt="License content" src="https://img.shields.io/badge/templates%2Fdocs-CC%20BY%204.0-lightgrey">
  <img alt="Domains" src="https://img.shields.io/badge/domains-30-1f6feb">
  <img alt="Templates" src="https://img.shields.io/badge/templates-80-238636">
  <img alt="Cards" src="https://img.shields.io/badge/%E9%A2%86%E5%9F%9F%E5%8D%A1-12-0d9488">
  <img alt="CLI" src="https://img.shields.io/badge/CLI-i2w%20%C2%B7%2011%20%E5%91%BD%E4%BB%A4-334155">
  <img alt="Skill" src="https://img.shields.io/badge/Skill-7%20%E8%BF%90%E8%A1%8C%E6%97%B6-7c3aed">
  <img alt="Bilingual" src="https://img.shields.io/badge/%E5%8F%8C%E8%AF%AD-EN%20%2B%20%E4%B8%AD%E6%96%87-d97706">
  <img alt="Tests" src="https://img.shields.io/badge/%E6%B5%8B%E8%AF%95-420%20%E9%80%9A%E8%BF%87-15803d">
  <img alt="Status" src="https://img.shields.io/badge/%E7%8A%B6%E6%80%81-v0.3%20alpha-ea580c">
</p>

<p align="center">
  <a href="#atlas--16-个领域52-个模板"><strong>浏览 Atlas &rarr;</strong></a>
  &nbsp;&middot;&nbsp;
  <a href="#快速开始"><strong>快速开始 &rarr;</strong></a>
  &nbsp;&middot;&nbsp;
  <a href="#样图"><strong>样图 &rarr;</strong></a>
  &nbsp;&middot;&nbsp;
  <a href="./skills/gpt-image/"><strong>查看 Skills &rarr;</strong></a>
  &nbsp;&middot;&nbsp;
  <a href="#常见问题"><strong>FAQ &rarr;</strong></a>
</p>

---

## 目录

- [为什么需要工作台？](#为什么需要工作台)
- [快速开始](#快速开始)
- [Atlas — 16 个领域，52 个模板](#atlas--16-个领域52-个模板)
- [样图](#样图)
- [能力清单](#能力清单)
- [工作流](#工作流)
- [CLI 命令面](#cli-命令面)
- [Skill 生态](#skill-生态)
- [常见问题](#常见问题)
- [仓库结构](#仓库结构)
- [许可](#许可)
- [贡献](#贡献)

---

## 为什么需要工作台？

Prompt 清单适合启发灵感。一旦你需要做这些事，它就开始吃力：

- **可复现的输出**：覆盖不同模板、尺寸、成本、模型快照。
- **双语交付**（EN + 中文）：同一份 spec，不允许翻译漂移。
- **API 调用前校验**：花钱前先把坏请求拦下来。
- **审计轨迹**：六个月后模型快照换了，依然能回答“当时发生了什么”。

这个仓库把 prompt pack 改造成可审计、可执行、可批量的工作流，围绕三个支柱：

<table>
<tr>
  <th align="left" width="22%">支柱</th>
  <th align="left" width="48%">解决的问题</th>
  <th align="left" width="30%">CLI 入口</th>
</tr>
<tr>
  <td><strong>成本可预测</strong></td>
  <td>双轨成本：官方 <code>(size, quality)</code> 价目表 + 像素面积启发式 + Batch API 五折。</td>
  <td><code>i2w cost compare</code><br/><code>i2w cost estimate</code><br/><code>i2w cost budget</code><br/><code>i2w batch sweep</code></td>
</tr>
<tr>
  <td><strong>错误分级</strong></td>
  <td>七个退出码（<code>OK</code>、<code>AUTH</code>、<code>RATE_LIMIT</code>、<code>MODERATION_BLOCKED</code>、<code>VALIDATION</code>、<code>API_OTHER</code>、<code>INTERNAL</code>），加本地校验和 pre-moderation。</td>
  <td><code>i2w preflight</code><br/><code>i2w doctor capabilities</code></td>
</tr>
<tr>
  <td><strong>可观测性</strong></td>
  <td>追加式 JSONL ledger：成功率、p50 / p95 时延、单价、快照漂移。</td>
  <td><code>i2w ledger query</code><br/><code>i2w ledger top-failures</code><br/><code>i2w ledger drift</code><br/><code>i2w ledger export</code></td>
</tr>
</table>

[完整定位说明 &rarr;](docs/positioning.md)

---

## 快速开始

<details open>
<summary><strong>安装（约 30 秒）</strong></summary>

```bash
# fork 后或直接 clone：
git clone https://github.com/StartripAI/gpt-image-2.0-workbench.git
cd gpt-image-2.0-workbench

python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

i2w --help                  # 11 个命令
i2w doctor capabilities     # 探测参数兼容性（无需 API key）
pytest -q                   # 工作台自检（420+ 通过）
```

</details>

<details>
<summary><strong>渲染第一个 prompt（无需 API key）</strong></summary>

```bash
i2w template render business_swot_card --lang zh-CN \
  --vars templates/business/_vars_examples/swot_acme.yml \
  --out out/swot.zh.md
cat out/swot.zh.md   # 直接粘贴进网页 ChatGPT
```

把 markdown 粘贴到 ChatGPT 的图像对话框，下载图片即可。这是 L3 路径——只走网页，不花钱，不用 API key。

</details>

<details>
<summary><strong>走 API 渲染（需要 <code>OPENAI_API_KEY</code>）</strong></summary>

```bash
export OPENAI_API_KEY=sk-...

# 调用前先在本地拦下坏请求：
i2w preflight out/swot.zh.md --template-id business_swot_card

# 在(尺寸, 质量)矩阵上比成本，不下单：
i2w cost compare --size 1024x1024,1536x1024 --quality low,medium,high

# 渲染并写一行 ledger：
i2w render generate --prompt-file out/swot.zh.md \
  --template-id business_swot_card \
  --size 1536x1024 --quality medium --out out/swot.png

# 回看刚才发生了什么：
i2w ledger query --template business_swot_card
```

</details>

<details>
<summary><strong>跑 Batch API 批量任务（5 折）</strong></summary>

```bash
i2w batch sweep \
  --template business_swot_card \
  --vars templates/business/_vars_examples/swot_acme.yml \
  --route batch-api \
  --dry-run                                # 预览 JSONL，不花钱

i2w batch sweep ... --route batch-api      # 确认后再正式提交
```

</details>

[详细教程 &rarr;](docs/getting-started.zh.md) &nbsp;&middot;&nbsp; [成本建模 &rarr;](docs/cost-modeling.md) &nbsp;&middot;&nbsp; [错误码 &rarr;](docs/error-codes.md)

---

<!-- BEGIN GALLERY (auto-generated by `i2w gallery readme`; do not edit by hand) -->

## 模板图册 — 30 个领域，80 个模板

<table>
<tr>
<td width="33%" valign="top">

### academic · 4 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>academic_chalkboard_proof</strong><br/>Photorealistic university chalkboard with a four-step mathematical proof and QED line. | 1920x1088 | text_fidelity_dense |
| <strong>academic_journal_poster</strong><br/>Vertical 3-column conference poster with intro, methods, results, conclusion. | 1088x1920 | text_fidelity_dense |
| <strong>academic_multilingual_eduposter</strong><br/>Multilingual education infographic. Designed for Korean / Japanese / Chinese / Arabic / Hindi educational posters; the image's text is in language_native_name, NOT the prompt language. | 1920x1088 | text_fidelity_dense |
| <strong>academic_scientific_diagram</strong><br/>Museum-style cross-section or labeled scientific illustration with five callouts. | 1536x1024 | text_fidelity_dense |

[**查看 academic 全部 →**](docs/gallery/academic.md)

</td>
<td width="33%" valign="top">

### advertising · 3 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>advertising_billboard_mockup</strong><br/>Photoreal urban billboard mockup with the hero ad pasted on a real-feeling outdoor placement. | 1920x1088 | layout |
| <strong>advertising_campaign_key_visual</strong><br/>Premium production-grade brand campaign hero key-visual with tagline, product name, and call-to-action. | 1920x1088 | text_fidelity_dense |
| <strong>advertising_storyboard_3frame</strong><br/>Three-panel storyboard sketch for a 30-second commercial, with brand seal beneath the panels. | 1536x1024 | continuity |

[**查看 advertising 全部 →**](docs/gallery/advertising.md)

</td>
<td width="33%" valign="top">

### anime · 4 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>anime_ccd_candid</strong><br/>复古 CCD 相机风格自拍 / Vintage CCD camera-style candid (a non-photoreal staged "authenticity"). | 1088x1920 | text_fidelity_sparse |
| <strong>anime_character_sheet</strong><br/>Concept-art character reference sheet with three-view turnaround, expression sheet, and prop detail. | 1920x1088 | continuity |
| <strong>anime_city_poster</strong><br/>双语城市旅行海报 / Bilingual editorial city travel poster mixing calligraphic skyline and premium typography. | 1088x1920 | text_fidelity_dense |
| <strong>anime_comic_8panel</strong><br/>Eight-panel sequential manga page rendered in black-and-white seinen ink with strict character continuity. | 1024x1536 | continuity |

[**查看 anime 全部 →**](docs/gallery/anime.md)

</td>
</tr>
<tr>
<td width="33%" valign="top">

### architecture · 3 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>architecture_facade_concept</strong><br/>Conceptual exterior facade rendering for an architecture studio's project poster. | 1536x1024 | text_fidelity_dense |
| <strong>architecture_presentation_board</strong><br/>Multi-panel architecture presentation board combining concept, diagram, render, and short text. | 1920x1088 | layout |
| <strong>architecture_site_diagram</strong><br/>Site plan / urban-context diagram with three labeled zones, drawn in plan view. | 1920x1088 | text_fidelity_dense |

[**查看 architecture 全部 →**](docs/gallery/architecture.md)

</td>
<td width="33%" valign="top">

### automotive · 2 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>automotive_dealership_poster</strong><br/>Point-of-sale dealership poster — vehicle hero plus price, financing terms, and dealer name. | 1024x1280 | text_fidelity_dense |
| <strong>automotive_hero_ad</strong><br/>Cinematic single-vehicle hero ad — fictional car, motorcycle, or EV on a deliberate backdrop. | 1920x1088 | text_fidelity_sparse |

[**查看 automotive 全部 →**](docs/gallery/automotive.md)

</td>
<td width="33%" valign="top">

### beauty · 2 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>beauty_editorial_layout</strong><br/>Magazine-style beauty editorial spread — close-up beauty shot with small product callouts. | 1024x1280 | text_fidelity_sparse |
| <strong>beauty_skincare_packaging</strong><br/>Single skincare unit on minimal staging — bottle / jar / dropper as design hero. | 1024x1024 | text_fidelity_dense |

[**查看 beauty 全部 →**](docs/gallery/beauty.md)

</td>
</tr>
<tr>
<td width="33%" valign="top">

### business · 4 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>business_data_dashboard</strong><br/>Light-theme analytics dashboard mockup with KPI tiles and two illustrative charts. | 1920x1088 | layout |
| <strong>business_linkedin_carousel</strong><br/>LinkedIn "by the numbers" carousel cover slide with bold dark-mode typography. | 1152x1440 | text_fidelity_dense |
| <strong>business_pitch_slide</strong><br/>Single-slide pitch deck cover with hero tagline and three headline metrics. | 1920x1088 | text_fidelity_dense |
| <strong>business_swot_card</strong><br/>Four-quadrant SWOT analysis card for executive briefings and quarterly reviews. | 1536x1024 | text_fidelity_dense |

[**查看 business 全部 →**](docs/gallery/business.md)

</td>
<td width="33%" valign="top">

### comic_book · 2 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>comic_book_panel_page</strong><br/>Multi-panel American comic-book interior page with speech balloons, halftone shading, and short panel captions. | 1024x1536 | continuity |
| <strong>comic_book_variant_cover</strong><br/>Single-figure American comic-book variant cover with masthead, issue number, and credit slug, in bold inks and halftone. | 1024x1536 | text_fidelity_dense |

[**查看 comic_book 全部 →**](docs/gallery/comic_book.md)

</td>
<td width="33%" valign="top">

### ecommerce · 3 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>ecommerce_category_banner</strong><br/>Wide 16:9 storefront category banner with a row of product silhouettes, headline, sub-text, and CTA. | 1920x1088 | text_fidelity_dense |
| <strong>ecommerce_marketplace_card</strong><br/>Compact 1:1 marketplace tile — product, price, and a single trust badge — built for grid views. | 1024x1024 | layout |
| <strong>ecommerce_product_hero</strong><br/>Single-SKU hero card for a product detail page — large product silhouette, price tag, primary CTA. | 1024x1280 | layout |

[**查看 ecommerce 全部 →**](docs/gallery/ecommerce.md)

</td>
</tr>
<tr>
<td width="33%" valign="top">

### events · 2 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>events_concert_poster</strong><br/>Vertical concert / festival poster with headliner, support, date, and venue. | 1088x1920 | text_fidelity_dense |
| <strong>events_wedding_invite</strong><br/>Wedding invitation card — formal vertical layout with names, date, venue, and RSVP. | 1024x1280 | text_fidelity_dense |

[**查看 events 全部 →**](docs/gallery/events.md)

</td>
<td width="33%" valign="top">

### fashion · 3 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>fashion_flatlay_board</strong><br/>Styled flatlay of garments and accessories arranged on a surface for editorial use. | 1024x1024 | layout |
| <strong>fashion_lookbook_page</strong><br/>Editorial lookbook page — single-look hero shot with brand caption and item credits. | 1024x1280 | text_fidelity_dense |
| <strong>fashion_runway_poster</strong><br/>Vertical runway / show poster — brutalist editorial fashion-week announcement. | 1088x1920 | text_fidelity_dense |

[**查看 fashion 全部 →**](docs/gallery/fashion.md)

</td>
<td width="33%" valign="top">

### food · 3 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>food_menu_poster</strong><br/>Vertical restaurant menu wall poster — categorized dish list with prices and accent. | 1088x1920 | text_fidelity_dense |
| <strong>food_packaging_label</strong><br/>Packaged-goods label mock — branded coffee bag, bottle, or jar wrapper design. | 1152x1536 | text_fidelity_dense |
| <strong>food_recipe_card</strong><br/>Single-recipe card — image hero with recipe meta and key-ingredient callout. | 1024x1280 | text_fidelity_dense |

[**查看 food 全部 →**](docs/gallery/food.md)

</td>
</tr>
<tr>
<td width="33%" valign="top">

### gaming · 3 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>gaming_hud_mockup</strong><br/>Fictional video-game HUD mockup with health and mana bars, minimap, mission objective overlay. | 1920x1088 | text_fidelity_dense |
| <strong>gaming_item_card</strong><br/>Vertical 3:4 collectible RPG/CCG-style item card with name, rarity ribbon, stat lines, and lore blurb. | 1152x1536 | text_fidelity_dense |
| <strong>gaming_map_panel</strong><br/>16:9 fantasy world-map / quest-map panel with three labeled regions and a parchment border. | 1920x1088 | layout |

[**查看 gaming 全部 →**](docs/gallery/gaming.md)

</td>
<td width="33%" valign="top">

### industrial · 3 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>industrial_cutaway_view</strong><br/>Isometric cutaway / exploded view of an industrial machine with four labeled internal components. | 1536x1024 | text_fidelity_dense |
| <strong>industrial_process_diagram</strong><br/>Wide 16:9 industrial process-flow diagram with four labeled stages and connecting arrows. | 1920x1088 | text_fidelity_dense |
| <strong>industrial_safety_poster</strong><br/>Vertical 9:16 factory-floor safety / hazard / PPE notice for posting at line entry points. | 1088x1920 | text_fidelity_dense |

[**查看 industrial 全部 →**](docs/gallery/industrial.md)

</td>
<td width="33%" valign="top">

### infographic_data · 2 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>infographic_data_chart_explainer</strong><br/>Single-chart explainer panel — large hero chart annotated with three pull-out callouts and a source line. | 1024x1280 | text_fidelity_dense |
| <strong>infographic_data_dashboard</strong><br/>Editorial dataviz dashboard explainer with four chart panels, headline, and insight callouts. | 1920x1088 | text_fidelity_dense |

[**查看 infographic_data 全部 →**](docs/gallery/infographic_data.md)

</td>
</tr>
<tr>
<td width="33%" valign="top">

### interior · 3 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>interior_before_after</strong><br/>Split-screen interior before/after edit; left panel preserves the original, right panel shows the renovation. | 1920x1088 | edit_locality |
| <strong>interior_material_board</strong><br/>Square material / finish / color board (4-6 swatches with named labels) for an interior project. | 1024x1024 | layout |
| <strong>interior_room_mockup</strong><br/>Photoreal single-room interior mockup (bedroom / living / kitchen) with one labelled accent zone. | 1536x1024 | text_fidelity_sparse |

[**查看 interior 全部 →**](docs/gallery/interior.md)

</td>
<td width="33%" valign="top">

### isometric_illustration · 2 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>isometric_city_block</strong><br/>True-isometric city block with named buildings, tiny vehicles, and street trees, projected on a strict 30-30 grid. | 1024x1024 | layout |
| <strong>isometric_workspace_scene</strong><br/>Isometric workspace scene — desk, studio, and side station — in true 30-30 projection with labeled accessories. | 1920x1088 | layout |

[**查看 isometric_illustration 全部 →**](docs/gallery/isometric_illustration.md)

</td>
<td width="33%" valign="top">

### kids_illustration · 2 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>kids_illustration_storybook_spread</strong><br/>Two-page children's storybook spread with friendly cast, narration band, and a single dialogue line. | 1920x1088 | text_fidelity_dense |
| <strong>kids_illustration_workbook_page</strong><br/>Preschool workbook page — counting / matching / coloring activity with friendly characters and a clear instruction line. | 1024x1280 | text_fidelity_dense |

[**查看 kids_illustration 全部 →**](docs/gallery/kids_illustration.md)

</td>
</tr>
<tr>
<td width="33%" valign="top">

### music · 2 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>music_album_cover</strong><br/>Square album-cover artwork — single hero visual identity with artist and album metadata. | 1024x1024 | text_fidelity_dense |
| <strong>music_concert_poster</strong><br/>Vertical tour / concert poster — headliner identity with tour name, dates, and city run. | 1088x1920 | text_fidelity_dense |

[**查看 music 全部 →**](docs/gallery/music.md)

</td>
<td width="33%" valign="top">

### pet · 2 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>pet_adoption_flyer</strong><br/>Single-animal adoption flyer — companion-animal photo with name, age, key trait, and shelter contact. | 1024x1280 | text_fidelity_dense |
| <strong>pet_food_packaging</strong><br/>Pet-food bag or can label — branded packaging plate with feeding metadata. | 1152x1536 | text_fidelity_dense |

[**查看 pet 全部 →**](docs/gallery/pet.md)

</td>
<td width="33%" valign="top">

### photography · 3 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>photography_cinematic_still</strong><br/>Film-frame still — anamorphic cinematic look capturing a single narrative beat. | 1920x1088 | text_fidelity_sparse |
| <strong>photography_documentary_scene</strong><br/>Documentary photojournalism — natural, candid scene grounded in real-world observation. | 1536x1024 | text_fidelity_sparse |
| <strong>photography_editorial_portrait</strong><br/>Magazine-style editorial portrait — single subject, deliberate light and lens choice. | 1024x1280 | text_fidelity_sparse |

[**查看 photography 全部 →**](docs/gallery/photography.md)

</td>
</tr>
<tr>
<td width="33%" valign="top">

### product · 3 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>product_comparison_board</strong><br/>Vertical 4:5 side-by-side comparison of three product variants with feature checkboxes by axis. | 1024x1280 | text_fidelity_dense |
| <strong>product_feature_callout</strong><br/>Hero shot of one product with three feature callouts arranged around it on a horizontal canvas. | 1920x1088 | layout |
| <strong>product_packaging_concept</strong><br/>Single-product packaging concept rendering — branded box / bottle / pouch on a minimal studio backdrop. | 1024x1024 | text_fidelity_dense |

[**查看 product 全部 →**](docs/gallery/product.md)

</td>
<td width="33%" valign="top">

### science_fiction_concept · 2 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>science_fiction_concept_keyframe</strong><br/>Cinematic sci-fi keyframe matte painting — alien landscape or far-future urban scene with painterly atmosphere. | 1920x1088 | text_fidelity_sparse |
| <strong>science_fiction_concept_vehicle_hero</strong><br/>Hero side-view concept-art plate of a fictional sci-fi vehicle, mech, or spacecraft on a clean studio plate. | 1920x1088 | text_fidelity_sparse |

[**查看 science_fiction_concept 全部 →**](docs/gallery/science_fiction_concept.md)

</td>
<td width="33%" valign="top">

### social_media · 3 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>social_media_launch_post</strong><br/>1:1 feed-friendly Instagram or X launch announcement post for a new product, with date and CTA. | 1024x1024 | text_fidelity_dense |
| <strong>social_media_story_sequence</strong><br/>9:16 vertical Instagram-Story-style 3-frame mini-narrative grid stitched into one image. | 1088x1920 | continuity |
| <strong>social_media_thumbnail_grid</strong><br/>1:1 YouTube-style 3-up thumbnail grid for previewing alternate channel-cover thumbnail concepts. | 1024x1024 | layout |

[**查看 social_media 全部 →**](docs/gallery/social_media.md)

</td>
</tr>
<tr>
<td width="33%" valign="top">

### streetwear · 2 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>streetwear_lookbook_drop</strong><br/>Drop-announcement lookbook plate — single street look with drop date and collection name. | 1024x1280 | text_fidelity_dense |
| <strong>streetwear_sneaker_hero</strong><br/>Single sneaker hero shot — stage-lit isolation plate for a fictional drop colorway. | 1024x1024 | text_fidelity_sparse |

[**查看 streetwear 全部 →**](docs/gallery/streetwear.md)

</td>
<td width="33%" valign="top">

### tattoo · 2 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>tattoo_flash_sheet</strong><br/>Traditional tattoo flash sheet — multiple design vignettes on aged paper. | 1024x1280 | layout |
| <strong>tattoo_minimal_design</strong><br/>Single isolated minimalist tattoo design on stark white substrate. | 1024x1024 | text_fidelity_sparse |

[**查看 tattoo 全部 →**](docs/gallery/tattoo.md)

</td>
<td width="33%" valign="top">

### travel · 3 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>travel_destination_poster</strong><br/>Vintage-style travel poster for a fictional or generic destination, with name, tagline, and year. | 1024x1536 | text_fidelity_dense |
| <strong>travel_itinerary_card</strong><br/>Single-page vertical itinerary card with day-by-day items for a short trip. | 1088x1920 | text_fidelity_dense |
| <strong>travel_map_guide</strong><br/>Illustrated tourist map with three numbered points of interest across a generic region. | 1920x1088 | layout |

[**查看 travel 全部 →**](docs/gallery/travel.md)

</td>
</tr>
<tr>
<td width="33%" valign="top">

### typography · 2 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>typography_lettering_art</strong><br/>Hand-lettered art piece — a single phrase rendered as the visual subject. | 1024x1024 | text_fidelity_dense |
| <strong>typography_specimen_poster</strong><br/>Type specimen poster — display alphabet, glyph grid, and typeface metadata as the artwork. | 1024x1280 | text_fidelity_dense |

[**查看 typography 全部 →**](docs/gallery/typography.md)

</td>
<td width="33%" valign="top">

### uiux · 4 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>uiux_design_system_card</strong><br/>Square design-system showcase card highlighting a single component or token with prop rows. | 1024x1024 | text_fidelity_dense |
| <strong>uiux_ios_app_mockup</strong><br/>Hyper-realistic iPhone app screenshot mockup with native iOS chrome and a card-based content feed. | 1088x1920 | text_fidelity_dense |
| <strong>uiux_social_cover_xhs</strong><br/>中文小红书风格教程封面 / Chinese-language Xiaohongshu cover for tutorial or lifestyle topic. | 1152x1536 | text_fidelity_dense |
| <strong>uiux_web_dashboard</strong><br/>Clean B2B SaaS analytics dashboard mockup with sidebar nav, KPI grid, and a primary chart. | 1920x1088 | text_fidelity_dense |

[**查看 uiux 全部 →**](docs/gallery/uiux.md)

</td>
<td width="33%" valign="top">

### watercolor_illustration · 2 条

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>watercolor_botanical_study</strong><br/>Single-specimen botanical watercolor study with latin caption, in transparent washes on visibly textured paper. | 1024x1280 | text_fidelity_sparse |
| <strong>watercolor_character_portrait</strong><br/>Three-quarter character portrait painted in transparent watercolor washes with visible paper grain and a small footer caption. | 1024x1280 | text_fidelity_sparse |

[**查看 watercolor_illustration 全部 →**](docs/gallery/watercolor_illustration.md)

</td>
</tr>
</table>

<details>
<summary>**自己组装一条（CLI / Skill / 网页 ChatGPT）**</summary>

```bash
# 本地组装提示词，复制到网页 ChatGPT(无需 API key)
i2w template render <id> --lang zh-CN --vars <vars.yml> --out prompt.md
cat prompt.md  # 直接粘贴

# 通过 API 直接渲染(需要 OPENAI_API_KEY)
i2w render generate --prompt-file prompt.md --size 1024x1024 --quality medium
```

</details>

<!-- END GALLERY -->

---

## 样图

> 按模板域分类的示例渲染。30 张卡片 × 每域一张 —— 仓库里的规格优先模板驱动每张图。这些图位由 gpt-image-2 按 `HANDOFF_v0.3.5.md` 中的 prompt 渲染并 commit 到 `docs/assets/`。

<table>
<tr>
<td width="20%" align="center">
  <img src="docs/assets/showcase-business.webp" alt="business 样图" width="100%" /><br/>
  <strong>商业</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-academic.webp" alt="academic 样图" width="100%" /><br/>
  <strong>学术</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-uiux.webp" alt="uiux 样图" width="100%" /><br/>
  <strong>界面设计</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-anime.webp" alt="anime 样图" width="100%" /><br/>
  <strong>动漫</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-ecommerce.webp" alt="ecommerce 样图" width="100%" /><br/>
  <strong>电商</strong>
</td>
</tr>
<tr>
<td width="20%" align="center">
  <img src="docs/assets/showcase-industrial.webp" alt="industrial 样图" width="100%" /><br/>
  <strong>工业</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-product.webp" alt="product 样图" width="100%" /><br/>
  <strong>产品</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-advertising.webp" alt="advertising 样图" width="100%" /><br/>
  <strong>广告</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-social_media.webp" alt="social_media 样图" width="100%" /><br/>
  <strong>社交媒体</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-gaming.webp" alt="gaming 样图" width="100%" /><br/>
  <strong>游戏</strong>
</td>
</tr>
<tr>
<td width="20%" align="center">
  <img src="docs/assets/showcase-photography.webp" alt="photography 样图" width="100%" /><br/>
  <strong>摄影</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-fashion.webp" alt="fashion 样图" width="100%" /><br/>
  <strong>时尚</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-food.webp" alt="food 样图" width="100%" /><br/>
  <strong>食品</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-architecture.webp" alt="architecture 样图" width="100%" /><br/>
  <strong>建筑</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-interior.webp" alt="interior 样图" width="100%" /><br/>
  <strong>室内</strong>
</td>
</tr>
<tr>
<td width="20%" align="center">
  <img src="docs/assets/showcase-travel.webp" alt="travel 样图" width="100%" /><br/>
  <strong>旅行</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-typography.webp" alt="typography 样图" width="100%" /><br/>
  <strong>字体</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-beauty.webp" alt="beauty 样图" width="100%" /><br/>
  <strong>美妆</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-events.webp" alt="events 样图" width="100%" /><br/>
  <strong>活动</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-tattoo.webp" alt="tattoo 样图" width="100%" /><br/>
  <strong>纹身</strong>
</td>
</tr>
<tr>
<td width="20%" align="center">
  <img src="docs/assets/showcase-watercolor_illustration.webp" alt="watercolor_illustration 样图" width="100%" /><br/>
  <strong>水彩</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-isometric_illustration.webp" alt="isometric_illustration 样图" width="100%" /><br/>
  <strong>等距</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-comic_book.webp" alt="comic_book 样图" width="100%" /><br/>
  <strong>美式漫画</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-music.webp" alt="music 样图" width="100%" /><br/>
  <strong>音乐</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-science_fiction_concept.webp" alt="science_fiction_concept 样图" width="100%" /><br/>
  <strong>科幻概念</strong>
</td>
</tr>
<tr>
<td width="20%" align="center">
  <img src="docs/assets/showcase-infographic_data.webp" alt="infographic_data 样图" width="100%" /><br/>
  <strong>数据图表</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-kids_illustration.webp" alt="kids_illustration 样图" width="100%" /><br/>
  <strong>童书插画</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-automotive.webp" alt="automotive 样图" width="100%" /><br/>
  <strong>汽车</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-pet.webp" alt="pet 样图" width="100%" /><br/>
  <strong>宠物</strong>
</td>
<td width="20%" align="center">
  <img src="docs/assets/showcase-streetwear.webp" alt="streetwear 样图" width="100%" /><br/>
  <strong>潮牌</strong>
</td>
</tr>
</table>

<sub>首次提交只有图位的 alt 文字；codex 会在对应模板上批量补齐渲染产物。</sub>

---

## 能力清单

<p align="center">
  <img src="docs/assets/production-controls.svg" alt="生产控制能力矩阵" width="100%" />
</p>

<table>
<tr>
  <th align="left">能力</th>
  <th align="left">状态</th>
  <th align="left">命令</th>
</tr>
<tr><td>spec-first DSL（七节）</td><td>已交付</td><td><code>i2w template render</code></td></tr>
<tr><td>双语 EN + 中文</td><td>已交付</td><td><code>--lang en | zh-CN</code></td></tr>
<tr><td>成本可预测（官方 + 启发式）</td><td>已交付</td><td><code>i2w cost compare</code></td></tr>
<tr><td>API 调用前校验</td><td>已交付</td><td><code>i2w preflight</code></td></tr>
<tr><td>能力探测</td><td>已交付</td><td><code>i2w doctor capabilities</code></td></tr>
<tr><td>Batch API（5 折）</td><td>已交付</td><td><code>i2w batch sweep --route batch-api</code></td></tr>
<tr><td>Run ledger（JSONL）</td><td>已交付</td><td><code>i2w ledger query</code></td></tr>
<tr><td>快照漂移报告</td><td>已交付</td><td><code>i2w ledger drift</code></td></tr>
<tr><td>Skill 包（7 运行时）</td><td>已交付</td><td>见 <a href="./skills/gpt-image/">skills/gpt-image/</a></td></tr>
<tr><td>OCR 评测</td><td>V0.4</td><td><code>i2w eval run</code>（当前仅 prompt 层）</td></tr>
<tr><td>多模型回退</td><td>V0.4</td><td>&mdash;</td></tr>
<tr><td>PyPI / wheel 打包</td><td>V0.4</td><td>&mdash;</td></tr>
</table>

---

## 工作流

<p align="center">
  <img src="docs/assets/workflow.svg" alt="image2-workbench 工作流" width="100%" />
</p>

```
 spec.yml  ──►  i2w template render  ──►  prompt.md  ──►  Images API  ──►  image.png
                                                            │
                                                            └──►  i2w ledger 记录
```

三个阶段，一份单一事实来源。同一份 `spec.yml` 既能编译成网页 ChatGPT 直接粘贴的 markdown，又能驱动 Images API 单次渲染，还能喂 Batch API JSONL 跑批量——完全不必手工改 prompt。

---

## CLI 命令面

<table>
<tr>
  <th align="left">命令</th>
  <th align="left">用途</th>
</tr>
<tr><td><code>i2w catalog</code></td><td>浏览和搜索模板 / corpus 元数据。</td></tr>
<tr><td><code>i2w template</code></td><td>列出模板，并把 YAML spec 编译成双语 prompt。</td></tr>
<tr><td><code>i2w render</code></td><td>带本地校验和 sidecar 的图像生成 / 编辑。</td></tr>
<tr><td><code>i2w batch</code></td><td>构建可 dry-run 预览的批量 sweep 与 Batch API job。</td></tr>
<tr><td><code>i2w eval</code></td><td>跑 prompt 层 rubric 检查（OCR 评测在 V0.4）。</td></tr>
<tr><td><code>i2w cost</code></td><td>估算、对比、按预算上限收敛 Images API 花费。</td></tr>
<tr><td><code>i2w doctor</code></td><td>按账户 / 组织 / 模型探测运行时参数兼容性。</td></tr>
<tr><td><code>i2w preflight</code></td><td>API 调用前在本地拦截已知错误请求。</td></tr>
<tr><td><code>i2w ledger</code></td><td>查询成功率、时延、成本、错误分布、快照漂移。</td></tr>
<tr><td><code>i2w gallery</code></td><td>从模板生成可粘贴的 markdown gallery。</td></tr>
<tr><td><code>i2w version</code></td><td>打印当前工作台版本。</td></tr>
</table>

---

## Skill 生态

`image2-workbench` 在 [`skills/gpt-image/`](skills/gpt-image/) 提供一份可移植的 Skill 包，可直接落到任何加载 `SKILL.md` 风格 manifest 的 agent 运行时里。

<table>
<tr>
  <th align="left">运行时</th>
  <th align="left">状态</th>
  <th align="left">Manifest</th>
</tr>
<tr><td>Claude Code</td><td>已验证</td><td><a href="./skills/gpt-image/manifests/claude.json"><code>claude.json</code></a></td></tr>
<tr><td>Anthropic Skills</td><td>已验证</td><td><a href="./skills/gpt-image/manifests/claude.json"><code>claude.json</code></a></td></tr>
<tr><td>OpenAI Codex</td><td>已验证</td><td><a href="./skills/gpt-image/manifests/codex.yml"><code>codex.yml</code></a></td></tr>
<tr><td>LangChain</td><td>shim 就绪</td><td><a href="./skills/gpt-image/manifests/langchain.py"><code>langchain.py</code></a></td></tr>
<tr><td>smolagents</td><td>shim 就绪</td><td><a href="./skills/gpt-image/manifests/smolagents.py"><code>smolagents.py</code></a></td></tr>
<tr><td>OpenClaw</td><td>理论可用</td><td><a href="./skills/gpt-image/manifests/openclaw.json"><code>openclaw.json</code></a></td></tr>
<tr><td>Hermes</td><td>理论可用</td><td><a href="./skills/gpt-image/manifests/hermes.yml"><code>hermes.yml</code></a></td></tr>
</table>

[完整 Skill 兼容矩阵 &rarr;](docs/skill-compatibility.md)

---

## 常见问题

<details>
<summary><strong>这和 prompt 清单的差别在哪？</strong></summary>

prompt 清单是 markdown，这是一个编译器。模板都是 pydantic 校验过的 YAML；输出可审计；同一份模板既能编译成双语 prompt，也能直接驱动 API。详见 [`docs/positioning.md`](docs/positioning.md) 的长文论证。

</details>

<details>
<summary><strong>必须要 OpenAI API key 吗？</strong></summary>

L3 路径不要。`i2w template render` 编译出的 markdown 直接粘到网页 ChatGPT 即可（不用 key）。L2 路径（`i2w render generate`）才需要 `OPENAI_API_KEY` 和已验证的 org。`doctor capabilities`、`cost`、`preflight`、`template`、`gallery`、`catalog` 都能离线跑。

</details>

<details>
<summary><strong>为什么是 16 个领域，不是“万物皆可”？</strong></summary>

每个领域都附 `DOMAIN_CARD.md`（FOR / NOT FOR / 关键轴），相邻领域才不会黏在一起。我们只在能写出 3 条已有领域不覆盖的关键轴时，才新增一个领域。目前 12 张卡已就位，剩下 4 张会随交叉工作流的发布陆续补齐。

</details>

<details>
<summary><strong>能用中文吗？</strong></summary>

完全可以。52 个模板都支持双语；示例变量在合理处包含中文内容。编译器是“懂语言”的（CJK 标点、断行、字形密度），不是字符串替换。中文入门指南见 [`docs/getting-started.zh.md`](docs/getting-started.zh.md)。

</details>

<details>
<summary><strong>安全和审核怎么做？</strong></summary>

`i2w preflight` 跑本地校验（尺寸、背景、质量、不支持参数），并可选打 Moderation API。`MODERATION_BLOCKED` 是独立退出码（5），方便 CI 分支处理。我们不默认 `moderation: low`；要放低就显式指定。

</details>

<details>
<summary><strong>为什么是“成本 / 预检 / 审计”三支柱？</strong></summary>

工作台必须能回答 prompt 清单回答不了的三个问题：<em>“这一次要花多少钱？”</em>、<em>“付费前能不能跑通？”</em>、<em>“最近 1000 次跑下来怎么样？”</em>。每个支柱对应一个 CLI 命令面、一类退出码、JSONL ledger 的一节。

</details>

<details>
<summary><strong>内容许可怎么算？</strong></summary>

代码 Apache-2.0；模板、文档、README、Skill 的 `SKILL.md` 用 CC BY 4.0；corpus 记录按来源（见 [`source_registry.yml`](corpus/manifests/source_registry.yml)）。详见下方[许可](#许可)节。

</details>

---

## 仓库结构

```
image2-workbench/
├── src/image2_workbench/    # CLI + runtime + compiler + ledger + ...
├── templates/<domain>/       # 52 个 spec yaml + demo vars + DOMAIN_CARD
├── skills/gpt-image/         # SKILL.md + 7 个运行时 manifest
├── docs/                     # gallery、positioning、cost-modeling、...
├── corpus/                   # provenance-first prompt 记录
└── tests/                    # 420+ 单元测试和冒烟测试
```

[仓库约定（`AGENTS.md`） &rarr;](AGENTS.md)

---

## 许可

<table>
<tr>
  <th align="left">路径</th>
  <th align="left">许可</th>
</tr>
<tr><td><code>src/</code>、<code>tests/</code>、<code>scripts/</code>、<code>.github/</code></td><td>Apache-2.0（<a href="./LICENSE">LICENSE</a>）</td></tr>
<tr><td><code>templates/</code>、<code>docs/</code>、<code>README*</code>、<code>skills/gpt-image/SKILL.md</code></td><td>CC BY 4.0（<a href="./LICENSE-CONTENT">LICENSE-CONTENT</a>）</td></tr>
<tr><td><code>corpus/normalized/*.jsonl</code></td><td>按记录（见 <a href="./corpus/manifests/source_registry.yml"><code>source_registry.yml</code></a>）</td></tr>
</table>

致谢与方法见 [`NOTICE`](NOTICE)。

---

## 贡献

请先读 [`AGENTS.md`](AGENTS.md)：文件归属、反模式（默认不开 `transparent` 背景、不传 `input_fidelity`、不默认 `moderation: low`）、V1 完成标准。

安全披露走 [`SECURITY.md`](SECURITY.md)。

---

<p align="center">
  <a href="./README.md"><strong>English README &rarr;</strong></a>
</p>
