<!--
SPDX-License-Identifier: CC-BY-4.0
-->

# Prompt craft

How to write prompts for `gpt-image-2` that the model actually obeys, and how
the workbench's seven-section DSL helps you do it consistently. Upstream
reference: the OpenAI cookbook image-prompting guide
(`https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide`).

## Why structured prompts beat free-text

`gpt-image-2` reads its input as a brief, not as a sentence. A wall-of-text
prompt forces the model to guess at structure: which noun is the subject,
which adjective belongs to which object, which line is a quote vs a
description. The result is correlated noise — not random failures, but
*systematic* drift away from what you wanted.

Structured prompts pin the brief down. When you tell the model explicitly
"this is the subject; this is the action; this is the literal text to
render", you remove the guesswork. The same structure also gives you a
debugging surface: when an output is wrong, you can usually point to the
section that failed.

The workbench's seven-section DSL is one such structure. It is *opinionated*
— there are other good ones — but it is the structure every template in
this repo compiles down to. In V0.3 the canonical domain set spans 16
domains (business, academic, uiux, anime, ecommerce, industrial,
product, advertising, social_media, gaming, photography, fashion, food,
architecture, interior, travel) with a target of 52 executable
templates; the same seven sections power every one of them.

## The seven sections

Every compiled prompt has seven labelled sections in this order:

1. **subject** — who or what is in the frame.
2. **action** — what they're doing.
3. **scene** — where it happens.
4. **composition** — how the camera sees it.
5. **style** — render style and mood.
6. **text_blocks** — literal text the image must render.
7. **preserve and negative** — what to keep (in edits) and what to exclude.

For each section: what it controls, an example phrasing, and a common
mistake.

### 1. subject

**Controls:** the central object(s) in the frame. The model leans heavily on
this section for who-is-the-protagonist; everything else gets read as
modifying it.

**Example:** `subject: "a 2x2 SWOT analysis card for a fintech startup,
filling the full canvas"`.

**Common mistake:** burying the subject inside a paragraph
(`"Generate an image where I'd like to see a SWOT card..."`). The model
will sometimes interpret "image" as the subject. Lead with the noun.

### 2. action

**Controls:** verbs and dynamic relationships. Gives the model permission
to depict motion, interaction, gesture.

**Example:** `action: "the four quadrants are arranged Strengths
top-left, Weaknesses top-right, Opportunities bottom-left, Threats
bottom-right"`.

**Common mistake:** using static descriptors instead of verbs. "is
arranged" is less effective than "arranges". The model rewards active voice.

### 3. scene

**Controls:** the setting, environment, lighting context, supporting
elements not central to the subject.

**Example:** `scene: "minimalist white background, soft shadow under the
card, studio-product-photography lighting"`.

**Common mistake:** packing style and scene into the same sentence. Style
("flat vector", "watercolour", "photoreal") goes in section 5, not here.

### 4. composition

**Controls:** camera framing, perspective, focal length, layout grid, where
the eye lands first.

**Example:** `composition: "head-on flat view, 3:2 aspect ratio, the four
quadrants occupy a 2x2 grid with equal weight, 8% margin around the card"`.

**Common mistake:** specifying composition in cinematic language without
grounding numbers. "Cinematic shot, dramatic angle" gives the model
freedom to interpret. "Head-on, 3:2, equal-weight 2x2 grid" gives it a
grid to fill.

### 5. style

**Controls:** render aesthetic — flat vector vs photoreal vs watercolour vs
anime — plus colour palette, line weight, mood adjectives.

**Example:** `style: "flat infographic vector, two-tone palette (deep navy
and warm coral), confident sans-serif typography, business-formal mood"`.

**Common mistake:** chaining ten adjectives. Three to five style cues that
agree with each other beat ten that fight. If you find yourself writing
"realistic but stylised but flat but illustrated", pick one.

### 6. text_blocks

**Controls:** the literal text the image must render. Each block is a
short string in **double quotes**, ideally **80 characters or fewer**. The
model treats quoted strings as "render this verbatim".

**Example:**
```
text_blocks:
  - title: "SWOT Analysis"
  - quadrants:
    - "Strengths: regulatory licence in 12 markets"
    - "Weaknesses: heavy dependence on one acquirer"
    - "Opportunities: B2B embedded finance"
    - "Threats: incumbent banks moving in"
```

**Common mistake:** writing 200-character marketing paragraphs and asking
the model to render them as image text. `gpt-image-2` is excellent at
short literal strings (titles, button labels, axis ticks) and gets
progressively worse with length and density. See the chunking section
below.

### 7. preserve and negative

**Controls:** in edits, what *not* to change; in any prompt, hard
exclusions.

- **preserve:** a list, only meaningful for `i2w render edit` (which sends
  a reference image alongside the prompt). Each entry names something in
  the input that must survive untouched.
