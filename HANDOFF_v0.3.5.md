<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# image2-workbench v0.3.5 — Handoff

This is the agent-to-agent handoff packet that ships with the v0.3.5
expansion of `image2-workbench`. v0.3.5 widens the atlas from 16
domains / 52 templates to **30 domains / 80 templates**, locks the
schema and bilingual READMEs around that surface, and enumerates a
complete **30 hero showcase** image strip — one webp per domain — that
codex will render via gpt-image-2 to take the GitHub-facing first fold
to ship-quality.

---

## 1. What this hand-off contains

The v0.3.5 atlas runs to **30 domains and 80 templates**, each of
which loads through the compiler, renders bilingually, survives the
gpt-image-2 hard-constraint validators, and is regression-locked by
the atlas test suite. CI is green at **893+ tests passing**.

Three SVG assets — `docs/assets/hero.svg`, `docs/assets/workflow.svg`,
`docs/assets/production-controls.svg` — remain on disk as text-
deterministic placeholders for the README first fold (see §3). They
were authored hand-tuned during the v0.3 cut and continue to serve;
the recommendation is to **keep them**, not to re-render.

What is **not yet on disk** is the `docs/assets/showcase-<domain>.webp`
strip — **thirty** 1536×1024 bitmaps that the README atlas section
already references. Codex's job in this handoff round is to render
those thirty bitmaps using the prompts in §2, drop the files into
`docs/assets/`, run the verification suite below, commit, and tag
**`v0.3.6`** (since v0.3.5 is the schema/template/README expansion that
we are shipping in this handoff round; the asset drop ships under
v0.3.6).

The thirty prompts below are written for direct submission to the
gpt-image-2 endpoint with no editing. Each prompt names a bitmap output
target (`docs/assets/showcase-<domain>.webp`), an exact size
(`1536x1024`, i.e. 16:9), a quality recommendation (`medium` for the
first pass, `high` once you are happy with the framing), and explicit
lists for the preserve / negative axes. Each is anchored on the
corresponding `templates/<domain>/DOMAIN_CARD.md` so the visual reads
as a faithful cover for the domain.

Codex's contract: **render the 30 webps to
`docs/assets/showcase-<domain>.webp` and commit + tag `v0.3.6`.** No
other repo changes belong in the asset drop commit.

---

## 2. Thirty showcase webp prompts

Each prompt follows the V1.5 prompt spec: literal text inside `""`
double quotes, explicit composition guidance, an explicit forbidden
list, and a preserve list (empty for fresh renders). Sizes are fixed at
`1536x1024` (16:9) so the cards line up cleanly in the README grid.
Submit each prompt through whichever interface codex prefers — the
`images.generate` API directly, or `i2w render generate` once the
template is wrapped, or the ChatGPT image-tool. The text inside the
prompt block is the only payload the model needs.

Numbered by canonical domain order: the V1 atlas first (1–12), the
V0.3 expansion next (13–16), and the V0.3.5 expansion last (17–30).

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

### Showcase 13 — product

Save to: `docs/assets/showcase-product.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A design-press packaging concept render at 16:9 (1536×1024). A
> single fictional product package — a tall matte-finish carton in
> warm bone with an oxidised-copper foil seal — sits centered on a
> soft warm-grey paper-toned set with a hairline horizon. The carton
> face carries a confident two-tier wordmark ""NORDEN / WHOLE BEAN
> COFFEE"" in a quiet display sans, a thin descriptor band reading
> ""Light roast · Single origin · 250 g"", and a small batch chip
> ""LOT 042 — ROASTED 04.26"". Lighting: a soft top-key with a
> tighter rim from camera-right that catches the foil seal, and a
> faint ground-contact shadow at low opacity. To the right of the
> carton, a slim spec column typeset in small caps lists ""Substrate:
> uncoated kraft / Foil: 1c oxidised copper / Tier: studio prototype
> 03 / Variant: bone"". Across the top-left corner, a small section
> banner reads ""PACKAGING CONCEPT — Q2 2026"". Restrained palette
> anchored on bone, oxidised copper, deep umber, and a single
> hairline of cool slate. The cover should read in 1.5 seconds as a
> design-press packaging plate — the package is the subject, the
> environment exists only to support it. No lifestyle context, no
> hands, no shelf surroundings.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-brand logos (no Apple, no
Aesop, no Muji, no Blue Bottle), no human models or hands, no
recognizable storefront context, no rainbow palette, no
glassmorphism, no neon, no photoreal human skin, no shelf or retail
environment.

---

### Showcase 14 — social_media

Save to: `docs/assets/showcase-social_media.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A platform-native feed creative mockup rendered at 16:9 (1536×1024)
> as if it were the editor's preview of a social launch post. Soft
> off-white workspace background carries a single phone-shaped frame
> at center holding a 1:1 launch-announcement post. The post itself
> is a high-contrast feed card: warm ochre flat-color ground, a
> confident two-line headline ""DRIFT 04 / DROPS 05.18"" in a heavy
> display grotesk, a thin date-anchored eyebrow above reading ""NEW
> RELEASE"", and a fictional studio wordmark ""LAUTRE"" tucked into
> the bottom-left at small-cap weight. To the right of the phone
> frame, a slim editor-side panel typeset in tight humanist sans
> reads ""Aspect 1:1 · Caption draft 02 · Schedule 05.18 09:00 ·
> Status DRAFT"" with a small green dot beside ""ready to post"". A
> top banner across the workspace reads ""FEED MOCKUP — LAUNCH
> POST"". Restrained palette: ochre, warm bone, ink, a single hot
> coral CTA pip. Thumb-scroll legibility: the hero card must read at
> 100-pixel tall thumbnail. The cover should read as an in-house
> social-team review board, not as a screenshot of any real platform.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-platform UI (no Instagram, no
TikTok, no X/Twitter, no Facebook, no real app chrome), no real
hashtags or handles, no celebrity faces, no recognizable photos, no
neon glow, no glassmorphism, no rainbow palette.

