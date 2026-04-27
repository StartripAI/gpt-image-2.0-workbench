<!-- SPDX-License-Identifier: CC-BY-4.0 -->

<p align="center"><a href="./README.md"><img alt="English" src="https://img.shields.io/badge/lang-English-1f6feb?style=for-the-badge"></a> &nbsp; <a href="./README.zh.md"><img alt="中文" src="https://img.shields.io/badge/%E8%AF%AD%E8%A8%80-%E4%B8%AD%E6%96%87-d4380d?style=for-the-badge"></a></p>

<h1 align="center">image2-workbench</h1>

<p align="center"><strong>面向 OpenAI gpt-image-2 的规格先行生产工作台。</strong><br/>80 个可执行模板 &middot; 30 个领域 &middot; 双语提示词 &middot; 成本 / 预检 / 批处理 / 审计日志一体化。</p>

<p align="center"><img src="docs/assets/hero-meme.webp" alt="image2-workbench：30 个领域 80 个规格先行模板" width="900" /></p>

<!-- 徽章按三排分组,避免窄屏被挤压。 -->

<p align="center"><sub><strong>状态</strong></sub></p>
<p align="center"><img alt="version" src="https://img.shields.io/badge/version-v0.3.5-ea580c"><img alt="tests" src="https://img.shields.io/badge/%E6%B5%8B%E8%AF%95-1017%20%E9%80%9A%E8%BF%87-15803d"><img alt="ci" src="https://img.shields.io/badge/CI-%E7%BB%BF-2ea043"></p>

<p align="center"><sub><strong>规模</strong></sub></p>
<p align="center"><img alt="domains" src="https://img.shields.io/badge/%E9%A2%86%E5%9F%9F-30-1f6feb"><img alt="templates" src="https://img.shields.io/badge/%E6%A8%A1%E6%9D%BF-80-238636"><img alt="showcase webps" src="https://img.shields.io/badge/%E6%A0%B7%E5%9B%BE-30%20%E5%BC%A0%20webp-0d9488"><img alt="bilingual" src="https://img.shields.io/badge/bilingual-EN%20%2B%20%E4%B8%AD%E6%96%87-d97706"></p>

<p align="center"><sub><strong>技术栈</strong></sub></p>
<p align="center"><img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white"><img alt="License code" src="https://img.shields.io/badge/code-Apache--2.0-blue"><img alt="License content" src="https://img.shields.io/badge/templates%2Fdocs-CC%20BY%204.0-lightgrey"><img alt="CLI" src="https://img.shields.io/badge/CLI-i2w%20%C2%B7%2011%20%E5%91%BD%E4%BB%A4-334155"><img alt="Skill runtimes" src="https://img.shields.io/badge/Skill-7%20%E8%BF%90%E8%A1%8C%E6%97%B6-7c3aed"></p>

<p align="center"><a href="#-精选"><strong>✨ 精选 →</strong></a> &nbsp;&middot;&nbsp; <a href="#atlas--30-domains-80-templates"><strong>🗂️ 模板图册 →</strong></a> &nbsp;&middot;&nbsp; <a href="#-快速开始"><strong>🚀 快速开始 →</strong></a> &nbsp;&middot;&nbsp; <a href="./skills/gpt-image/"><strong>🤖 Skill →</strong></a> &nbsp;&middot;&nbsp; <a href="#-常见问题"><strong>❓ 常见问题 →</strong></a></p>

---

<a id="目录"></a>
## 📚 目录

