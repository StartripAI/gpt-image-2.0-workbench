<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# image2-workbench v0.3 — Handoff

This is the agent-to-agent handoff packet that ships with the v0.3 cut of
`image2-workbench`. Everything you need to bring the GitHub-facing first
fold up to ship-quality is contained in this document.

---

## 1. What this hand-off contains

The v0.3 codebase is **complete except for twelve showcase webp images**.
Tags `v0.2.0` is on the trunk. The atlas runs to **16 domains and 52
templates**, every one of which loads through the compiler, renders
bilingually, and survives the gpt-image-2 hard-constraint validators.
The atlas has been injected into both `README.md` and `README.zh.md` via
`i2w gallery readme --inject` and the section is regression-locked by
`tests/unit/test_atlas_v03.py`. CI is green at **803 tests passing**.

Three SVG assets — `docs/assets/hero.svg`, `docs/assets/workflow.svg`,
`docs/assets/production-controls.svg` — are already on disk and serve as
**text-deterministic placeholders** for the README first fold. They are
hand-authored SVG, viewBox-correct, accessible (`<title>` + `<desc>`),
and will not drift across model versions. You can keep them as-is or
re-render them via gpt-image-2 using the prompts in §3.

What is **not yet on disk** is the `docs/assets/showcase-<domain>.webp`
strip — twelve 1536×1024 bitmaps that the README atlas section already
references. Codex will render those bitmaps using the prompts in §2,
drop the files into `docs/assets/`, run the verification suite below,
and tag `v0.3.1`. Once the twelve webps land, the GitHub README first
fold becomes visually rich (twelve domain-evocative cards in a 4×3
grid) and the project graduates from text-only-with-placeholders to
**spec-first AND visually argumentative**.

The twelve prompts below are written for direct submission to the
gpt-image-2 endpoint with no editing. Each prompt names a bitmap output
target (`docs/assets/showcase-<domain>.webp`), an exact size (`1536x1024`,
i.e. 16:9), a quality recommendation (`medium` for the first pass,
`high` once you are happy with the framing), and explicit lists for the
preserve / negative axes. Each is anchored on the corresponding
`templates/<domain>/DOMAIN_CARD.md` so the visual reads as a faithful
cover for the domain.

---

## 2. Twelve showcase webp prompts

Each prompt follows the V1.5 prompt spec: literal text inside `""`
double quotes, explicit composition guidance, an explicit forbidden
list, and a preserve list (empty for fresh renders). Sizes are fixed at
`1536x1024` (16:9) so the cards line up cleanly in the README four-column
grid. Submit each prompt through whichever interface Codex prefers —
the `images.generate` API directly, or `i2w render generate` once the
template is wrapped, or the ChatGPT image-tool. The text inside the
prompt block is the only payload the model needs.

### Showcase 1 — business

Save to: `docs/assets/showcase-business.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A polished editorial business intelligence cover image rendered at
> 16:9 (1536×1024). Centered composition: a single large flat
> infographic card occupies roughly 70 percent of the frame, framed
> against a soft warm-grey paper field with subtle paper grain. The
> card itself is a four-quadrant SWOT analysis matrix with a slim
> header band reading "STRATEGY BRIEF — Q4 FY2026" in compact display
> caps. Each quadrant carries a quiet category icon top-left, a
> small-caps label ("Strengths" / "Weaknesses" / "Opportunities" /
> "Threats"), and three short typeset bullets in a humanist sans body
> face. To the right of the card, a smaller secondary panel carries a
> minimalist line chart trending up. Editorial corporate aesthetic:
> palette anchored on deep navy, slate, cool fog grey, and a single
> muted oxidized-teal accent. No drop shadows beyond hairline rules;
> no gradients; no glow. Studio-flat document-grade environment,
> calibrated for both print and on-screen legibility. The cover should
> read in 1.5 seconds as "executive boardroom briefing material."

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-brand logos, no specific
recognizable people, no stock-photo executives, no rainbow palette,
no glassmorphism, no 3D rendering, no clip-art icons.

---

### Showcase 2 — academic

Save to: `docs/assets/showcase-academic.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A museum-grade scientific illustration cover rendered at 16:9
> (1536×1024). Aged cream paper substrate with subtle deckle edges and
> gentle foxing at the corners — the paper itself is the world. A
> single hero specimen sits centered at roughly 55 percent of frame
> width: a hand-drawn cross-section of an ammonite fossil rendered in
> sepia ink linework over soft watercolor washes (warm ivory, umber,
> ochre, slate, muted viridian). Five thin leader lines fan from the
> specimen to small filled circles beside lightweight humanist
> sans-serif labels: "aperture", "septum", "siphuncle", "umbilicus",
> "growth lines". Across the top, a slim title band sets "FIELD GUIDE
> — INVERTEBRATA" in a confident display sans. Beneath the specimen, a
> small caption plate reads "Plate IV — Mesozoic Cretaceous". Margins
> are at least 6 percent, leader lines never cross, internal
> whitespace is generous. The cover should read as a 19th-century
> natural-history monograph reissued for a modern classroom wall.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-museum logos, no real
researcher names, no busy ornamentation, no neon, no photorealistic
texture, no franchise IP, no rainbow palette.

