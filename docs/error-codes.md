<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Error codes

Every failure path in image2-workbench surfaces a structured
`ErrorEnvelope` with two stable identifiers:

- An **integer exit code** (one of seven), so shell wrappers can branch
  without parsing prose.
- A **stable string `code`** field (e.g. `"missing_api_key"`,
  `"transparent_bg_unsupported"`), so logs and the ledger can group
  failures across snapshots.

The envelope is rendered to stderr with a red exit-code label and any
attached `detail`, `docs_url`, or `cause`. The same fields are recorded
in the local ledger (`~/.image2/ledger.jsonl`) on the way out, so
`i2w ledger query` can later compute success rate and an
error-code breakdown.

## The seven exit codes

| Exit | Name                | Default `code`        | When it fires |
|-----:|---------------------|-----------------------|----------------|
| 0    | `OK`                | —                     | Command completed successfully. |
| 1    | `AUTH`              | `missing_api_key`     | Missing / invalid `OPENAI_API_KEY`, org not verified, scope mismatch. |
| 2    | `RATE_LIMIT`        | `rate_limited`        | OpenAI returned 429; tier limit hit; retry-after honored by the runtime. |
| 3    | `MODERATION_BLOCKED`| `moderation_blocked`  | `/v1/moderations` flagged the prompt or a post-generation filter rejected the output. |
| 4    | `VALIDATION`        | (caller-supplied)     | Local-side parameter validation refused the request before any API call. |
| 5    | `API_OTHER`         | `api_error`           | OpenAI 4xx/5xx that does not fit the buckets above. |
| 6    | `INTERNAL`          | `internal_error`      | Unhandled exception inside the workbench (a bug; please file). |

Exit codes 1 and 2 are *retryable in principle* (refresh the key, wait
for the rate-limit window). Exit codes 3 and 4 mean the call should not
be retried as-is. Exit code 5 is the bucket for "OpenAI said no in a
shape we don't fully recognise"; check the message before retrying.
Exit code 6 should only ever appear when the workbench itself is broken.

## Common `code` strings

The `code` field is intentionally a small, stable vocabulary so log
analysers and the ledger's `error_code_breakdown` can group across
snapshots without false negatives.

### Validation (exit 4)

| `code`                          | Common cause                                         | What to do |
|---------------------------------|------------------------------------------------------|------------|
| `prompt_file_missing`           | `--prompt-file` points to a non-existent path.       | Fix the path, or run `i2w template render` to produce one. |
| `transparent_bg_unsupported`    | `--background transparent` (rejected pre-flight).    | Use `auto` or `opaque`. |
| `invalid_background`            | `--background` is not one of `auto` / `opaque`.      | Pick a valid value. |
| `invalid_quality`               | `--quality` not in `low/medium/high/auto`.           | Pick a valid value. |
| `invalid_format`                | `--format` not in `png/jpeg/webp`.                   | Pick a supported format. |
| `invalid_moderation`            | `--moderation` not in `auto/low`.                    | Pick a valid value. |
| `missing_reference_image`       | `i2w render edit` invoked without `-i / --image`.    | Pass at least one reference image. |
| `size_too_large`                | Edge or pixel-count exceeds documented limits.       | Reduce the size; check `i2w doctor capabilities`. |
| `unsupported_parameter`         | Runtime adapter rejected a parameter (e.g. `input_fidelity`). | Drop the parameter; consult OpenAI docs. |

`i2w doctor capabilities` proactively lists known will-fail patterns
before you ever issue a call — read it before forecasting a sweep.

### Auth (exit 1)

| `code`            | Common cause                                  | What to do |
|-------------------|-----------------------------------------------|------------|
| `missing_api_key` | `OPENAI_API_KEY` unset / empty / malformed.   | `export OPENAI_API_KEY=...` or set in your secrets manager. |

### Rate limit (exit 2)

| `code`         | Common cause                                       | What to do |
|----------------|----------------------------------------------------|------------|
| `rate_limited` | Tier limit hit; OpenAI returned 429.               | Wait the suggested interval, or move to `i2w batch sweep` for non-urgent work (50% off, up to 24h). |

### Moderation (exit 3)

| `code`               | Common cause                              | What to do |
|----------------------|-------------------------------------------|------------|
| `moderation_blocked` | `/v1/moderations` flagged the prompt.     | Run `i2w preflight` to see the categories; tone the prompt down. |

### API other (exit 5)

| `code`       | Common cause                                  | What to do |
|--------------|-----------------------------------------------|------------|
| `api_error`  | OpenAI 4xx/5xx outside the buckets above.     | Check OpenAI status page; retry the call with `--think low` if applicable. |
| `bad_request`| OpenAI rejected the request body.             | Re-read the docs for the parameter mentioned in `cause`. |

### Internal (exit 6)

| `code`           | Common cause                                | What to do |
|------------------|---------------------------------------------|------------|
| `internal_error` | Unhandled exception inside the workbench.   | File an issue; include the `cause` and `detail` fields. |

## Reading an envelope

A typical CLI failure looks like this on stderr:

```
exit 4 (VALIDATION) transparent_bg_unsupported: background='transparent' is not supported by gpt-image-2; use 'auto' or 'opaque'
  docs: docs/error-codes.md#validation
```

The first line is parseable: `exit <int> (<NAME>) <code>: <message>`.
The indented lines below are optional `detail`, `docs_url`, and `cause`.

## Wiring into a shell

```bash
i2w render generate --prompt-file p.md --out out.png
case "$?" in
  0) echo ok ;;
  1) echo "auth — refresh OPENAI_API_KEY" ;;
  2) echo "rate-limited — backing off" ;;
  3) echo "moderation — rewrite prompt" ;;
  4) echo "validation — bug in calling code" ;;
  5) echo "api error — retry once" ;;
  6) echo "internal — file a bug" ;;
esac
```

## See also

- [`positioning.md`](./positioning.md) — why error granularity is one of
  the three pillars.
- `i2w doctor capabilities` — proactive listing of known will-fail
  patterns and the `code` strings they will raise.
- The ledger (`i2w ledger query --group-by template`) — historical
  `error_code_breakdown` per template / snapshot.
