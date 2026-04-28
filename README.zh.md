<!-- SPDX-License-Identifier: CC-BY-4.0 -->

<p align="center"><a href="./README.md"><img alt="English" src="https://img.shields.io/badge/lang-English-1f6feb?style=for-the-badge"></a> &nbsp; <a href="./README.zh.md"><img alt="中文" src="https://img.shields.io/badge/%E8%AF%AD%E8%A8%80-%E4%B8%AD%E6%96%87-d4380d?style=for-the-badge"></a></p>

<h1 align="center">image2-workbench</h1>

<p align="center"><strong>给 gpt-image-2 用的可执行 prompt 工作台，不是再堆一份 prompt 清单。</strong><br/>30 个领域 · 80 条 YAML 模板 · 中英双语输出 · CLI / Skill / 网页 ChatGPT 三条路径。</p>

<p align="center"><img alt="version" src="https://img.shields.io/badge/version-v0.3.5-ea580c"> <img alt="tests" src="https://img.shields.io/badge/tests-passing-15803d"> <img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white"> <img alt="License" src="https://img.shields.io/badge/code-Apache--2.0-blue"> <img alt="Content license" src="https://img.shields.io/badge/templates%2Fdocs-CC%20BY%204.0-lightgrey"></p>

<p align="center"><a href="#快速开始"><strong>快速开始</strong></a> · <a href="#样图展示"><strong>样图展示</strong></a> · <a href="#atlas--30-domains-80-templates"><strong>模板图册</strong></a> · <a href="skills/gpt-image/"><strong>Skill 包</strong></a></p>

## 快速开始

```bash
git clone https://github.com/StartripAI/gpt-image-2.0-workbench.git
cd gpt-image-2.0-workbench
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

i2w template render business_swot_card --lang zh-CN \
  --vars templates/business/_vars_examples/swot_acme.yml \
  --out out/swot.zh.md
```

打开 `out/swot.zh.md`，把渲染好的 prompt 粘到支持图片生成的网页 ChatGPT 里，再改里面看得见的示例值。这条路径不需要 API key。

## API 路径

```bash
export OPENAI_API_KEY=sk-...

i2w preflight out/swot.zh.md --template-id business_swot_card
i2w cost compare --size 1024x1024,1536x1024 --quality low,medium,high
i2w render generate --prompt-file out/swot.zh.md \
  --template-id business_swot_card \
  --size 1536x1024 --quality medium --out out/swot.png

# 可选：查看 API / batch 跑过什么
i2w ledger query --template business_swot_card
```

## 你拿到什么

| 需求 | 用法 |
|---|---|
| 复制即用的 prompt | `i2w template render ... --out prompt.md`，然后粘到网页 ChatGPT。 |
| API 出图 | `i2w render generate`，带本地校验和 sidecar 元数据。 |
| 成本控制 | `i2w cost compare`、`i2w cost estimate`、`i2w batch sweep --dry-run`。 |
| 请求校验 | `i2w preflight` 在花钱前拦掉 gpt-image-2 不支持的参数。 |
| 本地运行历史 | `i2w ledger` 从 JSONL 汇总 render / preflight / batch 记录。 |
| Agent 使用 | 把 `skills/gpt-image/` 放进 Codex、Claude Code 或其他 Skill 运行时。 |

当前扩展图册是 **30 个领域 / 80 条可执行 YAML 模板**。最早的 V1 core 仍然是 `business`、`academic`、`uiux`、`anime`；扩展图册继续覆盖 product、ecommerce、advertising、social_media、photography、fashion、food、architecture、interior、travel 等领域。

## 样图展示 — 30 个领域

下面每张都是一个领域的代表渲染。点进领域图册可以直接复制中英双语 prompt；点进模板目录可以改 YAML 源模板。

