<!--
SPDX-License-Identifier: CC-BY-4.0
-->

# Licensing

This project ships under a **layered license**: code is permissively
licensed, content (templates, docs, gallery markdown) is openly licensed
with attribution, and third-party corpus records carry per-record
licensing metadata. This page is a plain-English guide; for legal text,
see `LICENSE` (Apache-2.0) and `LICENSE-CONTENT` (CC BY 4.0).

## Code — Apache-2.0

Everything under `src/`, `tests/`, `scripts/`, and `.github/` is
Apache-2.0.

**What you can do:**

- Use the code commercially, privately, or in derivative works.
- Modify it, fork it, redistribute it.
- Sublicense it under a different OSI-approved license, including
  permissive ones (MIT, BSD).

**What you must do:**

- **Preserve the `NOTICE` file** in any redistribution. Apache-2.0
  requires that downstream users see the attribution and patent-grant
  language.
- **Include a copy of the Apache-2.0 license** alongside any
  redistribution, even when sublicensing under another license.
- **State significant changes** you've made. A `CHANGELOG.md` line is
  enough.

**What you cannot do:**

- Use the project name, contributor names, or trademarks to endorse or
  promote your derivative work without permission.
- Remove or alter the copyright notices.

## Templates and docs — CC BY 4.0

Everything under `templates/`, `docs/`, and the top-level `README*`
files is Creative Commons Attribution 4.0 International.

**What you can do:**

- Copy templates into your own project.
- Adapt them — change variables, restructure sections, translate.
- Use them commercially.
- Build derivative gallery pages, training materials, or course content
  on top of them.

**What you must do:**

- **Attribute** the original work. The recommended attribution string is:

  > Adapted from `image2-workbench` template `<template_id>`, licensed
  > under CC BY 4.0. Source: https://github.com/image2-workbench/image2-workbench

- **Indicate changes** if you modified the template. A line in your
  README is sufficient.
- **Preserve the SPDX header** if you copy a file verbatim.

You do *not* need to apply CC BY 4.0 to your own derivative work — CC BY
4.0 is permissive about downstream relicensing of adaptations, as long as
the original attribution survives.

## Third-party corpus — per-record metadata

The `corpus/normalized/` directory holds metadata records ingested from
upstream sources (the OpenAI cookbook, GitHub repos, community posts).
Each record carries a `license_status` field that tells you what you may
do with it:

- **`clear`** — the upstream source has a known, redistributable open
  license (Apache-2.0, MIT, CC BY 4.0, etc). The record body can be
  used per the upstream license; the metadata itself is CC BY 4.0.
- **`ambiguous`** — the source's licensing is unclear, contradictory, or
  silent. We **do not redistribute the body** of these records, only
  the URL and shallow metadata you'd need to fetch the original.
- **`metadata_only`** — official documentation, posts under
  citation-only terms, or content explicitly marked
  "no redistribution". We store URL, title, author, date — never the
  prose. You can cite the URL; you must visit it for the actual
  content.

The default for any newly-ingested record is `metadata_only` until a
human review confirms a more permissive status. This is conservative on
purpose: false-positive openness is harder to walk back than
false-negative caution.

The full registry lives at `corpus/manifests/source_registry.yml`.

## Worked examples

### "I forked the CLI. Can I sublicense it under MIT?"

Yes. Apache-2.0 permits sublicensing under another OSI-approved license,
including MIT. You must:

- Keep a copy of the Apache-2.0 license in your fork's repository.
- Keep the `NOTICE` file (or its content) intact.
- Pass through the patent grant — Apache-2.0 includes an explicit patent
  grant from contributors, and that grant continues to apply to the
  Apache-2.0-licensed code even after you sublicense.

In practice: add `LICENSE-MIT` for your new code, keep `LICENSE` and
`NOTICE` for the inherited code, and document the boundary in your
README.

### "I copied a template prompt to my blog. How do I attribute?"

If you reproduce a CC BY 4.0 template in a blog post, include a line
like:

> Prompt template adapted from `business_swot_card` in
> `image2-workbench`, licensed under CC BY 4.0. See the project on
> GitHub for the full source.

If your post links the GitHub URL of the template file, that link
discharges the "indicate location" requirement. If your blog has a
generic credits page, you can put the attribution there as long as it's
discoverable from the post.

### "I want to ingest my own prompts from Twitter. What `license_status` should I use?"

Twitter (X) posts are not, by default, openly licensed. The platform's
ToS gives the site a broad licence for hosting; it does not give you a
licence for redistribution. So:

- **Default to `metadata_only`.** Capture the URL, the author handle,
  and the date. Do not store the prompt text in your normalized record.
- **Upgrade to `ambiguous`** only if the tweet's author has explicitly
  said "feel free to use this", and even then keep the body out of any
  public artifact.
- **Upgrade to `clear`** only if the tweet, or the author's bio, points
  to a clear open licence covering the content (rare on Twitter).

When in doubt, keep the URL and let the reader visit the original. That
costs you nothing and respects the source's authorship.

## Where each header goes

A new file should carry the SPDX header that matches its layer:

- Code (`*.py`, `*.toml`, `*.yml` under `src/` or `tests/`):
  `# SPDX-License-Identifier: Apache-2.0`
- Docs and templates (`*.md`, `*.yml` under `docs/` or `templates/`):
  `<!-- SPDX-License-Identifier: CC-BY-4.0 -->` (markdown) or
  `# SPDX-License-Identifier: CC-BY-4.0` (yaml)
- Corpus records: licensing is *per record*, encoded in the record's
  `license_status` field. No file-level SPDX header.

When in doubt, look at a neighbouring file in the same directory and
copy its header form.
