<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Gallery

The gallery is the prompt-only surface of image2-workbench: generated markdown
that can be copied into web ChatGPT without installing Python or using an API
key. Every domain page is compiled from `templates/<domain>/*.yml` and shows the
same template in `en` and `zh-CN`.

## Domains

Current inventory: **30 domains / 80 executable templates**. Counts vary by
domain.

| Domain | Templates | Page |
|---|---:|---|
| `academic` | 4 | [academic.md](./academic.md) |
| `advertising` | 3 | [advertising.md](./advertising.md) |
| `anime` | 4 | [anime.md](./anime.md) |
| `architecture` | 3 | [architecture.md](./architecture.md) |
| `automotive` | 2 | [automotive.md](./automotive.md) |
| `beauty` | 2 | [beauty.md](./beauty.md) |
| `business` | 4 | [business.md](./business.md) |
| `comic_book` | 2 | [comic_book.md](./comic_book.md) |
| `ecommerce` | 3 | [ecommerce.md](./ecommerce.md) |
| `events` | 2 | [events.md](./events.md) |
| `fashion` | 3 | [fashion.md](./fashion.md) |
| `food` | 3 | [food.md](./food.md) |
| `gaming` | 3 | [gaming.md](./gaming.md) |
| `industrial` | 3 | [industrial.md](./industrial.md) |
| `infographic_data` | 2 | [infographic_data.md](./infographic_data.md) |
| `interior` | 3 | [interior.md](./interior.md) |
| `isometric_illustration` | 2 | [isometric_illustration.md](./isometric_illustration.md) |
| `kids_illustration` | 2 | [kids_illustration.md](./kids_illustration.md) |
| `music` | 2 | [music.md](./music.md) |
| `pet` | 2 | [pet.md](./pet.md) |
| `photography` | 3 | [photography.md](./photography.md) |
| `product` | 3 | [product.md](./product.md) |
| `science_fiction_concept` | 2 | [science_fiction_concept.md](./science_fiction_concept.md) |
| `social_media` | 3 | [social_media.md](./social_media.md) |
| `streetwear` | 2 | [streetwear.md](./streetwear.md) |
| `tattoo` | 2 | [tattoo.md](./tattoo.md) |
| `travel` | 3 | [travel.md](./travel.md) |
| `typography` | 2 | [typography.md](./typography.md) |
| `uiux` | 4 | [uiux.md](./uiux.md) |
| `watercolor_illustration` | 2 | [watercolor_illustration.md](./watercolor_illustration.md) |

## Regenerate

The domain pages are generated from the template DSL and checked-in demo
variables:

```bash
i2w gallery build
```

The README atlas is generated separately:

```bash
i2w gallery readme --lang en --inject README.md
i2w gallery readme --lang zh-CN --inject README.zh.md
```

## Two paths to a finished image

- **Web ChatGPT:** open a domain page, copy the prompt block in your preferred
  language, paste it into a ChatGPT conversation with image generation enabled,
  and edit the demo literal fields before sending.
- **CLI / API:** render the same template with
  `i2w template render ... --out prompt.md`, then pass the prompt file to
  `i2w render generate` when you need reproducible artifacts, validation,
  batch workflows, or local run history.

## License

The gallery markdown is **CC BY 4.0**. See
[`../licensing.md`](../licensing.md) for attribution guidance when reusing
prompts in derivative work.