<p align="center"><strong>按分类看：</strong> <a href="docs/gallery/business.md">business</a> · <a href="docs/gallery/academic.md">academic</a> · <a href="docs/gallery/uiux.md">uiux</a> · <a href="docs/gallery/anime.md">anime</a> · <a href="docs/gallery/ecommerce.md">ecommerce</a> · <a href="docs/gallery/product.md">product</a> · <a href="docs/gallery/advertising.md">advertising</a> · <a href="docs/gallery/social_media.md">social_media</a> · <a href="docs/gallery/gaming.md">gaming</a> · <a href="docs/gallery/photography.md">photography</a> · <a href="docs/gallery/fashion.md">fashion</a> · <a href="docs/gallery/food.md">food</a> · <a href="docs/gallery/architecture.md">architecture</a> · <a href="docs/gallery/interior.md">interior</a> · <a href="docs/gallery/industrial.md">industrial</a> · <a href="docs/gallery/infographic_data.md">infographic_data</a> · <a href="docs/gallery/travel.md">travel</a> · <a href="docs/gallery/typography.md">typography</a> · <a href="docs/gallery/beauty.md">beauty</a> · <a href="docs/gallery/events.md">events</a> · <a href="docs/gallery/tattoo.md">tattoo</a> · <a href="docs/gallery/watercolor_illustration.md">watercolor_illustration</a> · <a href="docs/gallery/isometric_illustration.md">isometric_illustration</a> · <a href="docs/gallery/comic_book.md">comic_book</a> · <a href="docs/gallery/music.md">music</a> · <a href="docs/gallery/science_fiction_concept.md">science_fiction_concept</a> · <a href="docs/gallery/kids_illustration.md">kids_illustration</a> · <a href="docs/gallery/automotive.md">automotive</a> · <a href="docs/gallery/pet.md">pet</a> · <a href="docs/gallery/streetwear.md">streetwear</a></p>

### business

<p align="center"><a href="docs/gallery/business.md"><img src="docs/assets/showcase-business.webp" alt="business showcase" width="100%"/></a></p>

面向真实商务交付的画面：SWOT 卡、融资 pitch、数据看板、LinkedIn 轮播封面。适合做进团队汇报、管理层更新和客户提案。 [图册](docs/gallery/business.md) · [模板](templates/business/)

### academic

<p align="center"><a href="docs/gallery/academic.md"><img src="docs/assets/showcase-academic.webp" alt="academic showcase" width="100%"/></a></p>

学术和教育场景的高密度文字视觉：黑板证明、会议海报、多语言教学海报、带标签的科学图解。 [图册](docs/gallery/academic.md) · [模板](templates/academic/)

### uiux

<p align="center"><a href="docs/gallery/uiux.md"><img src="docs/assets/showcase-uiux.webp" alt="uiux showcase" width="100%"/></a></p>

产品设计展示面：iOS mockup、Web dashboard、design-system card、社媒教程封面。重点是界面可信、层级清楚、可直接用于方案讲解。 [图册](docs/gallery/uiux.md) · [模板](templates/uiux/)

### anime

<p align="center"><a href="docs/gallery/anime.md"><img src="docs/assets/showcase-anime.webp" alt="anime showcase" width="100%"/></a></p>

偏二次元原生的图像格式：角色设定表、城市海报、8 格漫画、CCD 风格抓拍。模板会强调角色一致性、姿态控制和画面内文字可读性。 [图册](docs/gallery/anime.md) · [模板](templates/anime/)

### ecommerce

<p align="center"><a href="docs/gallery/ecommerce.md"><img src="docs/assets/showcase-ecommerce.webp" alt="ecommerce showcase" width="100%"/></a></p>

电商转化用图：marketplace card、商品主图、分类 banner，预留标题、卖点和 CTA 空间，让用户快速看懂商品。 [图册](docs/gallery/ecommerce.md) · [模板](templates/ecommerce/)

### product

<p align="center"><a href="docs/gallery/product.md"><img src="docs/assets/showcase-product.webp" alt="product showcase" width="100%"/></a></p>

产品说明板：包装概念、功能 callout、横向对比板。适合同时保留物体本身和卖点信息的可读性。 [图册](docs/gallery/product.md) · [模板](templates/product/)

### advertising

<p align="center"><a href="docs/gallery/advertising.md"><img src="docs/assets/showcase-advertising.webp" alt="advertising showcase" width="100%"/></a></p>

广告战役画面：campaign key visual、户外 billboard mockup、三帧 storyboard。重点是视觉钩子、品牌可读性和清晰的商业信息。 [图册](docs/gallery/advertising.md) · [模板](templates/advertising/)

### social_media

<p align="center"><a href="docs/gallery/social_media.md"><img src="docs/assets/showcase-social_media.webp" alt="social media showcase" width="100%"/></a></p>

社媒发布资产：launch post、竖版 story sequence、thumbnail grid。模板会把小屏浏览时最重要的信息放在清楚的位置。 [图册](docs/gallery/social_media.md) · [模板](templates/social_media/)

