# architecture — domain card

## FOR
- Exterior built form: building facades, massing, urbanism.
- Studio deliverables: competition boards, planning submissions, RFP cover art.
- Public-realm, site-scale, and architectural-portrait images.

## NOT FOR
- Interior rooms or material/finish boards — use `interior/`.
- Wanderlust or city-marketing posters — use `travel/`.
- Industrial machinery, factory floors, process diagrams — use `industrial/`.
- Photoreal candids of real famous buildings or real cities by name.

## Key axes
- Scale: building (facade) vs urban (site plan) vs portfolio (presentation board).
- Lens: hero elevation, top-down plan, multi-panel composite.
- Grader: facade & site rely on `text_fidelity_dense` for project metadata; the
  presentation board uses `layout` for its multi-panel structure.

## Templates in domain
- `architecture_facade_concept` — poster, 3:2 (1536x1024), `text_fidelity_dense`.
  Single-elevation conceptual facade rendering.
- `architecture_site_diagram` — diagram, 16:9 (1920x1088), `text_fidelity_dense`.
  Top-down site plan with three labelled zones.
- `architecture_presentation_board` — infographic, 16:9 (1920x1088), `layout`.
  Multi-panel composite (concept + diagram + render + text).

Demo vars use generic / fictional projects; never reference real famous
buildings, real cities by name, or real practising architects.
