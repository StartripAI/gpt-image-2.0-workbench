# interior — domain card

## FOR
- Room-scale residential and small-commercial interiors.
- Single-room photoreal mockups, material/finish boards, before/after pairings.
- Pre-construction visualisation for renovations and FFE specs.

## NOT FOR
- Exterior facades, massing, or urban context — use `architecture/`.
- Product packaging or catalog product cards — use `product/` or `ecommerce/`.
- Branded restaurant interiors with a heavy food story — keep the room generic
  here; route food-led scenes through `food/`.

## Key axes
- Scope: full-room photoreal volume vs. flat material chips vs. paired edit.
- API mode: most templates ship as `images_generate`; the before/after pairing
  ships as `images_edit` with locality phrasing and a populated preserve list.
- Grader: `text_fidelity_sparse` for the room mockup (one labelled zone),
  `layout` for the material board (grid composition), `edit_locality` for the
  before/after split.

## Templates in domain
- `interior_room_mockup` — mockup, 3:2 (1536x1024), `text_fidelity_sparse`.
  Photoreal single-room volume with one accent label.
- `interior_material_board` — infographic, 1:1 (1024x1024), `layout`.
  Flat-lay grid of named material / finish chips.
- `interior_before_after` — mockup, 16:9 (1920x1088), `edit_locality`.
  Split-screen renovation pairing; preserves shell, edits finishes.

Demo rooms are generic residential settings; no real homes by name.