### gaming

<p align="center"><a href="docs/gallery/gaming.md"><img src="docs/assets/showcase-gaming.webp" alt="gaming showcase" width="100%"/></a></p>

游戏 UI 和世界观展示：HUD mockup、道具卡、任务地图面板。目标是看起来像能被玩家理解和操作的界面。 [图册](docs/gallery/gaming.md) · [模板](templates/gaming/)

### photography

<p align="center"><a href="docs/gallery/photography.md"><img src="docs/assets/showcase-photography.webp" alt="photography showcase" width="100%"/></a></p>

摄影感画面：editorial portrait、cinematic still、documentary scene。prompt 会明确镜头语言、光线、构图和可信的主体语境。 [图册](docs/gallery/photography.md) · [模板](templates/photography/)

### fashion

<p align="center"><a href="docs/gallery/fashion.md"><img src="docs/assets/showcase-fashion.webp" alt="fashion showcase" width="100%"/></a></p>

时装编辑格式：lookbook page、flatlay board、runway poster。用来保留穿搭、材质、廓形和造型线索。 [图册](docs/gallery/fashion.md) · [模板](templates/fashion/)

### food

<p align="center"><a href="docs/gallery/food.md"><img src="docs/assets/showcase-food.webp" alt="food showcase" width="100%"/></a></p>

餐饮和食品包装资产：菜单海报、食谱卡、包装标签。模板会为菜名、价格、成分和品牌信息留出版面。 [图册](docs/gallery/food.md) · [模板](templates/food/)

### architecture

<p align="center"><a href="docs/gallery/architecture.md"><img src="docs/assets/showcase-architecture.webp" alt="architecture showcase" width="100%"/></a></p>

建筑表达图：立面概念、site diagram、presentation board。适合既要空间氛围、又要保留图解清晰度的场景。 [图册](docs/gallery/architecture.md) · [模板](templates/architecture/)

### interior

<p align="center"><a href="docs/gallery/interior.md"><img src="docs/assets/showcase-interior.webp" alt="interior showcase" width="100%"/></a></p>

室内设计表达：room mockup、material board、before/after renovation edit。模板会保护家具、材质和标签区域。 [图册](docs/gallery/interior.md) · [模板](templates/interior/)

### industrial

<p align="center"><a href="docs/gallery/industrial.md"><img src="docs/assets/showcase-industrial.webp" alt="industrial showcase" width="100%"/></a></p>

工业说明和安全传播：cutaway view、process diagram、factory safety poster。适合把复杂设备或流程讲清楚。 [图册](docs/gallery/industrial.md) · [模板](templates/industrial/)

### infographic_data

<p align="center"><a href="docs/gallery/infographic_data.md"><img src="docs/assets/showcase-infographic_data.webp" alt="infographic data showcase" width="100%"/></a></p>

数据密集型信息图：chart explainer、editorial dashboard。适合把一个量化故事压缩成可扫读的一屏。 [图册](docs/gallery/infographic_data.md) · [模板](templates/infographic_data/)

### travel

<p align="center"><a href="docs/gallery/travel.md"><img src="docs/assets/showcase-travel.webp" alt="travel showcase" width="100%"/></a></p>

旅行传播资产：目的地海报、itinerary card、地图指南。重点是地点气质、路线信息和版面导航。 [图册](docs/gallery/travel.md) · [模板](templates/travel/)

### typography

<p align="center"><a href="docs/gallery/typography.md"><img src="docs/assets/showcase-typography.webp" alt="typography showcase" width="100%"/></a></p>

文字本身作为主角的生成：lettering art、type specimen poster。适合需要字体、字形和排版成为画面核心的时候。 [图册](docs/gallery/typography.md) · [模板](templates/typography/)

### beauty

<p align="center"><a href="docs/gallery/beauty.md"><img src="docs/assets/showcase-beauty.webp" alt="beauty showcase" width="100%"/></a></p>

美妆和护肤视觉：skincare packaging、beauty editorial layout。模板会给小字功效、产品 callout 和高级材质留空间。 [图册](docs/gallery/beauty.md) · [模板](templates/beauty/)

### events

<p align="center"><a href="docs/gallery/events.md"><img src="docs/assets/showcase-events.webp" alt="events showcase" width="100%"/></a></p>