- **negative (NO list):** capitalised `NO` markers indicating elements
  that *must not* appear. The model treats `NO` as a stronger signal than
  "without" or "no" in lowercase.

**Example (edit):**
```
preserve:
  - "the company logo in the top-left corner"
  - "the original colour palette"
negative:
  - "NO stock-photo people"
  - "NO additional text beyond what's listed in text_blocks"
```

**Common mistake:** putting "without people" or "no text" in lowercase
inside a paragraph. The model often ignores it. Use the `NO` prefix.

## Chunking text blocks

Why each block stays short and quoted:

- **Quotes mean "render verbatim".** `"Quarterly Revenue"` is read as
  "literally output those characters". Without quotes, the model treats it
  as a topic, not a string, and may rephrase it.
- **80 characters is the comfort zone.** `gpt-image-2` renders short
  strings cleanly and starts to drop or smear letters past roughly 80
  characters per line. If you have a longer block, split it into two
  blocks; if you have a paragraph, you almost certainly want a graphic
  with the paragraph as a caption rendered separately, not as image text.
- **One language per block.** Don't mix Chinese and English in a single
  quoted string — the model can do both, but switching languages mid-block
  destabilises typography. Use two blocks instead.

## Preserve lists for edits

When calling `i2w render edit`, you pass a reference image plus the same
seven-section structure. The `preserve` list is your contract with the
model: things named here must come through unchanged.

The phrasing pattern that works most reliably is:

> *Change only `<X>` — keep everything else exactly as in the input.*

Then the `preserve` list enumerates the "everything else" you most care
about, in concrete terms ("the colour palette", "the layout", "the logo
position", "the typography weight"). Naming concrete things beats vague
"keep the style".

If you over-preserve (list every detail), the model starts to refuse the
edit entirely. Aim for three to six preserve items: the load-bearing ones.

## NO list (negative constraints)

Capitalised `NO` is a hard exclusion marker. Patterns that work:

- `NO stock-photo people` — exclude a category.
- `NO text other than the items in text_blocks` — bound the typography.
- `NO logos, watermarks, or signatures` — exclude unwanted overlays.
- `NO photorealistic faces` — exclude a render style for ethical / brand
  reasons.

Patterns that don't work as well:

- `Don't include people` — lowercase, conversational; often ignored.
- `Avoid clutter` — too vague; the model has no fixed definition of
  clutter.

A useful rule: every NO item should be something you could point at in a
bad output and say "that, specifically, shouldn't be there".

## Bilingual prompts

Each template declares `language_targets: [en, zh-CN]` (most do), and the
compiler emits one prompt per target. The `language_targets` field
controls the **language of the prompt itself** — the meta-instruction the
model reads — not the language of the text rendered into the image.

The text in the image comes from the variables you fill in. So:

- A SWOT template can be rendered with `language_target: en` and English
  variable values to get an English brief that produces an image with
  English typography.
- The same template, rendered with `language_target: zh-CN` and Chinese
  variable values, gives a Chinese brief that produces an image with
  Chinese typography.
- You can also render with `language_target: en` but Chinese variable
  values — the brief is in English, but the text in the image is Chinese.
  This is occasionally useful when the surrounding ChatGPT conversation is
  in English but the deliverable is for a Chinese audience.

In practice, match the brief language to the image text language unless
you have a reason not to. The model is happiest when the two agree.

## What gpt-image-2 still struggles with

Even with structured prompts, some failure modes persist. Be aware of
them, and design around them.

- **Small dense text.** Tiny captions, dense data tables, footnote-sized
  legends often blur or invent characters. Mitigation: increase canvas
  size to give text more pixels, reduce the amount of text, or render the
  text separately and overlay it in your editor.
- **Complex multi-character interactions.** Three or more figures
  interacting (passing objects, looking at each other, hand contact) tend
  to produce extra fingers, mismatched eyelines, or merged limbs.
  Mitigation: stage scenes with one or two characters and use
  `i2w render edit` to add a third over a reference.
- **Exact element placement.** "Logo at exactly 5% from the top-left
  corner, 120px wide" doesn't reliably translate. The model approximates
  layout. Mitigation: describe layout *zonally* ("top-left logo, centred
  title, bottom-right CTA") and accept that pixel-precise placement needs
  a post-edit pass in a real layout tool.
- **Counting.** "Exactly seven items" sometimes lands on six or eight.
  Mitigation: enumerate the items in `text_blocks` so the model has to
  render each one.
- **Long strings of digits.** Phone numbers, ISBNs, and similar long
  numeric strings garble. Mitigation: avoid making them image text
  whenever possible; render the rest of the design and overlay the digits
  yourself.

A good prompt makes the easy things automatic and acknowledges where the
hard things still need a human in the loop.