---

### Showcase 15 — interior

Save to: `docs/assets/showcase-interior.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A photoreal single-room interior mockup rendered at 16:9
> (1536×1024). Hero zone: a warm contemporary residential living room
> shot from a slightly low three-quarter angle so the back wall and
> the side wall both read. Plaster walls in a soft chalk-bone tone, a
> wide-plank smoked-oak floor, and a tall slim arched window flooding
> the room with afternoon side-light. Furniture: a low boucle sofa in
> oat, a single curved armchair in cognac leather, a sculptural raw-
> travertine coffee table, and a low slim sideboard in fluted ash on
> the back wall carrying a ceramic vase with three tall dried branches.
> Above the sideboard, a single oversized abstract painting in
> ochre-and-rust mineral pigments anchors the back wall. A subtle
> jute rug grounds the seating cluster. A small flat-tab label set
> on the right edge reads ""ACCENT WALL — back wall · ochre-rust
> palette · phase 02"". Soft cool secondary fill from the window
> balances the warm key. Photoreal but quiet — interior-architect
> register, FFE-spec polish, no busy clutter, no exterior view, no
> visible electronics. The frame should read as a residential
> renovation mockup ready for an FFE meeting.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-architect names, no real-IKEA
or Muji marks, no real-celebrity client names, no recognizable
real-house references, no exterior facade, no neon, no rainbow
palette, no HDR plastic finish, no humans in frame.

---

### Showcase 16 — travel

Save to: `docs/assets/showcase-travel.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A vintage-screen-print destination poster rendered at 16:9
> (1536×1024) for a fictional coastal place. Composition: a tall
> central illustration occupies roughly 70 percent of frame height
> showing a stylised seaside town climbing a hill — pastel-stuccoed
> houses with red-clay roofs stacked along a switchback road, a small
> harbour at the foot with two fictional fishing skiffs, and a
> distant headland fading into a warm haze. Aesthetic: 1960s WPA-
> meets-Italian-poster screen-print, four-color separation feel,
> soft grain, gentle ink-trap dots, no photoreal texture. A confident
> display-serif masthead at the top reads ""COSTA LUMINA"" with a
> thin rule beneath; a smaller subtitle reads ""Visit the slow
> coast — summer 2026"". Bottom-band sets a small tagline ""Train
> service from Northern Junction · Brochure inside"" and a fictional
> tourism mark ""Lumina Tourism Bureau"". Restrained palette: warm
> coral, ochre, dusk teal, deep indigo, paper-cream. The poster should
> read as a piece of mid-century travel ephemera reissued for a
> contemporary tourism office wall — wanderlust-led, type-driven,
> never literal photo reference.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real city names (no Paris, no
Tokyo, no NYC, no Lisbon), no real flags, no real airline logos, no
real tourism-board marks, no real famous landmarks, no celebrity
travelers, no neon, no rainbow palette, no franchise IP.

---

### Showcase 17 — typography