活动类设计：演出海报、音乐节视觉、婚礼邀请函。重点是日期、地点、阵容和气氛层级。 [图册](docs/gallery/events.md) · [模板](templates/events/)

### tattoo

<p align="center"><a href="docs/gallery/tattoo.md"><img src="docs/assets/showcase-tattoo.webp" alt="tattoo showcase" width="100%"/></a></p>

纹身设计板：flash sheet、minimal standalone design。prompt 会强调干净轮廓、可复用 motif 和纹身师可参考的结构。 [图册](docs/gallery/tattoo.md) · [模板](templates/tattoo/)

### watercolor_illustration

<p align="center"><a href="docs/gallery/watercolor_illustration.md"><img src="docs/assets/showcase-watercolor_illustration.webp" alt="watercolor illustration showcase" width="100%"/></a></p>

水彩插画格式：植物研究、柔和角色肖像。模板偏纸张纹理、透明叠色和克制标签。 [图册](docs/gallery/watercolor_illustration.md) · [模板](templates/watercolor_illustration/)

### isometric_illustration

<p align="center"><a href="docs/gallery/isometric_illustration.md"><img src="docs/assets/showcase-isometric_illustration.webp" alt="isometric illustration showcase" width="100%"/></a></p>

等距插画场景：城市街区、workspace scene。适合需要固定投影、结构清楚的空间叙事。 [图册](docs/gallery/isometric_illustration.md) · [模板](templates/isometric_illustration/)

### comic_book

<p align="center"><a href="docs/gallery/comic_book.md"><img src="docs/assets/showcase-comic_book.webp" alt="comic book showcase" width="100%"/></a></p>

漫画书页面：panel page、variant cover。模板会指定分格、 gutter、对白气泡和封面层级。 [图册](docs/gallery/comic_book.md) · [模板](templates/comic_book/)

### music

<p align="center"><a href="docs/gallery/music.md"><img src="docs/assets/showcase-music.webp" alt="music showcase" width="100%"/></a></p>

音乐视觉：album cover、concert poster。模板平衡艺人识别、活动信息和强中心视觉 motif。 [图册](docs/gallery/music.md) · [模板](templates/music/)

### science_fiction_concept

<p align="center"><a href="docs/gallery/science_fiction_concept.md"><img src="docs/assets/showcase-science_fiction_concept.webp" alt="science fiction concept showcase" width="100%"/></a></p>

科幻概念图：cinematic keyframe、vehicle hero concept。适合做氛围、尺度和 speculative design language。 [图册](docs/gallery/science_fiction_concept.md) · [模板](templates/science_fiction_concept/)

### kids_illustration

<p align="center"><a href="docs/gallery/kids_illustration.md"><img src="docs/assets/showcase-kids_illustration.webp" alt="kids illustration showcase" width="100%"/></a></p>

儿童插画格式：storybook spread、workbook page。prompt 会保持友好、清楚，并围绕简单故事或学习目标组织画面。 [图册](docs/gallery/kids_illustration.md) · [模板](templates/kids_illustration/)

### automotive

<p align="center"><a href="docs/gallery/automotive.md"><img src="docs/assets/showcase-automotive.webp" alt="automotive showcase" width="100%"/></a></p>

汽车营销画面：hero ad、dealership poster。模板会给车型识别、价格、金融方案或 campaign copy 留出干净空间。 [图册](docs/gallery/automotive.md) · [模板](templates/automotive/)

### pet

<p align="center"><a href="docs/gallery/pet.md"><img src="docs/assets/showcase-pet.webp" alt="pet showcase" width="100%"/></a></p>

宠物相关设计：领养传单、宠物食品包装。模板会让动物是中心，同时保留联系方式或包装信息。 [图册](docs/gallery/pet.md) · [模板](templates/pet/)

### streetwear

<p align="center"><a href="docs/gallery/streetwear.md"><img src="docs/assets/showcase-streetwear.webp" alt="streetwear showcase" width="100%"/></a></p>

街头服饰发布视觉：drop lookbook、sneaker hero plate。重点是廓形、发售日期、系列名和零售氛围。 [图册](docs/gallery/streetwear.md) · [模板](templates/streetwear/)

<!-- BEGIN GALLERY (auto-generated by `i2w gallery readme`; do not edit by hand) -->

<a id="atlas--30-domains-80-templates"></a>
## 模板图册 — 30 个领域，80 个模板

