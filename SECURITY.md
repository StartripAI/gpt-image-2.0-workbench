<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Security policy

This project is in **V1 alpha**. We take security seriously and welcome
careful disclosure from the community.

## Reporting a vulnerability

Please do **not** file public GitHub issues for suspected vulnerabilities.
Use one of the private channels below:

1. **Preferred — GitHub Security Advisory.** Open a draft advisory via
   the repository's "Security" tab → "Report a vulnerability". This routes
   directly to the maintainers, keeps the discussion private, and tracks
   a CVE if one is needed.
2. **Email backup.** If you cannot use GitHub Security Advisories, write
   to `<security-contact-here>` with a clear subject line beginning
   `[security]`. Maintainers replace this placeholder with a working
   address before announcing the project publicly.

We aim to **acknowledge new reports within 7 business days** and to share a
remediation timeline within 30 days. Coordinated disclosure timelines are
negotiable for severe issues — please indicate any constraints in your
initial report.

## Scope

Reports inside the following surface area will be triaged on the timeline
above:

- **Prompt-injection vectors** in compiled prompts, the seven-section DSL,
  or any template that ships with the repo. Examples: a template variable
  that escapes its quoted context, a sidecar that leaks an attacker's
  payload back into a downstream agent.
- **Supply-chain risk** in declared Python dependencies (anything pinned in
  `pyproject.toml`), GitHub Actions used by our workflows, and the
  pre-commit hook configurations under version control.
- **Secret leakage** in CLI logs, sidecar JSON files, error messages, or
  any artifact written next to a generated image. The CLI must never echo
  `OPENAI_API_KEY`, organization IDs, or short-lived auth tokens.
- **License-attribution failures** that cause a derivative work to ship
  without the upstream `LICENSE` / `LICENSE-CONTENT` / `NOTICE`, since
  this can expose downstream users to legal risk.

The following are explicitly **out of scope** for this repository's
security process:

- Vulnerabilities in the OpenAI `gpt-image-2` model itself, the Images API,
  or the Responses API. Report those upstream to OpenAI.
- Issues in third-party prompt collections that you point our compiler at.
  Validate untrusted prompts before feeding them to any agent.
- Risks introduced by user-supplied YAML variables. Treat your own
  `vars.yml` as untrusted input if you fetched it from elsewhere.

## Things we never want in a repro

When sending a report, please **strip the following before attaching any
log, screenshot, or input file**:

- `OPENAI_API_KEY`, `OPENAI_ORG_ID`, or any short-lived auth token. A
  redacted prefix (e.g. `sk-...XYZ`) is fine when the issue is about how
  a key is handled.
- OpenAI organization IDs that identify a private workspace.
- Real customer or end-user data — names, emails, internal documents,
  proprietary roadmap details. Synthesize a minimal repro instead.
- Copyrighted images you do not have rights to redistribute. Use an image
  you own, or a clearly-labeled placeholder.

If a repro genuinely requires sensitive data, mention that in the initial
contact and we will arrange a private channel.

## Supported versions

| Version | Supported |
|---------|-----------|
| `main` (V1 alpha) | yes |
| Tagged releases | not yet — first tagged release pending |

While the project is in V1 alpha, only the `main` branch receives security
fixes. Once we cut tagged releases, this table will be updated to reflect
the supported window.

## Acknowledgments

We will credit reporters in `NOTICE` (or the relevant release notes)
unless you ask to remain anonymous. Thank you for helping keep
image2-workbench safe to use.
