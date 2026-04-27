# music — Domain Card

## Lens
Music-identity art — album covers, tour posters, podcast covers — where
a single visual hook plus the artist's name and a thin sliver of
metadata tells the story. The artwork is the product.

## FOR
- Square album / single covers with one hero motif and credit type.
- Vertical concert / tour posters for fictional artists and labels.
- Podcast cover art that survives at 56-pixel thumbnail.

## NOT FOR
- Date-led event flyers where the date is the hero — use `events/`.
- Real-band, real-label, real-venue artwork (always fictional here).
- Lit-stage concert photography or audience crowd shots — use
  `photography/`.
- Music-streaming UI mockups — use `uiux/`.

## Key axes
- Visual hook: single motif beats collage; artist identity beats date.
- Surface: print-stock discipline (silkscreen, sleeve), not screen gloss.
- Type: credit-line quiet, not banner-shouting; album title is rarely
  the visual hero.

## Templates in domain
- `music_album_cover` — poster, 1:1 (1024x1024), `text_fidelity_dense`.
  Square sleeve with single hero motif + artist + album + label credit.
- `music_concert_poster` — poster, 9:16 (1088x1920), `text_fidelity_dense`.
  Vertical tour announcement with motif + tour name + dates + city run.

## Forbidden
Real famous band names, real label logos, real public-figure musicians,
real venue marks, parental-advisory iconography, rainbow gradients,
celebrity photo collages.