当前扩展图册覆盖 30 个领域；每个领域都有一页可复制的双语 prompt gallery，也能从同一份 YAML 模板走 CLI / Skill / API。

| 领域 | 模板数 | 适合做什么 | 代表模板 | 入口 |
|---|---:|---|---|---|
| 🎓 `academic` | 4 | Photorealistic university chalkboard with a four-step mathematical proof and QED line. | `academic_chalkboard_proof` · `academic_journal_poster` | <a href="docs/gallery/academic.md">图册</a> · <a href="templates/academic/">模板</a> |
| 📢 `advertising` | 3 | Photoreal urban billboard mockup with the hero ad pasted on a real-feeling outdoor placem… | `advertising_billboard_mockup` · `advertising_campaign_key_visual` | <a href="docs/gallery/advertising.md">图册</a> · <a href="templates/advertising/">模板</a> |
| 🎌 `anime` | 4 | 复古 CCD 相机风格自拍 / Vintage CCD camera-style candid (a non-photoreal staged "authenticity"). | `anime_ccd_candid` · `anime_character_sheet` | <a href="docs/gallery/anime.md">图册</a> · <a href="templates/anime/">模板</a> |
| 🏛️ `architecture` | 3 | Conceptual exterior facade rendering for an architecture studio's project poster. | `architecture_facade_concept` · `architecture_presentation_board` | <a href="docs/gallery/architecture.md">图册</a> · <a href="templates/architecture/">模板</a> |
| 🚗 `automotive` | 2 | Point-of-sale dealership poster — vehicle hero plus price, financing terms, and dealer na… | `automotive_dealership_poster` · `automotive_hero_ad` | <a href="docs/gallery/automotive.md">图册</a> · <a href="templates/automotive/">模板</a> |
| 💄 `beauty` | 2 | Magazine-style beauty editorial spread — close-up beauty shot with small product callouts. | `beauty_editorial_layout` · `beauty_skincare_packaging` | <a href="docs/gallery/beauty.md">图册</a> · <a href="templates/beauty/">模板</a> |
| 📊 `business` | 4 | Light-theme analytics dashboard mockup with KPI tiles and two illustrative charts. | `business_data_dashboard` · `business_linkedin_carousel` | <a href="docs/gallery/business.md">图册</a> · <a href="templates/business/">模板</a> |
| 💥 `comic_book` | 2 | Multi-panel American comic-book interior page with speech balloons, halftone shading, and… | `comic_book_panel_page` · `comic_book_variant_cover` | <a href="docs/gallery/comic_book.md">图册</a> · <a href="templates/comic_book/">模板</a> |
| 🛍️ `ecommerce` | 3 | Wide 16:9 storefront category banner with a row of product silhouettes, headline, sub-tex… | `ecommerce_category_banner` · `ecommerce_marketplace_card` | <a href="docs/gallery/ecommerce.md">图册</a> · <a href="templates/ecommerce/">模板</a> |
| 🎫 `events` | 2 | Vertical concert / festival poster with headliner, support, date, and venue. | `events_concert_poster` · `events_wedding_invite` | <a href="docs/gallery/events.md">图册</a> · <a href="templates/events/">模板</a> |
| 👗 `fashion` | 3 | Styled flatlay of garments and accessories arranged on a surface for editorial use. | `fashion_flatlay_board` · `fashion_lookbook_page` | <a href="docs/gallery/fashion.md">图册</a> · <a href="templates/fashion/">模板</a> |
| 🍽️ `food` | 3 | Vertical restaurant menu wall poster — categorized dish list with prices and accent. | `food_menu_poster` · `food_packaging_label` | <a href="docs/gallery/food.md">图册</a> · <a href="templates/food/">模板</a> |
| 🎮 `gaming` | 3 | Fictional video-game HUD mockup with health and mana bars, minimap, mission objective ove… | `gaming_hud_mockup` · `gaming_item_card` | <a href="docs/gallery/gaming.md">图册</a> · <a href="templates/gaming/">模板</a> |
| 🏭 `industrial` | 3 | Isometric cutaway / exploded view of an industrial machine with four labeled internal com… | `industrial_cutaway_view` · `industrial_process_diagram` | <a href="docs/gallery/industrial.md">图册</a> · <a href="templates/industrial/">模板</a> |
| 📈 `infographic_data` | 2 | Single-chart explainer panel — large hero chart annotated with three pull-out callouts an… | `infographic_data_chart_explainer` · `infographic_data_dashboard` | <a href="docs/gallery/infographic_data.md">图册</a> · <a href="templates/infographic_data/">模板</a> |
| 🛋️ `interior` | 3 | Split-screen interior before/after edit; left panel preserves the original, right panel s… | `interior_before_after` · `interior_material_board` | <a href="docs/gallery/interior.md">图册</a> · <a href="templates/interior/">模板</a> |
| 🧊 `isometric_illustration` | 2 | True-isometric city block with named buildings, tiny vehicles, and street trees, projecte… | `isometric_city_block` · `isometric_workspace_scene` | <a href="docs/gallery/isometric_illustration.md">图册</a> · <a href="templates/isometric_illustration/">模板</a> |
| 🧸 `kids_illustration` | 2 | Two-page children's storybook spread with friendly cast, narration band, and a single dia… | `kids_illustration_storybook_spread` · `kids_illustration_workbook_page` | <a href="docs/gallery/kids_illustration.md">图册</a> · <a href="templates/kids_illustration/">模板</a> |
| 🎵 `music` | 2 | Square album-cover artwork — single hero visual identity with artist and album metadata. | `music_album_cover` · `music_concert_poster` | <a href="docs/gallery/music.md">图册</a> · <a href="templates/music/">模板</a> |
| 🐾 `pet` | 2 | Single-animal adoption flyer — companion-animal photo with name, age, key trait, and shel… | `pet_adoption_flyer` · `pet_food_packaging` | <a href="docs/gallery/pet.md">图册</a> · <a href="templates/pet/">模板</a> |
| 📷 `photography` | 3 | Film-frame still — anamorphic cinematic look capturing a single narrative beat. | `photography_cinematic_still` · `photography_documentary_scene` | <a href="docs/gallery/photography.md">图册</a> · <a href="templates/photography/">模板</a> |
| 📦 `product` | 3 | Vertical 4:5 side-by-side comparison of three product variants with feature checkboxes by… | `product_comparison_board` · `product_feature_callout` | <a href="docs/gallery/product.md">图册</a> · <a href="templates/product/">模板</a> |
| 🚀 `science_fiction_concept` | 2 | Cinematic sci-fi keyframe matte painting — alien landscape or far-future urban scene with… | `science_fiction_concept_keyframe` · `science_fiction_concept_vehicle_hero` | <a href="docs/gallery/science_fiction_concept.md">图册</a> · <a href="templates/science_fiction_concept/">模板</a> |
| 🗯️ `social_media` | 3 | 1:1 feed-friendly Instagram or X launch announcement post for a new product, with date an… | `social_media_launch_post` · `social_media_story_sequence` | <a href="docs/gallery/social_media.md">图册</a> · <a href="templates/social_media/">模板</a> |
| 👟 `streetwear` | 2 | Drop-announcement lookbook plate — single street look with drop date and collection name. | `streetwear_lookbook_drop` · `streetwear_sneaker_hero` | <a href="docs/gallery/streetwear.md">图册</a> · <a href="templates/streetwear/">模板</a> |
| 🪡 `tattoo` | 2 | Traditional tattoo flash sheet — multiple design vignettes on aged paper. | `tattoo_flash_sheet` · `tattoo_minimal_design` | <a href="docs/gallery/tattoo.md">图册</a> · <a href="templates/tattoo/">模板</a> |
| ✈️ `travel` | 3 | Vintage-style travel poster for a fictional or generic destination, with name, tagline, a… | `travel_destination_poster` · `travel_itinerary_card` | <a href="docs/gallery/travel.md">图册</a> · <a href="templates/travel/">模板</a> |
| 🔤 `typography` | 2 | Hand-lettered art piece — a single phrase rendered as the visual subject. | `typography_lettering_art` · `typography_specimen_poster` | <a href="docs/gallery/typography.md">图册</a> · <a href="templates/typography/">模板</a> |
| 📱 `uiux` | 4 | Square design-system showcase card highlighting a single component or token with prop row… | `uiux_design_system_card` · `uiux_ios_app_mockup` | <a href="docs/gallery/uiux.md">图册</a> · <a href="templates/uiux/">模板</a> |
| 🎨 `watercolor_illustration` | 2 | Single-specimen botanical watercolor study with latin caption, in transparent washes on v… | `watercolor_botanical_study` · `watercolor_character_portrait` | <a href="docs/gallery/watercolor_illustration.md">图册</a> · <a href="templates/watercolor_illustration/">模板</a> |