Save to: `docs/assets/showcase-typography.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A type-specimen plate rendered at 16:9 (1536×1024) on a warm
> uncoated paper field with subtle long-fibre grain. Letterforms are
> the subject; nothing else competes. Composition: a confident
> display-serif uppercase showing ""DRIFTLINE"" in monumental scale
> across the top third, set in a fictional studio-press typeface. A
> thin rule beneath, then a quiet metadata band in small humanist
> sans reading ""DRIFTLINE — A DISPLAY SERIF / 4 weights · 412
> glyphs / Studio plate 04 / 04.2026"". The middle band carries the
> full uppercase alphabet ""ABCDEFGHIJKLMNOPQRSTUVWXYZ"" set at
> medium weight with even letterspacing. Below the alphabet, a
> compact glyph grid: numerals ""0123456789"", punctuation marks
> "".,;:!?&@"", and a small ligature row showing ""fi · fl · ffi"".
> The bottom band sets a single line of body copy in the typeface at
> reading scale — ""The drift coast wakes in slow particulars — paper,
> ink, salt, time."" — to demonstrate text-block colour. Restrained
> palette: warm paper-cream, deep ink-black, a single oxidised brick
> accent on the masthead rule. Foundry-plate aesthetic, ink-on-paper
> register, generous margins. The cover should read as a fictional
> studio-press specimen sheet from a small independent foundry.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-foundry marks (no Adobe Fonts,
no Klim, no Pangram, no Commercial Type, no Monotype), no real
typeface names (no Helvetica, no Gotham, no Inter, no SF Pro), no
photography, no drop shadows, no neon glow, no rainbow palette, no
3D rendering, no glassmorphism.

---

### Showcase 18 — beauty

Save to: `docs/assets/showcase-beauty.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A clean-beauty editorial still life rendered at 16:9 (1536×1024). A
> single fictional skincare bottle — a tall amber-glass dropper bottle
> with a matte aluminum collar — sits slightly off-center on a soft
> warm-stone plinth against a graduated bone-to-rose-clay background.
> Quiet morning light enters from camera-left at a low angle, casting
> a long soft shadow that grounds the bottle and a thin specular
> along the glass shoulder. The bottle face carries a calm wordmark
> ""HALYARD"" in a small humanist sans, a single descriptor line
> ""HYDRATING SERUM · 02"", and a hairline volume mark ""30 ml"". To
> the right of the bottle, two small material-study elements share the
> plinth at low priority: a single drop of clear serum on the stone
> reading like a tiny specular bead, and a folded square of unbleached
> cotton fabric at quarter scale. A thin metadata strip at the bottom
> right typeset in small caps reads ""STUDIO STILL — STILL 04 / SERUM
> 02 / 04.26"". Restrained palette: bone, rose-clay, amber glass,
> matte aluminum, deep ink. Aesop / Byredo press-still register, no
> brand copying. Honest skin-of-glass texture, no plastic smoothing.
> The frame reads as a design-press beauty press kit still.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-brand marks (no Aesop, no
Byredo, no SKII, no Estée Lauder, no La Mer, no Glossier), no human
face, no model body, no rainbow palette, no neon, no HDR plastic
sheen, no franchise IP, no celebrity endorsements.

---

### Showcase 19 — events