- [✨ 精选](#-精选)
- [🚀 快速开始](#-快速开始)
- [🗂️ 模板图册 — 30 个领域，80 个模板](#atlas--30-domains-80-templates)
- [🖼️ 样图展示](#-样图展示)
- [🛠️ 能力清单](#-能力清单)
- [🔁 工作流](#-工作流)
- [💻 CLI 命令面](#-cli-命令面)
- [🤖 Skill 生态](#-skill-生态)
- [❓ 常见问题](#-常见问题)
- [🗂️ 仓库结构](#-仓库结构)
- [📜 许可](#-许可)
- [🙋 贡献](#-贡献)

---

<a id="-概览"></a>
## ✨ 概览

| 项目 | 数据 |
|---|---|
| 覆盖领域 | **30** 个（business · academic · uiux · anime · ecommerce · industrial · product · advertising · social_media · gaming · photography · fashion · food · architecture · interior · travel · typography · beauty · events · tattoo · watercolor · isometric · comic_book · music · sci-fi · dataviz · kids · automotive · pet · streetwear） |
| 可执行模板 | **80** 个规格先行的 YAML 文件,全部通过 schema 校验,全部双语 |
| 样图 | **30** 张由 gpt-image-2 渲染并提交至 `docs/assets/` |
| CLI 命令 | **11** 个动词（catalog · template · render · batch · cost · preflight · ledger · doctor · gallery · eval · version） |
| Skill 运行时 | **7** 个（Claude Code · Codex · Anthropic API · LangChain · smolagents · OpenClaw · Hermes） |
| 许可 | **Apache-2.0**（代码）+ **CC BY 4.0**（模板/文档） |
| 最后更新 | 2026-04-27 |

---

<a id="-为什么需要工作台"></a>
## 🧰 为什么需要工作台?

精选提示词清单适合找灵感。但当你需要在多个模板、多种尺寸、多种成本、多个模型快照之间得到<strong>可复现的结果</strong>,并且半年后模型快照换了还能溯源时,清单就吃力了。

本仓库把提示词包装成可审计、可执行、可批处理的工作流,围绕三大支柱:

<table cellpadding="14" cellspacing="0">
<tr>
<td width="33%" valign="top">
  <h3>💰 成本可预测</h3>
  <p>双轨成本模型:官方 <code>(尺寸, 质量)</code> 表 + 像素面积启发式 + token 级估算 + Batch API <strong>5 折</strong>路径。</p>
  <p><sub><strong>CLI:</strong> <code>i2w cost compare</code> · <code>i2w cost estimate</code> · <code>i2w cost budget</code> · <code>i2w batch sweep</code></sub></p>
</td>
<td width="33%" valign="top">
  <h3>🛡️ 错误细分</h3>
  <p>七个退出码（<code>OK</code>、<code>AUTH</code>、<code>RATE_LIMIT</code>、<code>MODERATION_BLOCKED</code>、<code>VALIDATION</code>、<code>API_OTHER</code>、<code>INTERNAL</code>），加本地校验与预审。</p>
  <p><sub><strong>CLI:</strong> <code>i2w preflight</code> · <code>i2w doctor capabilities</code></sub></p>
</td>
<td width="33%" valign="top">
  <h3>📊 可观测性</h3>
  <p>仅追加的 JSONL 审计日志（ledger）；记录成功率、p50/p95 延迟、单产出成本、快照漂移、Top 失败项。</p>
  <p><sub><strong>CLI:</strong> <code>i2w ledger query</code> · <code>i2w ledger top-failures</code> · <code>i2w ledger drift</code> · <code>i2w ledger export</code></sub></p>
</td>
</tr></table>

<p align="right"><sub><a href="docs/positioning.md">完整定位论述 →</a></sub></p>

---

<a id="-精选"></a>
## ✨ 精选

<p align="center"><sub>模板图册一目了然 —— 五张代表性合成图自 30 个领域中拼成。每张图都用 gpt-image-2 对仓库内的规格 yaml 渲染而成。</sub></p>

<p align="center"><a href="#atlas--30-domains-80-templates"><img src="docs/assets/banner-featured.webp" alt="image2-workbench 模板图册 — 30 个领域 × 80 个模板" width="100%" /></a></p>

<table cellpadding="10" cellspacing="0">
<tr>
<td width="50%" align="center" valign="top">
  <a href="docs/gallery/business.md"><img src="docs/assets/collage-business-academic.webp" alt="商业 + 学术 拼图" width="100%" /></a><br/>
  <strong>📊 商业 · 🎓 学术</strong><br/>
  <sub>SWOT 卡 · 路演 deck · 科学示意图 · 期刊海报</sub>
</td>
<td width="50%" align="center" valign="top">
  <a href="docs/gallery/uiux.md"><img src="docs/assets/collage-uiux-anime.webp" alt="UI/UX + 动漫 拼图" width="100%" /></a><br/>
  <strong>📱 UI/UX · 🎌 动漫</strong><br/>
  <sub>iOS 原型 · Web 仪表盘 · 角色设定表 · 八格漫画</sub>
</td>
</tr>
<tr>
<td width="50%" align="center" valign="top">
  <a href="docs/gallery/fashion.md"><img src="docs/assets/collage-creative-lifestyle.webp" alt="时尚 + 纹身 拼图" width="100%" /></a><br/>
  <strong>👗 时尚 · 🪡 纹身</strong><br/>
  <sub>Lookbook · 秀场海报 · flash 图集 · 极简刺青</sub>
</td>
<td width="50%" align="center" valign="top">
  <a href="docs/gallery/architecture.md"><img src="docs/assets/collage-spatial-systems.webp" alt="建筑 + 数据图表 拼图" width="100%" /></a><br/>
  <strong>🏛️ 建筑 · 📈 数据图表</strong><br/>
  <sub>立面研究 · 汇报展板 · 仪表盘 · 图表解析</sub>
</td>
</tr></table>

<p align="center"><sub>↓ 向下滚动查看完整<a href="#-样图展示">30 个领域样图网格</a> · <a href="#atlas--30-domains-80-templates">浏览模板图册</a></sub></p>

---

<a id="-快速开始"></a>
## 🚀 快速开始

<details open>
<summary><strong>安装（约 30 秒）</strong></summary>

```bash
# fork 之后克隆,或直接基于本地 checkout 工作:
git clone https://github.com/StartripAI/gpt-image-2.0-workbench.git
cd gpt-image-2.0-workbench

python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

i2w --help                  # 11 个命令
i2w doctor capabilities     # 探测参数兼容性（无需 API key）
pytest -q                   # 工作台自检（1017+ 通过）
```

</details>

<details>
<summary><strong>渲染你的第一条提示词（无需 API key）</strong></summary>

```bash
i2w template render business_swot_card --lang zh-CN \
  --vars templates/business/_vars_examples/swot_acme.yml \
  --out out/swot.zh.md
cat out/swot.zh.md   # 复制到网页 ChatGPT 即可
```

把 markdown 粘进 ChatGPT 的图片对话,下载图片即可。这是 L3 路径 —— 纯网页、零花费、零 API key。

</details>

<details>
<summary><strong>通过 API 渲染（需要 <code>OPENAI_API_KEY</code>）</strong></summary>

```bash
export OPENAI_API_KEY=sk-...

# 在花钱前先在本地拦截坏请求:
i2w preflight out/swot.zh.md --template-id business_swot_card

# 提交前对比不同 (尺寸, 质量) 的成本:
i2w cost compare --size 1024x1024,1536x1024 --quality low,medium,high

# 渲染并写入一行审计日志:
i2w render generate --prompt-file out/swot.zh.md \
  --template-id business_swot_card \
  --size 1536x1024 --quality medium --out out/swot.png

# 查看刚刚发生了什么:
i2w ledger query --template business_swot_card
```

</details>

<details>
<summary><strong>跑一次 Batch API 扫描（5 折优惠）</strong></summary>

```bash
i2w batch sweep \
  --template business_swot_card \
  --vars templates/business/_vars_examples/swot_acme.yml \
  --route batch-api \
  --dry-run                                # 预览 JSONL 载荷,不花钱

i2w batch sweep ... --route batch-api      # 准备好后再正式提交
```

</details>

<p><sub><a href="docs/getting-started.zh.md">完整入门 →</a> &nbsp;·&nbsp; <a href="docs/cost-modeling.md">成本建模 →</a> &nbsp;·&nbsp; <a href="docs/error-codes.md">错误码 →</a></sub></p>

---

<!-- BEGIN GALLERY (auto-generated by `i2w gallery readme`; do not edit by hand) -->

## 模板图册 — 30 个领域，80 个模板

<table cellpadding="12" cellspacing="0">
<tr>
<td width="33%" valign="top">

<a id="domain-academic"></a>
### 🎓 academic · 4 个模板 &nbsp; <a href="docs/gallery/academic.md"><img src="docs/assets/showcase-academic.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>academic_chalkboard_proof</strong><br/>Photorealistic university chalkboard with a four-step mathematical proof and QED line. | 1920x1088 | text_fidelity_dense |
| <strong>academic_journal_poster</strong><br/>Vertical 3-column conference poster with intro, methods, results, conclusion. | 1088x1920 | text_fidelity_dense |
| <strong>academic_multilingual_eduposter</strong><br/>Multilingual education infographic. Designed for Korean / Japanese / Chinese / Arabic / Hindi educational posters; the image's text is in language_na… | 1920x1088 | text_fidelity_dense |
| <strong>academic_scientific_diagram</strong><br/>Museum-style cross-section or labeled scientific illustration with five callouts. | 1536x1024 | text_fidelity_dense |

<sub><a href="docs/gallery/academic.md"><strong>查看 4 条 →</strong></a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-advertising"></a>
### 📢 advertising · 3 个模板 &nbsp; <a href="docs/gallery/advertising.md"><img src="docs/assets/showcase-advertising.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>advertising_billboard_mockup</strong><br/>Photoreal urban billboard mockup with the hero ad pasted on a real-feeling outdoor placement. | 1920x1088 | layout |
| <strong>advertising_campaign_key_visual</strong><br/>Premium production-grade brand campaign hero key-visual with tagline, product name, and call-to-action. | 1920x1088 | text_fidelity_dense |
| <strong>advertising_storyboard_3frame</strong><br/>Three-panel storyboard sketch for a 30-second commercial, with brand seal beneath the panels. | 1536x1024 | continuity |

<sub><a href="docs/gallery/advertising.md"><strong>查看 3 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/advertising/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-anime"></a>
### 🎌 anime · 4 个模板 &nbsp; <a href="docs/gallery/anime.md"><img src="docs/assets/showcase-anime.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>anime_ccd_candid</strong><br/>复古 CCD 相机风格自拍 / Vintage CCD camera-style candid (a non-photoreal staged "authenticity"). | 1088x1920 | text_fidelity_sparse |
| <strong>anime_character_sheet</strong><br/>Concept-art character reference sheet with three-view turnaround, expression sheet, and prop detail. | 1920x1088 | continuity |
| <strong>anime_city_poster</strong><br/>双语城市旅行海报 / Bilingual editorial city travel poster mixing calligraphic skyline and premium typography. | 1088x1920 | text_fidelity_dense |
| <strong>anime_comic_8panel</strong><br/>Eight-panel sequential manga page rendered in black-and-white seinen ink with strict character continuity. | 1024x1536 | continuity |

<sub><a href="docs/gallery/anime.md"><strong>查看 4 条 →</strong></a></sub>

</td>
</tr>
<tr>
<td width="33%" valign="top">

<a id="domain-architecture"></a>
### 🏛️ architecture · 3 个模板 &nbsp; <a href="docs/gallery/architecture.md"><img src="docs/assets/showcase-architecture.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>architecture_facade_concept</strong><br/>Conceptual exterior facade rendering for an architecture studio's project poster. | 1536x1024 | text_fidelity_dense |
| <strong>architecture_presentation_board</strong><br/>Multi-panel architecture presentation board combining concept, diagram, render, and short text. | 1920x1088 | layout |
| <strong>architecture_site_diagram</strong><br/>Site plan / urban-context diagram with three labeled zones, drawn in plan view. | 1920x1088 | text_fidelity_dense |

<sub><a href="docs/gallery/architecture.md"><strong>查看 3 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/architecture/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-automotive"></a>
### 🚗 automotive · 2 个模板 &nbsp; <a href="docs/gallery/automotive.md"><img src="docs/assets/showcase-automotive.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>automotive_dealership_poster</strong><br/>Point-of-sale dealership poster — vehicle hero plus price, financing terms, and dealer name. | 1024x1280 | text_fidelity_dense |
| <strong>automotive_hero_ad</strong><br/>Cinematic single-vehicle hero ad — fictional car, motorcycle, or EV on a deliberate backdrop. | 1920x1088 | text_fidelity_sparse |

<sub><a href="docs/gallery/automotive.md"><strong>查看 2 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/automotive/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-beauty"></a>
### 💄 beauty · 2 个模板 &nbsp; <a href="docs/gallery/beauty.md"><img src="docs/assets/showcase-beauty.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>beauty_editorial_layout</strong><br/>Magazine-style beauty editorial spread — close-up beauty shot with small product callouts. | 1024x1280 | text_fidelity_sparse |
| <strong>beauty_skincare_packaging</strong><br/>Single skincare unit on minimal staging — bottle / jar / dropper as design hero. | 1024x1024 | text_fidelity_dense |

<sub><a href="docs/gallery/beauty.md"><strong>查看 2 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/beauty/DOMAIN_CARD.md">域卡</a></sub>

</td>
</tr>
<tr>
<td width="33%" valign="top">

<a id="domain-business"></a>
### 📊 business · 4 个模板 &nbsp; <a href="docs/gallery/business.md"><img src="docs/assets/showcase-business.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>business_data_dashboard</strong><br/>Light-theme analytics dashboard mockup with KPI tiles and two illustrative charts. | 1920x1088 | layout |
| <strong>business_linkedin_carousel</strong><br/>LinkedIn "by the numbers" carousel cover slide with bold dark-mode typography. | 1152x1440 | text_fidelity_dense |
| <strong>business_pitch_slide</strong><br/>Single-slide pitch deck cover with hero tagline and three headline metrics. | 1920x1088 | text_fidelity_dense |
| <strong>business_swot_card</strong><br/>Four-quadrant SWOT analysis card for executive briefings and quarterly reviews. | 1536x1024 | text_fidelity_dense |

<sub><a href="docs/gallery/business.md"><strong>查看 4 条 →</strong></a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-comic_book"></a>
### 💥 comic_book · 2 个模板 &nbsp; <a href="docs/gallery/comic_book.md"><img src="docs/assets/showcase-comic_book.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>comic_book_panel_page</strong><br/>Multi-panel American comic-book interior page with speech balloons, halftone shading, and short panel captions. | 1024x1536 | continuity |
| <strong>comic_book_variant_cover</strong><br/>Single-figure American comic-book variant cover with masthead, issue number, and credit slug, in bold inks and halftone. | 1024x1536 | text_fidelity_dense |

<sub><a href="docs/gallery/comic_book.md"><strong>查看 2 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/comic_book/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-ecommerce"></a>
### 🛍️ ecommerce · 3 个模板 &nbsp; <a href="docs/gallery/ecommerce.md"><img src="docs/assets/showcase-ecommerce.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>ecommerce_category_banner</strong><br/>Wide 16:9 storefront category banner with a row of product silhouettes, headline, sub-text, and CTA. | 1920x1088 | text_fidelity_dense |
| <strong>ecommerce_marketplace_card</strong><br/>Compact 1:1 marketplace tile — product, price, and a single trust badge — built for grid views. | 1024x1024 | layout |
| <strong>ecommerce_product_hero</strong><br/>Single-SKU hero card for a product detail page — large product silhouette, price tag, primary CTA. | 1024x1280 | layout |

<sub><a href="docs/gallery/ecommerce.md"><strong>查看 3 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/ecommerce/DOMAIN_CARD.md">域卡</a></sub>

</td>
</tr>
<tr>
<td width="33%" valign="top">

<a id="domain-events"></a>
### 🎫 events · 2 个模板 &nbsp; <a href="docs/gallery/events.md"><img src="docs/assets/showcase-events.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>events_concert_poster</strong><br/>Vertical concert / festival poster with headliner, support, date, and venue. | 1088x1920 | text_fidelity_dense |
| <strong>events_wedding_invite</strong><br/>Wedding invitation card — formal vertical layout with names, date, venue, and RSVP. | 1024x1280 | text_fidelity_dense |

<sub><a href="docs/gallery/events.md"><strong>查看 2 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/events/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-fashion"></a>
### 👗 fashion · 3 个模板 &nbsp; <a href="docs/gallery/fashion.md"><img src="docs/assets/showcase-fashion.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>fashion_flatlay_board</strong><br/>Styled flatlay of garments and accessories arranged on a surface for editorial use. | 1024x1024 | layout |
| <strong>fashion_lookbook_page</strong><br/>Editorial lookbook page — single-look hero shot with brand caption and item credits. | 1024x1280 | text_fidelity_dense |
| <strong>fashion_runway_poster</strong><br/>Vertical runway / show poster — brutalist editorial fashion-week announcement. | 1088x1920 | text_fidelity_dense |

<sub><a href="docs/gallery/fashion.md"><strong>查看 3 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/fashion/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-food"></a>
### 🍽️ food · 3 个模板 &nbsp; <a href="docs/gallery/food.md"><img src="docs/assets/showcase-food.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>food_menu_poster</strong><br/>Vertical restaurant menu wall poster — categorized dish list with prices and accent. | 1088x1920 | text_fidelity_dense |
| <strong>food_packaging_label</strong><br/>Packaged-goods label mock — branded coffee bag, bottle, or jar wrapper design. | 1152x1536 | text_fidelity_dense |
| <strong>food_recipe_card</strong><br/>Single-recipe card — image hero with recipe meta and key-ingredient callout. | 1024x1280 | text_fidelity_dense |

<sub><a href="docs/gallery/food.md"><strong>查看 3 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/food/DOMAIN_CARD.md">域卡</a></sub>

</td>
</tr>
<tr>
<td width="33%" valign="top">

<a id="domain-gaming"></a>
### 🎮 gaming · 3 个模板 &nbsp; <a href="docs/gallery/gaming.md"><img src="docs/assets/showcase-gaming.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>gaming_hud_mockup</strong><br/>Fictional video-game HUD mockup with health and mana bars, minimap, mission objective overlay. | 1920x1088 | text_fidelity_dense |
| <strong>gaming_item_card</strong><br/>Vertical 3:4 collectible RPG/CCG-style item card with name, rarity ribbon, stat lines, and lore blurb. | 1152x1536 | text_fidelity_dense |
| <strong>gaming_map_panel</strong><br/>16:9 fantasy world-map / quest-map panel with three labeled regions and a parchment border. | 1920x1088 | layout |

<sub><a href="docs/gallery/gaming.md"><strong>查看 3 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/gaming/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-industrial"></a>
### 🏭 industrial · 3 个模板 &nbsp; <a href="docs/gallery/industrial.md"><img src="docs/assets/showcase-industrial.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>industrial_cutaway_view</strong><br/>Isometric cutaway / exploded view of an industrial machine with four labeled internal components. | 1536x1024 | text_fidelity_dense |
| <strong>industrial_process_diagram</strong><br/>Wide 16:9 industrial process-flow diagram with four labeled stages and connecting arrows. | 1920x1088 | text_fidelity_dense |
| <strong>industrial_safety_poster</strong><br/>Vertical 9:16 factory-floor safety / hazard / PPE notice for posting at line entry points. | 1088x1920 | text_fidelity_dense |

<sub><a href="docs/gallery/industrial.md"><strong>查看 3 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/industrial/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-infographic_data"></a>
### 📈 infographic_data · 2 个模板 &nbsp; <a href="docs/gallery/infographic_data.md"><img src="docs/assets/showcase-infographic_data.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>infographic_data_chart_explainer</strong><br/>Single-chart explainer panel — large hero chart annotated with three pull-out callouts and a source line. | 1024x1280 | text_fidelity_dense |
| <strong>infographic_data_dashboard</strong><br/>Editorial dataviz dashboard explainer with four chart panels, headline, and insight callouts. | 1920x1088 | text_fidelity_dense |

<sub><a href="docs/gallery/infographic_data.md"><strong>查看 2 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/infographic_data/DOMAIN_CARD.md">域卡</a></sub>

</td>
</tr>
<tr>
<td width="33%" valign="top">

<a id="domain-interior"></a>
### 🛋️ interior · 3 个模板 &nbsp; <a href="docs/gallery/interior.md"><img src="docs/assets/showcase-interior.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>interior_before_after</strong><br/>Split-screen interior before/after edit; left panel preserves the original, right panel shows the renovation. | 1920x1088 | edit_locality |
| <strong>interior_material_board</strong><br/>Square material / finish / color board (4-6 swatches with named labels) for an interior project. | 1024x1024 | layout |
| <strong>interior_room_mockup</strong><br/>Photoreal single-room interior mockup (bedroom / living / kitchen) with one labelled accent zone. | 1536x1024 | text_fidelity_sparse |

<sub><a href="docs/gallery/interior.md"><strong>查看 3 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/interior/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-isometric_illustration"></a>
### 🧊 isometric_illustration · 2 个模板 &nbsp; <a href="docs/gallery/isometric_illustration.md"><img src="docs/assets/showcase-isometric_illustration.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>isometric_city_block</strong><br/>True-isometric city block with named buildings, tiny vehicles, and street trees, projected on a strict 30-30 grid. | 1024x1024 | layout |
| <strong>isometric_workspace_scene</strong><br/>Isometric workspace scene — desk, studio, and side station — in true 30-30 projection with labeled accessories. | 1920x1088 | layout |

<sub><a href="docs/gallery/isometric_illustration.md"><strong>查看 2 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/isometric_illustration/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-kids_illustration"></a>
### 🧸 kids_illustration · 2 个模板 &nbsp; <a href="docs/gallery/kids_illustration.md"><img src="docs/assets/showcase-kids_illustration.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>kids_illustration_storybook_spread</strong><br/>Two-page children's storybook spread with friendly cast, narration band, and a single dialogue line. | 1920x1088 | text_fidelity_dense |
| <strong>kids_illustration_workbook_page</strong><br/>Preschool workbook page — counting / matching / coloring activity with friendly characters and a clear instruction line. | 1024x1280 | text_fidelity_dense |

<sub><a href="docs/gallery/kids_illustration.md"><strong>查看 2 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/kids_illustration/DOMAIN_CARD.md">域卡</a></sub>

</td>
</tr>
<tr>
<td width="33%" valign="top">

<a id="domain-music"></a>
### 🎵 music · 2 个模板 &nbsp; <a href="docs/gallery/music.md"><img src="docs/assets/showcase-music.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>music_album_cover</strong><br/>Square album-cover artwork — single hero visual identity with artist and album metadata. | 1024x1024 | text_fidelity_dense |
| <strong>music_concert_poster</strong><br/>Vertical tour / concert poster — headliner identity with tour name, dates, and city run. | 1088x1920 | text_fidelity_dense |

<sub><a href="docs/gallery/music.md"><strong>查看 2 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/music/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-pet"></a>
### 🐾 pet · 2 个模板 &nbsp; <a href="docs/gallery/pet.md"><img src="docs/assets/showcase-pet.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>pet_adoption_flyer</strong><br/>Single-animal adoption flyer — companion-animal photo with name, age, key trait, and shelter contact. | 1024x1280 | text_fidelity_dense |
| <strong>pet_food_packaging</strong><br/>Pet-food bag or can label — branded packaging plate with feeding metadata. | 1152x1536 | text_fidelity_dense |

<sub><a href="docs/gallery/pet.md"><strong>查看 2 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/pet/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-photography"></a>
### 📷 photography · 3 个模板 &nbsp; <a href="docs/gallery/photography.md"><img src="docs/assets/showcase-photography.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>photography_cinematic_still</strong><br/>Film-frame still — anamorphic cinematic look capturing a single narrative beat. | 1920x1088 | text_fidelity_sparse |
| <strong>photography_documentary_scene</strong><br/>Documentary photojournalism — natural, candid scene grounded in real-world observation. | 1536x1024 | text_fidelity_sparse |
| <strong>photography_editorial_portrait</strong><br/>Magazine-style editorial portrait — single subject, deliberate light and lens choice. | 1024x1280 | text_fidelity_sparse |

<sub><a href="docs/gallery/photography.md"><strong>查看 3 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/photography/DOMAIN_CARD.md">域卡</a></sub>

</td>
</tr>
<tr>
<td width="33%" valign="top">

<a id="domain-product"></a>
### 📦 product · 3 个模板 &nbsp; <a href="docs/gallery/product.md"><img src="docs/assets/showcase-product.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>product_comparison_board</strong><br/>Vertical 4:5 side-by-side comparison of three product variants with feature checkboxes by axis. | 1024x1280 | text_fidelity_dense |
| <strong>product_feature_callout</strong><br/>Hero shot of one product with three feature callouts arranged around it on a horizontal canvas. | 1920x1088 | layout |
| <strong>product_packaging_concept</strong><br/>Single-product packaging concept rendering — branded box / bottle / pouch on a minimal studio backdrop. | 1024x1024 | text_fidelity_dense |

<sub><a href="docs/gallery/product.md"><strong>查看 3 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/product/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-science_fiction_concept"></a>
### 🚀 science_fiction_concept · 2 个模板 &nbsp; <a href="docs/gallery/science_fiction_concept.md"><img src="docs/assets/showcase-science_fiction_concept.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>science_fiction_concept_keyframe</strong><br/>Cinematic sci-fi keyframe matte painting — alien landscape or far-future urban scene with painterly atmosphere. | 1920x1088 | text_fidelity_sparse |
| <strong>science_fiction_concept_vehicle_hero</strong><br/>Hero side-view concept-art plate of a fictional sci-fi vehicle, mech, or spacecraft on a clean studio plate. | 1920x1088 | text_fidelity_sparse |

<sub><a href="docs/gallery/science_fiction_concept.md"><strong>查看 2 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/science_fiction_concept/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-social_media"></a>
### 🗯️ social_media · 3 个模板 &nbsp; <a href="docs/gallery/social_media.md"><img src="docs/assets/showcase-social_media.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>social_media_launch_post</strong><br/>1:1 feed-friendly Instagram or X launch announcement post for a new product, with date and CTA. | 1024x1024 | text_fidelity_dense |
| <strong>social_media_story_sequence</strong><br/>9:16 vertical Instagram-Story-style 3-frame mini-narrative grid stitched into one image. | 1088x1920 | continuity |
| <strong>social_media_thumbnail_grid</strong><br/>1:1 YouTube-style 3-up thumbnail grid for previewing alternate channel-cover thumbnail concepts. | 1024x1024 | layout |

<sub><a href="docs/gallery/social_media.md"><strong>查看 3 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/social_media/DOMAIN_CARD.md">域卡</a></sub>

</td>
</tr>
<tr>
<td width="33%" valign="top">

<a id="domain-streetwear"></a>
### 👟 streetwear · 2 个模板 &nbsp; <a href="docs/gallery/streetwear.md"><img src="docs/assets/showcase-streetwear.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>streetwear_lookbook_drop</strong><br/>Drop-announcement lookbook plate — single street look with drop date and collection name. | 1024x1280 | text_fidelity_dense |
| <strong>streetwear_sneaker_hero</strong><br/>Single sneaker hero shot — stage-lit isolation plate for a fictional drop colorway. | 1024x1024 | text_fidelity_sparse |

<sub><a href="docs/gallery/streetwear.md"><strong>查看 2 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/streetwear/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-tattoo"></a>
### 🪡 tattoo · 2 个模板 &nbsp; <a href="docs/gallery/tattoo.md"><img src="docs/assets/showcase-tattoo.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>tattoo_flash_sheet</strong><br/>Traditional tattoo flash sheet — multiple design vignettes on aged paper. | 1024x1280 | layout |
| <strong>tattoo_minimal_design</strong><br/>Single isolated minimalist tattoo design on stark white substrate. | 1024x1024 | text_fidelity_sparse |

<sub><a href="docs/gallery/tattoo.md"><strong>查看 2 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/tattoo/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-travel"></a>
### ✈️ travel · 3 个模板 &nbsp; <a href="docs/gallery/travel.md"><img src="docs/assets/showcase-travel.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>travel_destination_poster</strong><br/>Vintage-style travel poster for a fictional or generic destination, with name, tagline, and year. | 1024x1536 | text_fidelity_dense |
| <strong>travel_itinerary_card</strong><br/>Single-page vertical itinerary card with day-by-day items for a short trip. | 1088x1920 | text_fidelity_dense |
| <strong>travel_map_guide</strong><br/>Illustrated tourist map with three numbered points of interest across a generic region. | 1920x1088 | layout |

<sub><a href="docs/gallery/travel.md"><strong>查看 3 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/travel/DOMAIN_CARD.md">域卡</a></sub>

</td>
</tr>
<tr>
<td width="33%" valign="top">

<a id="domain-typography"></a>
### 🔤 typography · 2 个模板 &nbsp; <a href="docs/gallery/typography.md"><img src="docs/assets/showcase-typography.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>typography_lettering_art</strong><br/>Hand-lettered art piece — a single phrase rendered as the visual subject. | 1024x1024 | text_fidelity_dense |
| <strong>typography_specimen_poster</strong><br/>Type specimen poster — display alphabet, glyph grid, and typeface metadata as the artwork. | 1024x1280 | text_fidelity_dense |

<sub><a href="docs/gallery/typography.md"><strong>查看 2 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/typography/DOMAIN_CARD.md">域卡</a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-uiux"></a>
### 📱 uiux · 4 个模板 &nbsp; <a href="docs/gallery/uiux.md"><img src="docs/assets/showcase-uiux.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>uiux_design_system_card</strong><br/>Square design-system showcase card highlighting a single component or token with prop rows. | 1024x1024 | text_fidelity_dense |
| <strong>uiux_ios_app_mockup</strong><br/>Hyper-realistic iPhone app screenshot mockup with native iOS chrome and a card-based content feed. | 1088x1920 | text_fidelity_dense |
| <strong>uiux_social_cover_xhs</strong><br/>中文小红书风格教程封面 / Chinese-language Xiaohongshu cover for tutorial or lifestyle topic. | 1152x1536 | text_fidelity_dense |
| <strong>uiux_web_dashboard</strong><br/>Clean B2B SaaS analytics dashboard mockup with sidebar nav, KPI grid, and a primary chart. | 1920x1088 | text_fidelity_dense |

<sub><a href="docs/gallery/uiux.md"><strong>查看 4 条 →</strong></a></sub>

</td>
<td width="33%" valign="top">

<a id="domain-watercolor_illustration"></a>
### 🎨 watercolor_illustration · 2 个模板 &nbsp; <a href="docs/gallery/watercolor_illustration.md"><img src="docs/assets/showcase-watercolor_illustration.webp" width="60" height="40" align="right" alt=""/></a>

| 模板 | 尺寸 | 评测 |
|---|---|---|
| <strong>watercolor_botanical_study</strong><br/>Single-specimen botanical watercolor study with latin caption, in transparent washes on visibly textured paper. | 1024x1280 | text_fidelity_sparse |
| <strong>watercolor_character_portrait</strong><br/>Three-quarter character portrait painted in transparent watercolor washes with visible paper grain and a small footer caption. | 1024x1280 | text_fidelity_sparse |

<sub><a href="docs/gallery/watercolor_illustration.md"><strong>查看 2 条 →</strong></a> &nbsp;·&nbsp; <a href="templates/watercolor_illustration/DOMAIN_CARD.md">域卡</a></sub>

</td>
</tr>
</table>

<p align="center"><strong>按领域浏览：</strong> <a href="#domain-academic">🎓 academic</a> · <a href="#domain-advertising">📢 advertising</a> · <a href="#domain-anime">🎌 anime</a> · <a href="#domain-architecture">🏛️ architecture</a> · <a href="#domain-automotive">🚗 automotive</a> · <a href="#domain-beauty">💄 beauty</a> · <a href="#domain-business">📊 business</a> · <a href="#domain-comic_book">💥 comic_book</a> · <a href="#domain-ecommerce">🛍️ ecommerce</a> · <a href="#domain-events">🎫 events</a> · <a href="#domain-fashion">👗 fashion</a> · <a href="#domain-food">🍽️ food</a> · <a href="#domain-gaming">🎮 gaming</a> · <a href="#domain-industrial">🏭 industrial</a> · <a href="#domain-infographic_data">📈 infographic_data</a> · <a href="#domain-interior">🛋️ interior</a> · <a href="#domain-isometric_illustration">🧊 isometric_illustration</a> · <a href="#domain-kids_illustration">🧸 kids_illustration</a> · <a href="#domain-music">🎵 music</a> · <a href="#domain-pet">🐾 pet</a> · <a href="#domain-photography">📷 photography</a> · <a href="#domain-product">📦 product</a> · <a href="#domain-science_fiction_concept">🚀 science_fiction_concept</a> · <a href="#domain-social_media">🗯️ social_media</a> · <a href="#domain-streetwear">👟 streetwear</a> · <a href="#domain-tattoo">🪡 tattoo</a> · <a href="#domain-travel">✈️ travel</a> · <a href="#domain-typography">🔤 typography</a> · <a href="#domain-uiux">📱 uiux</a> · <a href="#domain-watercolor_illustration">🎨 watercolor_illustration</a> · <a href="#目录">↑ 返回目录</a></p>

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

<a id="-样图展示"></a>
## 🖼️ 样图展示 — 30 个领域，30 张代表渲染

<p align="center"><sub>每个领域一张代表样图,由 gpt-image-2 对应 <a href="templates/"><code>templates/&lt;domain&gt;/</code></a> 下的规格 yaml 渲染。点击任意卡片可直达对应图册子页。同一组内按字母顺序排列,便于扫读。</sub></p>

### 企业与知识

<table cellpadding="8" cellspacing="0">
<tr>
<td width="20%" align="center" valign="top"><a href="docs/gallery/business.md"><img src="docs/assets/showcase-business.webp" width="100%" alt="business showcase"/></a><br/><sub><strong>📊 商业 (business)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/academic.md"><img src="docs/assets/showcase-academic.webp" width="100%" alt="academic showcase"/></a><br/><sub><strong>🎓 学术 (academic)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/uiux.md"><img src="docs/assets/showcase-uiux.webp" width="100%" alt="uiux showcase"/></a><br/><sub><strong>📱 UI/UX (uiux)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/social_media.md"><img src="docs/assets/showcase-social_media.webp" width="100%" alt="social media showcase"/></a><br/><sub><strong>🗯️ 社交媒体 (social_media)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/infographic_data.md"><img src="docs/assets/showcase-infographic_data.webp" width="100%" alt="dataviz showcase"/></a><br/><sub><strong>📈 数据图表 (infographic_data)</strong></sub></td>
</tr></table>

### 商业与品牌

<table cellpadding="8" cellspacing="0">
<tr>
<td width="20%" align="center" valign="top"><a href="docs/gallery/ecommerce.md"><img src="docs/assets/showcase-ecommerce.webp" width="100%" alt="ecommerce showcase"/></a><br/><sub><strong>🛍️ 电商 (ecommerce)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/product.md"><img src="docs/assets/showcase-product.webp" width="100%" alt="product showcase"/></a><br/><sub><strong>📦 产品 (product)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/advertising.md"><img src="docs/assets/showcase-advertising.webp" width="100%" alt="advertising showcase"/></a><br/><sub><strong>📢 广告 (advertising)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/streetwear.md"><img src="docs/assets/showcase-streetwear.webp" width="100%" alt="streetwear showcase"/></a><br/><sub><strong>👟 潮牌 (streetwear)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/automotive.md"><img src="docs/assets/showcase-automotive.webp" width="100%" alt="automotive showcase"/></a><br/><sub><strong>🚗 汽车 (automotive)</strong></sub></td>
</tr></table>

### 创意与叙事

<table cellpadding="8" cellspacing="0">
<tr>
<td width="20%" align="center" valign="top"><a href="docs/gallery/anime.md"><img src="docs/assets/showcase-anime.webp" width="100%" alt="anime showcase"/></a><br/><sub><strong>🎌 动漫 (anime)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/comic_book.md"><img src="docs/assets/showcase-comic_book.webp" width="100%" alt="comic_book showcase"/></a><br/><sub><strong>💥 美式漫画 (comic_book)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/gaming.md"><img src="docs/assets/showcase-gaming.webp" width="100%" alt="gaming showcase"/></a><br/><sub><strong>🎮 游戏 (gaming)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/science_fiction_concept.md"><img src="docs/assets/showcase-science_fiction_concept.webp" width="100%" alt="science_fiction_concept showcase"/></a><br/><sub><strong>🚀 科幻概念 (sci-fi)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/kids_illustration.md"><img src="docs/assets/showcase-kids_illustration.webp" width="100%" alt="kids_illustration showcase"/></a><br/><sub><strong>🧸 童书插画 (kids)</strong></sub></td>
</tr></table>

### 生活方式与美学

<table cellpadding="8" cellspacing="0">
<tr>
<td width="20%" align="center" valign="top"><a href="docs/gallery/fashion.md"><img src="docs/assets/showcase-fashion.webp" width="100%" alt="fashion showcase"/></a><br/><sub><strong>👗 时尚 (fashion)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/beauty.md"><img src="docs/assets/showcase-beauty.webp" width="100%" alt="beauty showcase"/></a><br/><sub><strong>💄 美妆 (beauty)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/photography.md"><img src="docs/assets/showcase-photography.webp" width="100%" alt="photography showcase"/></a><br/><sub><strong>📷 摄影 (photography)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/tattoo.md"><img src="docs/assets/showcase-tattoo.webp" width="100%" alt="tattoo showcase"/></a><br/><sub><strong>🪡 纹身 (tattoo)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/watercolor_illustration.md"><img src="docs/assets/showcase-watercolor_illustration.webp" width="100%" alt="watercolor_illustration showcase"/></a><br/><sub><strong>🎨 水彩 (watercolor)</strong></sub></td>
</tr></table>

### 空间与系统

<table cellpadding="8" cellspacing="0">
<tr>
<td width="20%" align="center" valign="top"><a href="docs/gallery/architecture.md"><img src="docs/assets/showcase-architecture.webp" width="100%" alt="architecture showcase"/></a><br/><sub><strong>🏛️ 建筑 (architecture)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/interior.md"><img src="docs/assets/showcase-interior.webp" width="100%" alt="interior showcase"/></a><br/><sub><strong>🛋️ 室内 (interior)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/industrial.md"><img src="docs/assets/showcase-industrial.webp" width="100%" alt="industrial showcase"/></a><br/><sub><strong>🏭 工业 (industrial)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/isometric_illustration.md"><img src="docs/assets/showcase-isometric_illustration.webp" width="100%" alt="isometric_illustration showcase"/></a><br/><sub><strong>🧊 等距 (isometric)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/typography.md"><img src="docs/assets/showcase-typography.webp" width="100%" alt="typography showcase"/></a><br/><sub><strong>🔤 字体 (typography)</strong></sub></td>
</tr></table>

### 文化与时刻

<table cellpadding="8" cellspacing="0">
<tr>
<td width="20%" align="center" valign="top"><a href="docs/gallery/events.md"><img src="docs/assets/showcase-events.webp" width="100%" alt="events showcase"/></a><br/><sub><strong>🎫 活动 (events)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/music.md"><img src="docs/assets/showcase-music.webp" width="100%" alt="music showcase"/></a><br/><sub><strong>🎵 音乐 (music)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/food.md"><img src="docs/assets/showcase-food.webp" width="100%" alt="food showcase"/></a><br/><sub><strong>🍽️ 餐饮 (food)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/pet.md"><img src="docs/assets/showcase-pet.webp" width="100%" alt="pet showcase"/></a><br/><sub><strong>🐾 宠物 (pet)</strong></sub></td>
<td width="20%" align="center" valign="top"><a href="docs/gallery/travel.md"><img src="docs/assets/showcase-travel.webp" width="100%" alt="travel showcase"/></a><br/><sub><strong>✈️ 旅行 (travel)</strong></sub></td>
</tr></table>

<p align="center"><sub>↑ <a href="#-精选">回到精选</a> &nbsp;·&nbsp; ↓ <a href="#atlas--30-domains-80-templates">模板图册细节</a> &nbsp;·&nbsp; <a href="#目录">↑ 返回目录</a></sub></p>

---

<a id="-能力清单"></a>
## 🛠️ 能力清单

<p align="center"><img src="docs/assets/production-controls.svg" alt="生产控制 — 能力矩阵" width="100%" /></p>

| 能力 | 状态 | CLI |
|---|---|---|
| 规格先行 DSL（七节结构） | ![已上线](https://img.shields.io/badge/-%E5%B7%B2%E4%B8%8A%E7%BA%BF-2ea043) | `i2w template render` |
| 双语 EN + 中文 | ![已上线](https://img.shields.io/badge/-%E5%B7%B2%E4%B8%8A%E7%BA%BF-2ea043) | `--lang en\|zh-CN` |
| 成本可预测 | ![已上线](https://img.shields.io/badge/-%E5%B7%B2%E4%B8%8A%E7%BA%BF-2ea043) | `i2w cost compare` |
| API 前置校验 | ![已上线](https://img.shields.io/badge/-%E5%B7%B2%E4%B8%8A%E7%BA%BF-2ea043) | `i2w preflight` |
| 能力探针 | ![已上线](https://img.shields.io/badge/-%E5%B7%B2%E4%B8%8A%E7%BA%BF-2ea043) | `i2w doctor capabilities` |
| Batch API（5 折优惠） | ![已上线](https://img.shields.io/badge/-%E5%B7%B2%E4%B8%8A%E7%BA%BF-2ea043) | `i2w batch sweep --route batch-api` |
| 运行 ledger（JSONL 审计日志） | ![已上线](https://img.shields.io/badge/-%E5%B7%B2%E4%B8%8A%E7%BA%BF-2ea043) | `i2w ledger query` |
| 快照漂移报告 | ![已上线](https://img.shields.io/badge/-%E5%B7%B2%E4%B8%8A%E7%BA%BF-2ea043) | `i2w ledger drift` |
| Skill 技能包（7 个运行时） | ![已上线](https://img.shields.io/badge/-%E5%B7%B2%E4%B8%8A%E7%BA%BF-2ea043) | 详见 `skills/gpt-image/` |
| 基于 OCR 的评测 | ![v0.4](https://img.shields.io/badge/-v0.4-d97706) | `i2w eval run`（当前仅提示词层） |
| 多模型回退 | ![v0.4](https://img.shields.io/badge/-v0.4-d97706) | — |
| PyPI / wheel 打包 | ![v0.4](https://img.shields.io/badge/-v0.4-d97706) | — |

---

<a id="-工作流"></a>
## 🔁 工作流

<p align="center"><img src="docs/assets/hero.svg" alt="image2-workbench — 规格先行的生产工作台" width="100%" /></p>
<p align="center"><img src="docs/assets/workflow.svg" alt="image2-workbench 工作流：规格 → 编译 → 渲染 → 审计日志" width="100%" /></p>

<p align="center"><sub>同一份规格驱动三条路径 —— 网页 ChatGPT 可直接粘贴的 prompt、Images API 渲染、Batch API 扫描 —— 每次渲染都会写入一行 ledger。</sub></p>

---

<a id="-cli-命令面"></a>
## 💻 CLI 命令面

11 个动词,1 个入口（`i2w`）。按支柱分组,无需 `--help` 也能扫读。

| 分组 | 命令 | 用途 |
|---|---|---|
| 🤖 组装 | `i2w catalog` | 浏览与搜索模板 / 语料目录。 |
| 🤖 组装 | `i2w template` | 列出模板,把 YAML 规格编译成双语提示词。 |
| 🤖 组装 | `i2w render` | 在本地校验与 sidecar 协助下生成或编辑图像。 |
| 🤖 组装 | `i2w batch` | 通过 dry-run 预览构建安全的 sweep 与 Batch API 任务。 |
| 🤖 组装 | `i2w gallery` | 从模板生成可粘贴的 markdown 图册。 |
| 💰 成本 | `i2w cost` | 估算、对比、规划 Images API 花费。 |
| 🛡️ 校验 | `i2w preflight` | 在调用 API 之前就拒绝已知坏请求。 |
| 🛡️ 校验 | `i2w doctor` | 按账号 / 组织 / 模型探测运行时参数兼容性。 |
| 📊 观察 | `i2w ledger` | 查询成功率、延迟、成本、错误分布、快照漂移。 |
| 📊 观察 | `i2w eval` | 提示词层 rubric 评测（OCR 评测 V0.4 上线）。 |
| 📊 观察 | `i2w version` | 打印当前安装的 workbench 版本。 |

---

<a id="-skill-生态"></a>
## 🤖 Skill 生态

`image2-workbench` 在 [`skills/gpt-image/`](skills/gpt-image/) 提供一套可移植的 Skill 技能包,可放入任何加载 `SKILL.md` 类清单的 agent 运行时。

| 运行时 | 状态 | 清单 |
|---|---|---|
| Claude Code | ![已测试](https://img.shields.io/badge/-%E5%B7%B2%E6%B5%8B%E8%AF%95-2ea043) | [`manifests/claude.json`](skills/gpt-image/manifests/claude.json) |
| Anthropic Skills | ![已测试](https://img.shields.io/badge/-%E5%B7%B2%E6%B5%8B%E8%AF%95-2ea043) | [`manifests/claude.json`](skills/gpt-image/manifests/claude.json) |
| OpenAI Codex | ![已测试](https://img.shields.io/badge/-%E5%B7%B2%E6%B5%8B%E8%AF%95-2ea043) | [`manifests/codex.yml`](skills/gpt-image/manifests/codex.yml) |
| LangChain | ![shim 就绪](https://img.shields.io/badge/-shim%20%E5%B0%B1%E7%BB%AA-1f6feb) | [`manifests/langchain.py`](skills/gpt-image/manifests/langchain.py) |
| smolagents | ![shim 就绪](https://img.shields.io/badge/-shim%20%E5%B0%B1%E7%BB%AA-1f6feb) | [`manifests/smolagents.py`](skills/gpt-image/manifests/smolagents.py) |
| OpenClaw | ![理论支持](https://img.shields.io/badge/-%E7%90%86%E8%AE%BA%E6%94%AF%E6%8C%81-94a3b8) | [`manifests/openclaw.json`](skills/gpt-image/manifests/openclaw.json) |
| Hermes | ![理论支持](https://img.shields.io/badge/-%E7%90%86%E8%AE%BA%E6%94%AF%E6%8C%81-94a3b8) | [`manifests/hermes.yml`](skills/gpt-image/manifests/hermes.yml) |

<p><sub><a href="docs/skill-compatibility.md">完整 Skill 兼容矩阵 →</a></sub></p>

---

<a id="-常见问题"></a>
## ❓ 常见问题

<details>
<summary><strong>🤔 这跟一份精选 prompt 清单有什么不同?</strong></summary>

清单是 markdown,我们这是编译器。模板是经过 pydantic 校验的 YAML;输出可审计;同一个模板既能产出双语提示词,<em>也能</em>直接驱动 API。完整论述见 [`docs/positioning.md`](docs/positioning.md)。

</details>

<details>
<summary><strong>🤔 我必须有 OpenAI API key 吗?</strong></summary>

L3 路径不需要。`i2w template render` 会生成可直接粘贴到网页 ChatGPT 的 markdown(无需 API key)。L2 路径(`i2w render generate`)需要 `OPENAI_API_KEY` 与已通过 verification 的 org。`doctor capabilities`、`cost`、`preflight`、`template`、`gallery`、`catalog` 全部可离线运行。

</details>

<details>
<summary><strong>🤔 为什么是 30 个领域而不是"全都要"?</strong></summary>

每个领域都附带一份 `DOMAIN_CARD.md`(FOR / NOT FOR / Key axes),让相邻领域之间界限清晰。只有当我们能列出 3 条现有领域不覆盖的轴时,才会新增一个领域。今天有 30 张域卡,80 个模板分布在整张图册上。

</details>

<details>
<summary><strong>🤔 中文支持得怎么样?</strong></summary>

非常好。全部 80 个模板都支持双语渲染;demo 变量在合适的位置加入 CJK 内容。编译器是语言感知的(CJK 标点、断行、字形密度),不是简单的字符串替换。中文入门见 [`docs/getting-started.zh.md`](docs/getting-started.zh.md),英文版 README 在 [`README.md`](README.md)。

</details>

<details>
<summary><strong>🤔 安全与审核呢?</strong></summary>

`i2w preflight` 会做本地校验(尺寸、背景、质量、不支持的参数),并可选地在计费前过一遍 Moderation API。`MODERATION_BLOCKED` 有自己独立的退出码(5),CI 可以基于它做分支处理。我们不会默认 `moderation: low`;需要时再显式开启。

</details>

<details>
<summary><strong>🤔 为什么是三大支柱(成本 / 预检 / 审计日志)?</strong></summary>

工作台必须能回答 prompt 清单回答不了的三个问题:<em>"这要花多少钱?"</em>、<em>"在我付钱之前这条能跑通吗?"</em>、<em>"过去一千次跑发生了什么?"</em>。每条支柱都对应一条 CLI 命令面、一类退出码、一段 JSONL ledger。

</details>

<details>
<summary><strong>🤔 内容是怎么授权的?</strong></summary>

代码是 Apache-2.0。模板、文档、README 文件以及 Skill 的 `SKILL.md` 是 CC BY 4.0。语料记录按来源逐条声明(参见 [`source_registry.yml`](corpus/manifests/source_registry.yml))。详见下面的[许可](#-许可)章节。

</details>

---

<a id="-仓库结构"></a>
## 🗂️ 仓库结构

```
image2-workbench/
├── src/image2_workbench/    # CLI + 运行时 + 编译器 + ledger + ...
├── templates/<domain>/       # 30 个领域的 80 个规格 yaml + demo vars + DOMAIN_CARD
├── skills/gpt-image/         # SKILL.md + 7 个运行时清单
├── docs/                     # 图册、定位、成本建模等
├── corpus/                   # 来源优先的提示词记录
└── tests/                    # 1017+ 单元 + 烟雾测试
```

<p><sub><a href="AGENTS.md">仓库约定（<code>AGENTS.md</code>） →</a></sub></p>

---

<a id="-许可"></a>
## 📜 许可

| 路径 | 许可 |
|---|---|
| `src/`、`tests/`、`scripts/`、`.github/` | Apache-2.0（[LICENSE](./LICENSE)） |
| `templates/`、`docs/`、`README*`、`skills/gpt-image/SKILL.md` | CC BY 4.0（[LICENSE-CONTENT](./LICENSE-CONTENT)） |
| `corpus/normalized/*.jsonl` | 按记录逐条声明（参见 [`source_registry.yml`](./corpus/manifests/source_registry.yml)） |

完整致谢与方法论见 [`NOTICE`](NOTICE)。

---

<a id="-贡献"></a>
## 🙋 贡献

请阅读 [`AGENTS.md`](AGENTS.md) —— 文件归属、反模式（默认不要 `transparent` 背景、不要 `input_fidelity`、不要 `moderation: low` 默认值）、V1 完工定义。

安全披露 → [`SECURITY.md`](SECURITY.md)。

---

<p align="center"><a href="./README.md"><strong>English README →</strong></a></p>