<p><strong>继续看：</strong> <a href="docs/getting-started.zh.md">快速上手</a> · <a href="docs/chatgpt-web-mode.md">网页 ChatGPT 用法</a> · <a href="docs/cost-modeling.md">成本模型</a></p>

<!-- END GALLERY -->

## 工作流

<p align="center"><img src="docs/assets/workflow.svg" alt="image2-workbench 工作流：模板到 prompt 到出图到可选 ledger" width="100%" /></p>

一份 YAML 模板可以走三种表面：

| 表面 | 什么时候用 | 入口 |
|---|---|---|
| Skill | 想让 agent 选模板并执行流程。 | `skills/gpt-image/SKILL.md` |
| CLI / SDK | 想要可复现出图、校验、成本估算、batch payload 和产物。 | `i2w template`、`i2w render`、`i2w batch` |
| Prompt-only | 想要能直接粘到网页 ChatGPT 的 prompt。 | `docs/gallery/*.md` 或 `i2w template render` |

## CLI 命令面

`i2w --help` 暴露 11 个顶层命令：

| 分组 | 命令 |
|---|---|
| 找模板和组装 | `catalog`、`template`、`gallery` |
| 出图和批量 | `render`、`batch` |
| 预算和校验 | `cost`、`preflight`、`doctor` |
| 检查结果 | `ledger`、`eval`、`version` |