Save to: `docs/assets/showcase-events.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A vertical-leaning music festival announcement poster rendered at
> 16:9 (1536×1024) — type-driven, date-anchored, single-image-concept.
> A tall hero panel sits at frame center occupying about 70 percent of
> width: deep-indigo field with a faint dotted halftone suggesting a
> dusk sky. A confident display-serif masthead at the top reads
> ""DRIFT FESTIVAL"" with a thin oxidised-coral rule beneath; the rule
> is interrupted by a hairline date stamp reading ""08.16 — 08.18 /
> 2026"". Below the masthead, a single hand-drawn motif occupies the
> middle third: a stylised paper-bird in three-color screen-print
> tones (coral, dusk teal, bone) ascending across the panel. Beneath
> the motif, a tightly-typeset tier list runs in a small humanist
> sans across three columns: ""FRIDAY — sunset stage / saturday —
> harbour stage / sunday — closing stage"" with three fictional act
> names per column ("ATLAS HUM", "DRIFTLINE", "NORDEN", "PALE
> SUMMER", "VENT", "OAR", "LANTERNA", "SLOW MARIN", "THE COAST").
> Bottom band: ticket band ""Day pass · 48 / Weekend · 110 / Box
> office opens 04.30"" and a fictional bureau mark ""LUMINA EVENTS
> COUNCIL"". Restrained palette: indigo, coral, bone, dusk teal,
> paper-grain throughout. Print-stock register; hierarchy reads
> festival > date > acts > tickets in 1.5 seconds.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real artist names, no real venue
names, no real festival logos (no Coachella, no Glastonbury, no
SXSW), no celebrity faces, no real-band photos, no neon, no rainbow
gradient, no franchise IP, no parental-advisory marks.

---

### Showcase 20 — tattoo

Save to: `docs/assets/showcase-tattoo.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A vintage American-traditional tattoo flash sheet rendered at 16:9
> (1536×1024) on aged cream paper with subtle deckle edges and gentle
> foxing at the corners. Composition: a 3×4 grid of twelve classic
> American-traditional motifs — a thick-lined swallow in flight, an
> anchor with a flowing banner, a five-petal rose with two leaves, a
> sailing ship under sail, a ship's wheel, a clipper-style anchor-and-
> rope, a pair of dice showing ""LUCK"", a horseshoe ringed by stars,
> a swallow-and-banner pair, a coiled snake on a dagger, a heart with
> a banner reading ""MOTHER"" (a generic homage, not a real shop's),
> and a single nautical lighthouse. Each motif uses the bold-black-
> outline / four-flat-color American Traditional palette: deep red,
> emerald green, mustard yellow, ink black — no shading gradients, no
> photo realism. A thin top banner sets a fictional shop name
> ""COASTLINE FLASH — SHEET 04"" and a footer band reads ""HAND-DRAWN
> · STUDIO PRINT · 04.2026"". Sheet aesthetic: paper grain throughout,
> a faint pencil grid behind the flash visible only at low contrast,
> small motif-numbering pencil marks beside each piece. The frame
> should read as a piece of vintage tattoo-shop ephemera.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real shop names, no real artist
signatures, no copyrighted franchise IP (no Disney, no Pixar, no
Marvel), no celebrity faces, no offensive imagery, no real political
emblems, no real military insignia, no neon glow, no rainbow
palette.

---

### Showcase 21 — watercolor_illustration

Save to: `docs/assets/showcase-watercolor_illustration.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A botanical watercolor specimen plate rendered at 16:9 (1536×1024)
> on visibly textured cold-press cotton-rag paper with generous
> bare-paper margins. Composition: a single hero specimen — a
> flowering wild fennel stem — sits centered, painted in transparent
> washes that show wet-into-wet bleeds at the petal edges and dry-
> brush detail along the leaf veins. Pigment behavior is part of the
> meaning: deliberate granulation in the deeper greens, a faint water-
> tide mark at the base of the stem where one wash dried slower,
> bare-paper highlights left untouched at the petal centers.
> Palette: muted sap green, ochre, soft cool grey, with the faintest
> wash of warm coral on the petal tips. Around the specimen, four
> thin sepia leader lines fan out to small handwritten labels in a
> quiet copperplate-leaning hand: ""petal · 5 lobes"", ""umbel cluster"",
> ""leaf · pinnate"", ""stem · ribbed"". Across the top, a thin title
> line set in small letterpress caps reads ""WILD FENNEL — STUDIO
> STUDY 04"". Bottom-right corner sets a fictional studio mark
> ""drift atelier — 04.2026"" in tiny pencil-feel script. Cold-press
> paper grain visible throughout the frame; no photoreal texture, no
> neon, no franchise IP.

Preserve list: (none — fresh render)
Negative list: no watermarks, no photoreal photography, no neon, no
franchise IP (no Studio Ghibli, no Disney botanical art), no real-
botanist names, no rainbow gradient, no 3D rendering, no
glassmorphism, no HDR plastic sheen, no oil-paint impasto.

---

### Showcase 22 — isometric_illustration

Save to: `docs/assets/showcase-isometric_illustration.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A strict 30°-30° axonometric city block illustration rendered at
> 16:9 (1536×1024). Composition: a single fictional urban block sits
> at frame center, drawn in true isometric projection — no perspective
> recession, no vanishing points. Five named buildings cluster around
> a small central plaza with a fountain and four trees: a four-storey
> mixed-use brick building (""HARBOUR HOUSE""), a low cafe with a
> striped awning (""SLOW CAFE""), a community library with a stepped
> roofline (""LUMINA LIBRARY""), a pocket grocer with crates outside
> (""CORNER MARKET""), and a small studio gallery with a sawtooth
> skylight (""DRIFT STUDIO""). Each building uses the domain's
> two-tone flat-shading recipe — a base color plus exactly one shadow
> step — and crisp 1-pixel silhouette outlines. Five thin leader lines
> fan from each building to small labels typeset in a clean humanist
> sans beside the geometry, never overlapping. A small grid of paving
> stones suggests scale at the plaza. Restrained palette: warm ochre
> brick, dusk teal awning, paper bone walls, slate roof, with a single
> oxidised coral accent on the gallery skylight. Across the top, a
> thin section banner reads ""CITY BLOCK 04 — DRIFTSHORE"". Plan-
> readable, vector-flat, never cinematic.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-storefront brands, no real
city names (no NYC, no Tokyo, no Paris), no perspective recession,
no two-point perspective, no photoreal texture, no neon, no
glassmorphism, no franchise IP, no real-architect references.

---

### Showcase 23 — comic_book

Save to: `docs/assets/showcase-comic_book.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A single American-style comic-book variant cover rendered at 16:9
> (1536×1024). Cover composition: a tall hero panel occupies the left
> two-thirds — an original masked vigilante in a slate-and-ochre
> jumpsuit named ""THE DRIFTER"" stands on a rooftop edge against a
> stormy dusk sky, cape mid-furl, a faint lightning fork crossing
> behind. The figure is drawn with confident inked linework — heavy
> shadow shapes, deliberate negative space inside the cape, classic
> Ben-Day halftone dot shading on midtones, no photo realism.
> Across the top, a confident comic-book masthead in heavy display
> sans reads ""THE DRIFTER"" with a thin sub-banner ""ISSUE 04 —
> VARIANT COVER"". A small fictional publisher mark in the top-left
> corner reads ""LUMINA COMICS"". The right one-third holds a
> vertical stack of cover furniture: an issue number badge ""04"", a
> small ""$4.99"" price chip, a faux barcode block, and a cover-line
> banner ""— a city wakes alone —"" set diagonally. Palette discipline:
> cool slate, ochre, oxidised coral lightning, ink-black; halftone
> dots visible on midtones, registration kept clean. The cover should
> read as a piece of single-issue Wednesday-shelf cover art from a
> small independent publisher.

Preserve list: (none — fresh render)
Negative list: no watermarks, no Marvel IP, no DC Comics IP, no
real-publisher logos (no Image Comics mark, no Boom mark), no
real-celebrity faces, no real-superhero names (no Spider-Man, no
Batman, no Wonder Woman), no franchise crossover, no rainbow
palette, no neon glow, no photo realism.

---

### Showcase 24 — music

Save to: `docs/assets/showcase-music.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A square album cover rendered at 16:9 (1536×1024) — the album-cover
> sleeve sits centered occupying about 65 percent of frame height
> against a soft warm-grey paper-toned mounting board so the cover
> reads as a press-kit plate. Cover face: a single hero motif fills
> the square — a stylised paper-cut crane mid-flight rendered in
> three-tone screen-print (coral, dusk teal, bone) over a deep
> indigo field with a faint long-fibre paper grain. Across the top of
> the sleeve, a quiet humanist-sans credit line reads ""ATLAS HUM"".
> Across the bottom, a confident display-serif title reads ""SLOW
> COAST"" with a thin rule beneath and a small line below ""LP · LUMINA
> RECORDS · 04.2026"". A subtle catalog mark sits in the lower-right
> corner: ""LR-014"". Beside the mounted cover on the warm-grey board,
> a small editor's caption strip in small caps reads ""ALBUM ART —
> STUDIO PROOF 04"" and a hairline color-bar gives the press-stock
> palette as five tiny chips. Print-stock register: the album art is
> the product, the room exists only to support the cover. Restrained
> palette throughout: indigo, coral, dusk teal, bone, ink-black. No
> photo realism, no neon, no celebrity reference.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-band names, no real-label
logos (no Sony, no Warner, no Columbia, no Sub Pop), no real
musicians' faces, no real album-art references, no parental-
advisory mark, no rainbow gradient, no neon glow, no franchise IP.

---

### Showcase 25 — science_fiction_concept

Save to: `docs/assets/showcase-science_fiction_concept.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A painterly science-fiction matte-painting keyframe rendered at 16:9
> (1536×1024). Subject: an alien landscape on a fictional moon called
> ""DRIFT-IV"". Foreground: a quiet tidal flat of glassy black mineral
> sand reflecting a violet-amber sky; a single original explorer
> figure in a slate-and-bone EV suit stands silhouetted at low scale
> against the horizon, helmet turned to the right. Mid-ground: a
> derelict modular research outpost half-sunk in the flat — three
> linked habitat pods with peeling thermal blanket and a single
> guidance mast still upright. Background: a colossal ringed gas-
> giant fills the right third of the sky, its rings cutting a thin
> diagonal across the frame; two small moons sit at the upper left.
> Lighting: a low warm-amber primary from the gas-giant's terminator
> with a cooler violet secondary from the sky; volumetric haze
> separates the planes. Painterly aesthetic — visible brushwork on
> rocks and clouds, no photoreal-CG plasticness, no lens flare. A
> small bottom-right metadata strip set in lightweight humanist sans
> reads ""DRIFT-IV · STUDY 04 · KEYFRAME 02"". Restrained palette:
> deep violet, warm amber, cool slate, glassy black, paper bone for
> the suit. The frame should read as a single beat from an unproduced
> indie sci-fi feature.

Preserve list: (none — fresh render)
Negative list: no watermarks, no franchise IP (no Star Wars, no
Halo, no Star Trek, no Mass Effect, no Dune), no real-celebrity
faces, no real spacecraft references, no NASA-mark, no SpaceX-mark,
no photoreal-CG plastic finish, no neon, no rainbow palette, no
text overlays beyond the metadata strip.

---

### Showcase 26 — infographic_data

Save to: `docs/assets/showcase-infographic_data.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A clean editorial data dashboard rendered at 16:9 (1536×1024) on a
> soft off-white paper-grade field. Composition: a strict four-panel
> grid sits at frame center carrying four chart cards. Top-left:
> ""WEEKLY ACTIVE READERS"" — a slim line chart trending up across
> twelve weeks, with two soft callout dots and a tiny annotation
> reading ""launch week"". Top-right: ""SOURCE MIX"" — a horizontal
> stacked bar split into four segments labelled ""Direct"", ""Search"",
> ""Referral"", ""Social"" with percentages stamped inside the bar at
> small caps. Bottom-left: ""TOP CHAPTERS"" — a small horizontal-bar
> chart of five fictional chapter titles ranked by reads, each row
> ending in a small unit count. Bottom-right: ""SESSION DEPTH"" — a
> minimal scatter plot of dot clusters, with a single trendline and a
> right-side legend reading ""shallow / median / deep"". Around the
> grid, the dashboard reads like an editorial spread, not a SaaS app
> screenshot: a slim title band at the top sets ""READING ANALYTICS —
> WEEK 17 / 2026"" in a confident humanist serif; a thin footer line
> sets ""SOURCE: STUDIO TELEMETRY · DRAFT NOT FOR DISTRIBUTION"".
> Restrained palette: ink-black, paper-cream, two muted accents
> (oxidised coral, dusk teal). Editorial register; no fake-corporate
> dashboard chrome.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-corporation names, no real
font names called out (no Helvetica, no SF Pro, no Inter), no real
publisher names, no celebrity references, no glassmorphism, no
neon, no rainbow gradient, no 3D rendering, no SaaS app chrome
mimicking a real product.

---

### Showcase 27 — kids_illustration

Save to: `docs/assets/showcase-kids_illustration.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A children's-book storybook spread rendered at 16:9 (1536×1024) in
> a warm hand-painted gouache-and-crayon register. Spread composition:
> a single illustrated scene fills the left two-thirds — a small
> friendly fox-cub character in a striped scarf walks across a low
> hill at dusk carrying a paper lantern; two field mice peek from
> long grass at her feet, and a pair of moths drift in the warm
> evening air. The right one-third is the type column: a generous
> off-white margin holds a single short narration band typeset in a
> friendly humanist sans at picture-book scale, reading ""On the
> evening Mira followed the small light, the field went quiet, and
> the world made room."" Beneath the narration, a smaller line in
> handwritten-feel script reads ""— page 04 of MIRA AND THE SMALL
> LIGHT"". Across the very top, a quiet running-head band reads
> ""MIRA & THE SMALL LIGHT — chapter two"". Aesthetic: visible paper
> grain throughout, soft brush-edges, a small amount of pencil
> texture, no photo realism. Restrained palette: warm ochre, dusk
> teal, paper-bone, deep ink, with a single soft amber glow from the
> lantern. The spread should read as a quiet independent picture-
> book page ready for an editor's review.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real children's-book franchise (no
Pixar characters, no Disney characters, no Studio Ghibli
characters, no Peppa Pig, no Bluey), no photo realism, no neon, no
rainbow gradient, no real-celebrity faces, no franchise IP, no
manga-anime line art register.

---

### Showcase 28 — automotive

Save to: `docs/assets/showcase-automotive.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A cinematic automotive hero plate rendered at 16:9 (1536×1024). A
> single fictional sport-tourer concept car — a low long-bonnet
> three-quarter-rear silhouette, two-door, glasshouse swept toward
> the rear, fictional studio name ""ATLAS STUDIO — MARK 04"" —
> sits at frame center on a deliberate empty backdrop: a swept
> matte-asphalt floor and a graduated ink-blue cyclorama sky
> behind. Lighting: a soft top-key catches the roof-line and the
> rear haunch with a tighter rim from camera-right that reads the
> body-side crease, while a low cool fill grounds the shadow under
> the chassis. Restrained color discipline: deep body in oxidised
> bone-pearl with a dark-anodised graphite belt-line and bronze
> accents on the wheels and badges. The fictional studio mark
> ""ATLAS STUDIO"" sits as a small embossed rear badge. To the
> right of the car, a slim metadata column typeset in a clean
> humanist sans reads ""ATLAS MARK 04 / segment: gran tourer /
> wheelbase: 2,820 mm / drivetrain: dual-motor / studio plate 04 /
> 04.2026"". Across the top-left corner, a confident section banner
> reads ""HERO PLATE — STUDIO REVIEW"". Cinematic but quiet — design-
> studio register, no hero driver, no road context, no real makers'
> cues.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real automaker logos (no BMW, no
Tesla, no Toyota, no Porsche, no Ferrari, no Mercedes), no real
model names, no celebrity drivers, no recognizable real-track
backdrops, no real license plates, no neon, no rainbow palette, no
HDR plastic sheen.

---

### Showcase 29 — pet

Save to: `docs/assets/showcase-pet.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A clean adoption flyer rendered at 16:9 (1536×1024) on a warm
> bone-paper field with subtle paper grain. Composition: a single
> hero portrait occupies the left half — a friendly mid-sized
> fictional shelter dog with a sand-and-white coat, soft brown eyes,
> floppy ears, sitting calmly on a soft slate-grey studio backdrop;
> the lighting is a quiet overhead key with a low warm fill, no
> dramatic shadows. The right half is a flyer-style type column on
> the same paper field. From the top: a confident display-sans
> headline reads ""MEET MILO""; a slim eyebrow above reads ""HOPE
> SHELTER · ADOPT 04""; below the name, a short trait list typeset
> in a humanist sans with a small leading bullet for each line
> reads ""— 3 years old / — 18 kg, mid-energy / — good with kids /
> — house-trained / — leash trained"". Below the traits, a small
> story paragraph in body weight tells a one-paragraph fictional
> story about Milo's path to the shelter. A footer band sets contact
> ""hopeshelter.example / open Tue–Sun"" and a fictional shelter mark
> ""HOPE SHELTER — DRIFT COUNTY"". Palette: bone, soft sage, warm
> ochre accent, ink-black. The frame should read as a quiet community
> shelter's adoption flyer.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-shelter logos, no real
celebrity pets, no copyrighted franchise pets (no Snoopy, no
Scooby-Doo, no Pikachu), no real-veterinary brand marks, no
photoreal-CG plastic finish, no neon, no rainbow palette, no
real adopter faces, no franchise IP.

---

### Showcase 30 — streetwear

Save to: `docs/assets/showcase-streetwear.webp`
Size: `1536x1024` · aspect `16:9` · quality `medium` (or `high` for ship)

Prompt:
> A streetwear drop announcement plate rendered at 16:9 (1536×1024).
> Composition: a single hero garment — a fictional boxy heavyweight
> hoodie in oxidised-coral fleece with a small chest embroidery —
> sits centered on a hung-and-pinned wardrobe board against a deep
> graphite cyclorama. The board lighting is a single high key with
> a tight rim from camera-left so the fleece nap and the side-seam
> stitching read clearly; a quiet ground-contact shadow grounds the
> garment. The chest embroidery is a tiny fictional studio mark
> ""DRIFTLINE STUDIO — DROP 04"" with a small index number ""04""
> below; the hood drawcords end in matte-aluminum aglets. Across the
> top of the frame, a confident heavy-display masthead reads ""DROP
> 04 / 05.18.2026"". Down the right margin, a vertical credit list
> typeset in tight small caps reads ""FABRIC — 480 GSM HEAVYWEIGHT
> FLEECE / FIT — BOXY / COLOR — OXIDISED CORAL / RUN — 240 UNITS /
> SHIPS — 06.04"". Bottom-left corner: the fictional studio wordmark
> ""DRIFTLINE"" in a brutalist sans, with a small pricing chip
> reading ""$148"". Restrained palette: oxidised coral, graphite,
> paper bone, ink-black, brushed aluminum. Urban-press register —
> garment-first staging, drop-list typography hierarchy.

Preserve list: (none — fresh render)
Negative list: no watermarks, no real-streetwear logos (no
Supreme, no Off-White, no Nike, no Adidas, no Stüssy, no Palace),
no real silhouettes (no Air Jordan 1, no Yeezy, no Dunk), no real-
celebrity collaborators, no recognizable real-storefront, no neon,
no rainbow gradient, no franchise IP, no photoreal-celebrity
faces.

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
arrow marker, and a stat strip showing "30 domains / 80 templates".
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
> stat row showing "30 DOMAINS · 80 TEMPLATES · 7 RUNTIMES". No
> watermarks, no real brand logos, no photoreal screenshots, no glow
> beyond the gradient.

Size: `1536x1024` (16:9) · quality `medium` first pass, `high` for ship.
SVG-render forbidden axes: no watermarks, no real product UIs, no
neon, no glassmorphism, no photoreal screenshots.

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
SVG-render forbidden axes: no watermarks, no real API logos (no
OpenAI mark, no Anthropic mark), no photoreal screenshots, no neon.

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
SVG-render forbidden axes: no watermarks, no real-product logos, no
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

1. **Render the 30 webps.** For each prompt block in §2, submit
   the prompt text to your gpt-image-2 endpoint at size `1536x1024`,
   quality `medium` (first pass) or `high` (ship pass). Save each
   bitmap to the exact path named in the prompt
   (`docs/assets/showcase-<domain>.webp`). All 30 filenames are
   already referenced in `README.md` and `README.zh.md`. The exact
   filenames the gallery references are:

   ```text
   docs/assets/showcase-business.webp
   docs/assets/showcase-academic.webp
   docs/assets/showcase-uiux.webp
   docs/assets/showcase-anime.webp
   docs/assets/showcase-ecommerce.webp
   docs/assets/showcase-industrial.webp
   docs/assets/showcase-advertising.webp
   docs/assets/showcase-gaming.webp
   docs/assets/showcase-photography.webp
   docs/assets/showcase-fashion.webp
   docs/assets/showcase-architecture.webp
   docs/assets/showcase-food.webp
   docs/assets/showcase-product.webp
   docs/assets/showcase-social_media.webp
   docs/assets/showcase-interior.webp
   docs/assets/showcase-travel.webp
   docs/assets/showcase-typography.webp
   docs/assets/showcase-beauty.webp
   docs/assets/showcase-events.webp
   docs/assets/showcase-tattoo.webp
   docs/assets/showcase-watercolor_illustration.webp
   docs/assets/showcase-isometric_illustration.webp
   docs/assets/showcase-comic_book.webp
   docs/assets/showcase-music.webp
   docs/assets/showcase-science_fiction_concept.webp
   docs/assets/showcase-infographic_data.webp
   docs/assets/showcase-kids_illustration.webp
   docs/assets/showcase-automotive.webp
   docs/assets/showcase-pet.webp
   docs/assets/showcase-streetwear.webp
   ```

2. **Run the test suite.**

   ```bash
   cd /Users/star/image_skill
   .venv/bin/python -m pytest -q
   ```

   The expected count is **893+ tests passing** (with the v0.3.5
   atlas regression batch included). No skip count change beyond the
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
   git commit -m "chore(assets): add 30 showcase webps rendered via gpt-image-2"
   git push origin main
   ```

   Do not include any other change in that commit — keep the asset
   drop reviewable.

6. **Watch CI.** The GitHub Actions pipeline must remain green. If
   the webp files exceed reasonable size (>500 KB each), re-export at
   a slightly higher webp compression ratio (the tests do not assert
   on filesize but readers will appreciate it).

7. **Tag.**

   ```bash
   git tag -a v0.3.6 -m "v0.3.6 — atlas + showcase imagery complete (30 domains)"
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

## 6. v0.3.6+ polish backlog ("Trim Theater")

These are deliberate post-image-drop trim items. None block the
v0.3.6 tag; all are worth picking up before v0.4.

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
- **Consider adding 1–2 secondary images per domain for a richer
  showcase strip (V0.4)** — the current strip ships one hero per
  domain; a secondary template-specific plate per domain (e.g. a
  flat-lay product board next to the packaging concept) would give
  the README a richer second-fold.

---

## 7. Verification matrix (state at handoff)

| Property                                  | Value                                          |
| ----------------------------------------- | ---------------------------------------------- |
| Pytest count (full suite)                 | **893+ passing**, 1 skipped (optional dep)     |
| Atlas regression tests (v0.3.5 batch)     | **green** (this hand-off batch)                |
| Ruff lint (`src tests`)                   | `All checks passed!`                           |
| Domain count                              | **30** (verified against `templates/`)         |
| Template count                            | **80** (verified across all 30 domains)        |
| `DOMAIN_CARD.md` count                    | **30** (one per domain at v0.3.5)              |
| README EN gallery drift                   | clean (`i2w gallery readme --check README.md`) |
| README zh-CN gallery drift                | clean (`--lang zh-CN --check README.zh.md`)    |
| Showcase-webp slots referenced            | **30** in each README; bitmaps not yet on disk |
| Hand-authored SVG count (`docs/assets/`)  | **3** (hero, workflow, production-controls)    |
| Skill runtimes documented                 | **7** (claude, codex, anthropic, langchain, smolagents, openclaw, hermes) |
| Competitor mentions in READMEs            | **0**                                          |
| `input_fidelity` references in templates  | **0** (only the schema doc lists it as a no-no) |

---

End of hand-off. After §4 is complete and the 30 bitmaps are
committed, the v0.3.5 line is done. The trim-theater list in §6 picks
up where this leaves off.