---

### Showcase 3 — uiux

Save to: `docs/assets/showcase-uiux.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A pixel-perfect B2B SaaS analytics dashboard mockup rendered at 16:9
> (1536×1024) as if captured from a desktop viewport. Pure on-screen
> field — no browser chrome, no OS window controls, no wallpaper.
> Background is a soft off-white SaaS surface (#F7F8FA). Layout: left
> rail at about 14 percent width carrying a wordmark "Lumen" up top
> and five vertical nav rows ("Overview", "Pipeline", "Cohorts",
> "Reports", "Settings") each with a tiny leading icon. Above the
> content area, a 64-pixel-tall header strip holds the title "Pipeline
> health" at left and a date-range pill "Last 30 days" at right. Below
> the header, three KPI cards span the row with 24px gutters: "MRR",
> "Active accounts", "Net retention", each with a number and a small
> green delta arrow. Below the KPI row, a single hero chart panel
> occupies about 45 percent of vertical space showing a clean
> emerald-accented line chart. A compact data table pins the bottom.
> Clean Linear / Vercel / Tailwind UI cut. White cards on off-white,
> 1-pixel slate-200 hairline borders, 12-pixel corner radius, Inter
> typography, single emerald accent.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-brand logos (no Linear, no
Stripe, no Vercel marks), no glassmorphism, no drop shadows beyond
hairlines, no neon gradients, no fake browser chrome, no real
customer names.

---

### Showcase 4 — anime

Save to: `docs/assets/showcase-anime.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A clean concept-art character reference sheet rendered at 16:9
> (1536×1024) on a pure white reference-sheet ground (#FFFFFF). A
> three-quarter front-view illustration of an original anime/manga
> character occupies the left two-thirds: a young scout-archetype
> figure named "Kiri" with a long teal coat, bandolier of small
> brass-rimmed lenses, and a windswept silver braid. Confident
> anime/manga line art with subtle two-tone cel shading and faint
> low-opacity pencil construction lines visible underneath; ink-and-
> pencil feel. The right one-third holds a small "Expressions" header
> over four headshots in a horizontal strip — neutral, smiling,
> alert, downcast — and beneath it a thin palette swatch row labeled
> "Palette: dusk-teal / brass / paper". A slim banner across the very
> top sets the character name "KIRI — scout, world: Driftshore". No
> environment, no cast shadows beyond a subtle ground-contact tone,
> faint horizontal pencil rules at very low contrast for scale. Clean
> reference-sheet aesthetic, moderate palette, no neon.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-celebrity likeness, no
copyrighted franchise IP (no Studio Ghibli, no Pokémon, no Genshin),
no photorealistic skin, no busy environment background, no dynamic
action pose, no lens flare, no rainbow palette, no 3D-rendered look.

---

### Showcase 5 — ecommerce

Save to: `docs/assets/showcase-ecommerce.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A premium D2C product detail page hero rendered at 16:9 (1536×1024).
> Composition is split: the left 60 percent is a flat warm off-white
> brand field carrying a single SKU in stage-lit isolation — a
> matte-ceramic aroma diffuser in soft sage, photographed slightly
> above the centerline with a subtle ground contact tone, no other
> props. The right 40 percent is a slim conversion column on a softer
> graduated palette wash: a generous product title "Mira Diffuser",
> a one-line caption "Hand-glazed stoneware · 250 ml capacity", a
> price chip reading "$58", a small trust badge "Free shipping over
> $50", and a single solid-fill primary CTA button reading "Add to
> bag". A second tiny disclosure below the CTA reads "30-day returns".
> Restrained sales-driven aesthetic — calm marketing-grade
> photography, single-product focus, conversion elements clearly
> hierarchical (title > price > CTA). Use a fictional brand wordmark.
> The cover should read as the "Buy" page of an indie luxury home
> brand on a desktop viewport.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-brand marks (no Apple, no
Aesop, no Muji), no human models, no busy lifestyle context, no
stock-photo backdrops, no flame or smoke effects, no recognizable
storefront.

---

### Showcase 6 — industrial

Save to: `docs/assets/showcase-industrial.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A line-side industrial process diagram rendered at 16:9 (1536×1024).
> Slate-grey background field with very subtle perforated-panel
> texture. A horizontal four-stage process flow runs left-to-right
> across the middle band: each stage is a flat rectangular module in
> brushed-steel grey with a single safety-orange step number, a
> small isometric schematic glyph (raw-material intake → processing
> chamber → inspection station → packaging), and a short label set
> in clean sans caps ("INTAKE", "PROCESS", "INSPECT", "PACK").
> Slate-orange directional arrows connect the modules. Across the
> top, a strict masthead reads "STAMPING LINE 04 — STANDARD OPERATING
> FLOW" in a heavy industrial sans. A footer band carries small
> pictogram safety glyphs (helmet, gloves, ear protection) and a
> single-line caption "PPE required beyond this point — see SOP-117".
> Restrained color discipline: slate grey, safety orange, a single
> hairline of signal red on critical callouts. Sign-grade pictograms,
> service-manual register, no photorealism, no people. The cover
> should read as a manufacturing-floor wall poster.

Preserve list: (none — fresh render)
Negative list: no watermarks, no OSHA logo, no real-corporate
manufacturer marks, no human operators, no stock photography of
factories, no rust or grime, no neon, no rainbow palette, no 3D
rendering.

---

### Showcase 7 — advertising

Save to: `docs/assets/showcase-advertising.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A premium agency-grade brand campaign key visual rendered at 16:9
> (1536×1024). Cinematic editorial photography aesthetic with
> disciplined OOH-safe typography. Hero composition: a single
> conceptual product hero — a fictional pour-over coffee carafe —
> sits slightly off-center on a deep oxblood seamless backdrop, lit
> from camera-left with a soft key and a tighter rim from behind that
> outlines the glass; the carafe glows from within like a small
> lantern. Restrained palette of oxblood, warm amber, and graphite.
> Across the top right, a confident two-line tagline reads "MORNING /
> ON PURPOSE" in a clean modern grotesk. Beneath the carafe, a
> compact product line "Aurel — slow-pour, one cup" sits at small-cap
> body weight. Bottom-left carries a discreet fictional brandmark
> "Aurel" and a hairline-thin URL "aurel.coffee". OOH typography
> hierarchy reads in 1.5 seconds: tagline > product > brand. No
> garnish, no human hand. Photoreal lighting, single-image concept
> suitable for a billboard placement review.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-coffee brand logos (no
Starbucks, no Blue Bottle, no Lavazza), no celebrity faces, no
recognizable cities or storefronts, no photographed people, no neon,
no rainbow gradients, no 3D-CG plasticness.

---

### Showcase 8 — gaming

Save to: `docs/assets/showcase-gaming.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A fictional fantasy in-game HUD mockup rendered at 16:9 (1536×1024).
> Painterly RPG aesthetic — not photoreal. Background is a hand-
> painted forest clearing at dusk: violet sky, layered silhouetted
> conifers, a faint glowing rune-circle in the foreground at low
> opacity. Overlaid HUD elements arranged with strict spatial
> discipline. Top-left corner cluster: a circular character portrait
> of an original fictional ranger in green hood, a horizontal red
> "HEALTH 84/120" bar beneath, a slim mana strip below ("MANA 36/80")
> in pale teal, and a small XP segment underneath. Top-right corner: a
> compact circular minimap with a fictional region name "DRIFTSHORE
> WOODS" beneath it and three icon pips for points of interest.
> Bottom-center: a horizontal hotbar of eight square slots with
> ornamented corners, the active slot ringed in warm gold; each slot
> shows a small painted item icon. Bottom-right: a short "Quest:
> recover the moonsteel shard" objective card. All HUD chrome uses
> warm gold filigree on translucent dark-green panels with subtle
> embossed edges. Painterly game register; readable at thumbnail.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real game franchise IP (no World of
Warcraft, no Elden Ring, no Genshin, no Zelda), no real player
gamertags, no real brand marks, no photoreal humans, no neon, no UI
that copies a specific shipped game.

---

### Showcase 9 — photography

Save to: `docs/assets/showcase-photography.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A cinematic 35mm-anamorphic film still rendered at 16:9 (1536×1024).
> Single subject: an original mid-30s woman in a charcoal wool coat
> stands at a rain-glossed crosswalk at blue hour, half-turned away
> from camera, looking down a wet city street that fades into
> low-saturation neon haze. Composition leaves generous negative
> space camera-left so the subject reads as a quiet narrative beat,
> not a portrait. Lighting: a soft cool key from camera-left with a
> tighter warm practical from a streetlight behind catching the rim
> of her coat and a thin specular along the puddle in front of her;
> light-hair-particle flare clips the top-right corner just enough to
> imply atmosphere. Lens character: anamorphic oval bokeh in the
> background, mild barrel distortion on the storefront line, gentle
> vertical streaks on the brightest highlights. Color grade: teal
> shadows, amber highlights, deep crushed blacks, restrained
> saturation. Subtle 35mm grain throughout. Frame should read as a
> single beat from a quiet indie thriller.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-celebrity likeness, no
recognizable real city by name, no real news brand overlays, no
HDR-glossy plastic finish, no copyrighted franchise references, no
text overlays, no in-frame UI chrome.

---

### Showcase 10 — fashion

Save to: `docs/assets/showcase-fashion.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A single-look fashion lookbook hero plate rendered at 16:9
> (1536×1024). The garment is the subject, the figure carries it.
> Composition: an original androgynous model stands three-quarter
> facing camera against a warm bone-colored cyclorama, lit by a soft
> overhead key and a low fill that lets the fabric drape read. The
> look is a tailored taupe linen overshirt over a longer slate-blue
> tunic, belted at the waist with a wide brushed-brass buckle, with
> sand-colored wide-leg trousers. The fabric drapes are clearly
> structured — the editor would credit the shoulder break and the
> hem. Across the top-left, a small section banner reads "LOOK 04 —
> FW26 / DRIFT". Down the right margin, a vertical credit list
> typeset in tight small caps reads "Overshirt — house atelier ·
> Tunic — runway sample · Trousers — house atelier · Buckle —
> brushed brass". Bottom-right corner: a fictional brand wordmark
> "Lautre" in a brutalist sans. Editorial fashion-week aesthetic,
> dense legible typography, garment-first staging.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-house monograms (no LV, no
Chanel, no Prada, no Hermès), no real-celebrity faces, no
HDR-oversaturated skin, no busy backdrop, no neon, no body-revealing
poses, no franchise IP.

---

### Showcase 11 — architecture

Save to: `docs/assets/showcase-architecture.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A conceptual architectural facade study rendered at 16:9
> (1536×1024). Single-elevation hero treatment of an original
> mid-rise civic building (six storeys), shown frontal, at golden
> hour. The facade is a contemporary public-realm composition:
> warm-cream limestone base course, three storeys of dark-oxide
> bronze mullion grid wrapping deep punched windows, and an upper
> setback in board-formed concrete with a continuous public roof
> terrace planted with low grasses. A wide cantilevered canopy
> shelters the entry plaza below; small fictional human silhouettes
> at low contrast give scale at the plaza level. To the right edge of
> the frame, a thin metadata sidebar typeset in lightweight sans
> reads "PROJECT: HARBOUR EXCHANGE / CLIENT: METRO LIBRARY TRUST /
> SITE: 2.1 ha / GFA: 8,400 m² / PHASE: COMPETITION /
> COMPLETION: 2028". Bottom-left carries a confident project banner
> "HARBOUR EXCHANGE — COMPETITION ENTRY 04". Studio-grade
> architectural rendering register: warm but desaturated, soft sky
> gradient, no people in detail, no traffic in foreground.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-architect credits (no Foster,
no BIG, no Gehry), no real city skylines or famous landmarks, no
real client logos, no recognizable buildings, no photoreal hero
people, no neon, no rainbow palette.

---

### Showcase 12 — food

Save to: `docs/assets/showcase-food.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> An editorial restaurant menu poster cover rendered at 16:9
> (1536×1024) — appetite-led but typography-first. Background is a
> warm cream-paper field with subtle linen texture and a faint dotted
> seasonal motif at the corners. Composition centers a tall
> fictional menu poster panel occupying about 65 percent of frame
> width: a confident display-serif masthead reads "OSTERIA DRIFT —
> AUTUMN MENU" with a thin rule beneath. Below the masthead, three
> categorized columns of dishes typeset in a humanist sans body face
> with leader-dot rules to small italic prices: "ANTIPASTI" lists
> three items ("Pumpkin focaccia · 7 / Olive tapenade · 9 / Roasted
> chestnut · 11"); "PRIMI" lists three ("Mushroom tagliatelle · 18 /
> Squash gnocchi · 17 / Walnut ravioli · 19"); "DOLCI" lists three
> ("Honey panna cotta · 8 / Pear tart · 9 / Dark hazelnut torte · 9").
> A footer band sets a tagline "Open six nights — wine list inside."
> To the right of the menu panel, a small inset shows a single
> hand-drawn ingredient sketch of a sage sprig in soft watercolor
> wash. Dense legible typography; no photographed dishes; ingredient
> story over plated photography.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-restaurant marks (no Noma, no
Eleven Madison, no Michelin star imagery), no celebrity-chef
likeness, no real wine labels, no photographed plates of food, no
neon, no franchise IP, no HDR oversaturation.

---

## 3. Three SVG specs (decision summary)

The three SVG assets were authored deterministically — text-anchored
SVG with `viewBox`, gradients, and `<title>` / `<desc>` for screen-
readers. They render identically across browsers and across model
versions, ship as small text payloads (no LFS), and pass the
`tests/unit/test_atlas_v03.py::test_svgs_well_formed` regression. The
default recommendation is to **keep them**. If the reader's first-fold
needs a richer visual idiom, regenerate them with the prompts below.

### 3.1 hero.svg

**Current state.** A 1200×600 SVG positioned as the README hero
banner: dark-navy gradient ground with a faint dot pattern overlay,
the wordmark "image2-workbench" in heavy display weight, a teal
"SPEC-FIRST · BILINGUAL · AUDITABLE" eyebrow line, two schematic
"prompt card" rectangles wired to a render-output square via an
arrow marker, and a stat strip showing "16 domains / 52 templates".
Already accessibility-friendly with `aria-labelledby` referencing
`<title id="hero-title">` and `<desc id="hero-desc">`.

**If you want a re-render via gpt-image-2.**
> A wide hero banner rendered at 16:9 (1536×1024), evoking a
> "spec-first generative-image workbench". Background: deep navy
> gradient (#0E2A4D → #0B1F3A) with a faint cyan dot grid. Center:
> the wordmark "image2-workbench" in heavy display sans, white. Above
> it a teal eyebrow reads "SPEC-FIRST · BILINGUAL · AUDITABLE". Left
> third: two stylized "prompt cards" — flat off-white rectangles with
> faux yaml lines (subject:, composition:, text_blocks:). Right
> third: a schematic "render-output" framed square at 1.5× the card
> size, suggesting an image preview, with a clean teal-to-blue
> gradient arrow connecting the cards to the square. Bottom band: a
> stat row showing "16 DOMAINS · 52 TEMPLATES · 7 RUNTIMES". No
> watermarks, no real brand logos, no photoreal screenshots, no glow
> beyond the gradient.

Size: `1536x1024` (16:9) · quality `medium` first pass, `high` for ship.
Negative list: no watermarks, no real product UIs, no neon, no
glassmorphism, no photoreal screenshots.

**Recommendation.** **Keep the current SVG.** The webp showcase strip
will carry the photographic richness on the page; the hero is more
useful as a small fast-rendering text-anchored deterministic banner.

---

### 3.2 workflow.svg

**Current state.** A 1200×300 horizontal SVG that visualises the
spec-render-output pipeline as three stacked panels: a `spec.yml`
panel showing yaml keys, a render arrow labelled `i2w template
render`, and a `prompt.md → Images API → ledger.csv` arc. Light
background gradient, text-only icons, accessible.

**If you want a re-render via gpt-image-2.**
> A clean horizontal workflow diagram rendered at 16:9 (1536×1024)
> reading "spec → render → output". Background: soft off-white
> (#F8FAFC → #E2E8F0) with rounded panel cards. Three stages set
> left to right at equal width with thick teal-to-blue arrows
> connecting them. Stage 1: dark-navy card titled "spec.yml" showing
> faux yaml keys (subject, composition, text_blocks, quality_policy).
> Stage 2: a slim arrow labelled "i2w template render" with the words
> "bilingual / strict-undefined" beneath. Stage 3: a card titled
> "Images API" showing a small generated-image thumbnail mark and a
> ledger CSV row underneath. Below the row a strapline reads "every
> image has a receipt." Clean editorial vector aesthetic, no
> photorealism.

Size: `1536x1024` (16:9) · quality `medium` first pass, `high` for ship.
Negative list: no watermarks, no real API logos (no OpenAI mark, no
Anthropic mark), no photoreal screenshots, no neon.

**Recommendation.** **Keep the current SVG.** The diagram is
text-deterministic, will not drift across model retrains, and reads
cleanly at any DPI.

---

### 3.3 production-controls.svg

**Current state.** A 1200×360 SVG rendering a four-pillar capability
matrix as a stacked bar chart: pillars are `cost`, `preflight`,
`batch`, `ledger`; tiers are manual / opt-in / shipped. Each pillar
is a stacked bar with image2-workbench's "shipped" segment on top.
Hand-tuned palette (teal / blue / slate) with axis labels.

**If you want a re-render via gpt-image-2.**
> A clean editorial capability matrix rendered at 16:9 (1536×1024)
> titled "Production controls — capability matrix". Soft off-white
> background. Four vertical bars labelled at the bottom "cost",
> "preflight", "batch", "ledger". Each bar is segmented in three
> stacked tiers — bottom slate "manual", middle blue "opt-in", top
> teal "shipped". Each tier carries a small caption to the right of
> the bar describing what the workbench ships at that tier (for
> example "$/img estimator", "size + extension preflight", "Batch API
> 50%-off lane", "session-rotated CSV ledger"). A short legend at
> top-left reads "MANUAL · OPT-IN · SHIPPED". Editorial vector
> aesthetic, restrained palette, no photorealism.

Size: `1536x1024` (16:9) · quality `medium` first pass, `high` for ship.
Negative list: no watermarks, no real-product logos, no
glassmorphism, no neon, no real customer names, no photoreal
screenshots.

**Recommendation.** **Keep the current SVG.** This chart in
particular benefits from the deterministic SVG path — the bar
heights and tier counts are load-bearing claims about what the
workbench ships. A bitmap re-render would add visual richness but
might mis-render the text labels.

---

## 4. Codex receiving instructions

Step-by-step procedure for the agent that picks up this hand-off:

1. **Render the twelve webps.** For each prompt block in §2, submit
   the prompt text to your gpt-image-2 endpoint at size `1536x1024`,
   quality `medium` (first pass) or `high` (ship pass). Save each
   bitmap to the exact path named in the prompt
   (`docs/assets/showcase-<domain>.webp`). All twelve filenames are
   already referenced in `README.md` and `README.zh.md`.

2. **Run the test suite.**

   ```bash
   cd /Users/star/image_skill
   .venv/bin/python -m pytest -q
   ```

   The expected count is **803 tests passing** (446 V0.2 +
   357 V0.3 atlas regression). No skip count change beyond the
   existing `frontmatter` optional-import skip.

3. **Lint.**

   ```bash
   .venv/bin/ruff check src tests
   ```

   Must report `All checks passed!`.

4. **Re-check gallery drift in both languages.**

   ```bash
   .venv/bin/i2w gallery readme --check README.md
   .venv/bin/i2w gallery readme --lang zh-CN --check README.zh.md
   ```

   Both must exit `0`. If they don't, run with `--inject` to refresh
   and re-commit the README diffs as part of the same PR.

5. **Stage, commit, push.**

   ```bash
   git add docs/assets/showcase-*.webp
   git commit -m "chore(assets): add 12 showcase webps rendered via gpt-image-2"
   git push origin main
   ```

   Do not include any other change in that commit — keep the asset
   drop reviewable.

6. **Watch CI.** The GitHub Actions pipeline must remain green. If the
   webp files exceed reasonable size (>500 KB each), re-export at a
   slightly higher webp compression ratio (the tests do not assert on
   filesize but readers will appreciate it).

7. **Tag.**

   ```bash
   git tag -a v0.3.1 -m "v0.3.1 — atlas + showcase imagery complete"
   git push --tags
   ```

---

## 5. Skill-ecosystem matrix snapshot

The atlas now lives behind a runtime-neutral skill bundle
(`skills/gpt-image/SKILL.md`). The advertised compatibility matrix is
locked in by `tests/unit/test_skill_compat.py` and documented in full
in `docs/skill-compatibility.md` (with citations). Snapshot:

| Runtime              | Status        | Notes                                                                  |
| -------------------- | ------------- | ---------------------------------------------------------------------- |
| Claude Code          | `tested`      | Symlink-discovered via `~/.claude/skills/gpt-image/`.                  |
| Anthropic API Skills | `tested`      | Same `claude.json` manifest; uploaded via the Skills API.              |
| OpenAI Codex CLI     | `tested`      | Symlink-discovered via `~/.codex/skills/gpt-image/`.                   |
| LangChain            | `shim_ready`  | `manifests/langchain.py` — Python `BaseTool` shim, smoke-tested.       |
| smolagents           | `shim_ready`  | `manifests/smolagents.py` — `@tool`-decorated callable, smoke-tested.  |
| OpenClaw             | `theoretical` | `manifests/openclaw.json` — agentskills.io-shaped, untested live.      |
| Hermes Agent         | `theoretical` | `manifests/hermes.yml` — agentskills.io-compatible, untested live.     |

Status definitions and full citations live in
`docs/skill-compatibility.md`. The runtime list is regression-tested
in `tests/unit/test_atlas_v03.py::test_skill_compatibility_doc_lists_seven_runtimes`.

---

## 6. v0.3.1 polish backlog ("Trim Theater")

These are deliberate post-image-drop trim items. None block the
v0.3.1 tag; all are worth picking up before v0.4.

- **Delete the `i2w ledger drift` command** — no current users; the
  same job is doable via `ledger query --group-by snapshot`. Replace
  with a doc snippet, drop the CLI surface.
- **Make `/v1/moderations` opt-in** — currently default-on through the
  preflight pipeline. Default to off; gate behind `--moderation-check`
  and document in `docs/getting-started.{en,zh}.md`.
- **Demote the token estimator default** — show only when the user
  explicitly asks via a `--token-estimate` flag. The current default
  output adds noise to small renders.
- **Remove the soft-import `try: from ..errors` blocks** in
  `commands/cost.py` and `commands/batch.py`. `errors.py` is now
  stable; the fallback paths are dead code.
- **Audit pydantic models for `extra="forbid"`** — the `ConfigDict` in
  `compiler/schema.py` is correct; check the costing and ledger
  models too and tighten any that still default to `extra="ignore"`.
- **Decide the fate of `responses_api.py`** — currently unreferenced
  dead code. Either wire it into `commands/render.py` for
  `api_mode: responses` or delete.
- **Decide the fate of `commands/version.py`** — duplicates an
  inline-CLI version flag. Pick one source of truth.
- **Empty-ledger UX hint** in `i2w ledger query` — when the ledger
  file is empty, print "No runs yet — try `i2w render generate`".
- **Add `--csv` flag to `i2w cost compare`** so the cost-modeling
  table is grep-able from CI logs.

---

## 7. Verification matrix (state at handoff)

| Property                                  | Value                                          |
| ----------------------------------------- | ---------------------------------------------- |
| Pytest count (full suite)                 | **803 passing**, 1 skipped (optional dep)      |
| Atlas regression tests                    | **357 passing** (this hand-off batch)          |
| Ruff lint (`src tests`)                   | `All checks passed!`                           |
| Domain count                              | **16** (verified against `templates/`)          |
| Template count                            | **52** (verified across all 16 domains)        |
| `DOMAIN_CARD.md` count                    | **12** (V0.3 batch)                            |
| README EN gallery drift                   | clean (`i2w gallery readme --check README.md`) |
| README zh-CN gallery drift                | clean (`--lang zh-CN --check README.zh.md`)    |
| Showcase webp slots referenced            | **12** in each README; bitmaps not yet on disk |
| Hand-authored SVG count (`docs/assets/`)  | **3** (hero, workflow, production-controls)    |
| Skill runtimes documented                 | **7** (claude, codex, anthropic, langchain, smolagents, openclaw, hermes) |
| Competitor mentions in READMEs            | **0** (`wuyoscar`, `EvoLinkAI`, `YouMind` absent) |
| `input_fidelity` references in templates  | **0** (only the schema doc lists it as a no-no) |

---

End of hand-off. After §4 is complete and the twelve bitmaps are
committed, the v0.3 line is done. The trim-theater list in §6 picks
up where this leaves off.