Ledger 默认只写本地 `$IMAGE2_LEDGER_PATH` 或 `~/.image2/ledger.jsonl`。它对 API 或 batch 用户有用，但 prompt-only 路径完全不依赖它。

## 文档

- [快速上手](docs/getting-started.zh.md)
- [在网页 ChatGPT 里使用 image2-workbench](docs/chatgpt-web-mode.md)
- [Prompt craft](docs/prompt-craft.md)
- [成本模型](docs/cost-modeling.md)
- [错误码](docs/error-codes.md)
- [Skill 兼容矩阵](docs/skill-compatibility.md)
- [图册索引](docs/gallery/index.md)

## 常见问题

**需要 API key 吗？**
Prompt-only 路径不需要。`i2w template render` 和生成好的 gallery 页面会产出可粘贴的 markdown。`i2w render generate` 和真实 Batch API 提交需要 `OPENAI_API_KEY`。

**为什么用 YAML，不直接写 prompt？**
模板 DSL 把主体、动作、场景、构图、风格、文字块、保留规则和负面约束分开。这样更容易校验、翻译、测试和复用。

**是不是复制了别的 prompt gallery？**
不是。本仓库的模板、文档和 gallery 页面是这个 workbench 的原创内容。外部 prompt collection 可以参考结构，但不要把它们的 prompt 文本或 README 文案复制进来。

**`ledger` 是必须的吗？**
不是。它只是 CLI 跑图时写在本地的 JSONL 历史，适合看成本、失败模板和 snapshot drift。只浏览或复制 prompt 的用户不用管它。

## 仓库结构

```text
src/image2_workbench/     # CLI、runtime、compiler、catalog、costing、ledger
templates/                # 30 个领域，80 条可执行 YAML 模板
docs/gallery/             # 生成出来的双语 prompt gallery
docs/assets/              # 样图和 README 图示
skills/gpt-image/         # 可移植 Skill 包
tests/                    # unit、smoke 和 golden-adjacent 检查
```

## 许可

代码使用 Apache-2.0。模板、文档、README、gallery 页面和展示用 prompt 文本使用 CC BY 4.0。详见 [LICENSE](LICENSE)、[LICENSE-CONTENT](LICENSE-CONTENT)、[LICENSE-CC-BY-4.0](LICENSE-CC-BY-4.0)、[NOTICE](NOTICE) 和 [docs/licensing.md](docs/licensing.md)。

## 贡献

改共享表面前先读 [AGENTS.md](AGENTS.md)。几个重要规则：不要把 `input_fidelity` 传给 gpt-image-2，不要用 `background: transparent`，不要默认把 moderation 设成 `low`，新增 runtime 依赖时必须同步更新 `pyproject.toml` 和 PR 说明。
