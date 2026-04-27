<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Skill compatibility matrix

## Project goal

The `gpt-image` Skill bundle that ships with `image2-workbench` is
designed to be a **portable, runtime-neutral** agent skill. The
canonical artifact is `skills/gpt-image/SKILL.md` (agentskills.io spec
— `name` + `description` in YAML frontmatter, body is Markdown
instructions). Every other manifest in `skills/gpt-image/manifests/`
is a thin adapter that points the host runtime at the same canonical
SKILL.md, so a single skill bundle can be discovered by Claude Code,
Codex, LangChain, smolagents, OpenClaw, Hermes, and any other runtime
that consumes structured agent skills.

## Support matrix

| Runtime              | Status        | Manifest                   | Install hint                                       | Source                                                                                                                |
| -------------------- | ------------- | -------------------------- | -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Claude Code          | `tested`      | `manifests/claude.json`    | `~/.claude/skills/gpt-image/`                      | https://code.claude.com/docs/en/skills                                                                                |
| Anthropic API Skills | `tested`      | `manifests/claude.json`    | upload via Skills API                              | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview                                            |
| OpenAI Codex         | `tested`      | `manifests/codex.yml`      | `~/.codex/skills/gpt-image/`                       | https://developers.openai.com/codex/skills                                                                            |
| LangChain            | `shim_ready`  | `manifests/langchain.py`   | `from manifests.langchain import gpt_image_tool`   | https://docs.langchain.com/oss/python/langchain/tools                                                                 |
| smolagents           | `shim_ready`  | `manifests/smolagents.py`  | `from manifests.smolagents import gpt_image_tool`  | https://huggingface.co/docs/smolagents/tutorials/tools                                                                |
| OpenClaw             | `theoretical` | `manifests/openclaw.json`  | `~/.openclaw/workspace/skills/gpt-image/`          | https://docs.openclaw.ai/tools/skills                                                                                 |
| Hermes Agent         | `theoretical` | `manifests/hermes.yml`     | Hermes Skills Hub (agentskills.io-compatible)      | https://hermes-agent.nousresearch.com/docs/ , https://agentskills.io                                                  |

Status legend:

- **tested** — bundle discovered and run end-to-end on this runtime.
- **shim_ready** — the manifest is a working Python adapter; only
  pre-flight smoke testing has been done. The runtime author should
  drop the shim into a real agent and verify.
- **theoretical** — the runtime documents itself as compatible with
  the agentskills.io spec (or a similar format), but we have not
  executed the bundle there. The shim is a starting point; runtime
  authors should adapt as needed.

## Per-runtime install instructions

### Claude Code (and Claude Desktop / Anthropic Skills API)

```bash
ln -s "$(pwd)/skills/gpt-image" ~/.claude/skills/gpt-image
```

The Anthropic spec only requires `name` + `description`; our SKILL.md
satisfies both, plus the optional `version`, `compatibility`, and
`runtimes` fields. See `manifests/claude.json` for entrypoint hints.

### OpenAI Codex CLI

```bash
ln -s "$(pwd)/skills/gpt-image" ~/.codex/skills/gpt-image
```

Codex reads `name` + `description` for discovery and only loads the
full SKILL.md body when a task matches — same progressive disclosure
as Anthropic. The optional `agents/openai.yaml` sidecar is not
required for our skill.

### LangChain

```python
from skills.gpt_image.manifests.langchain import gpt_image_tool
from langchain.agents import AgentExecutor
agent = AgentExecutor.from_agent_and_tools(..., tools=[gpt_image_tool])
```

The `@tool` decorator turns our `i2w render generate` invocation into
a LangChain `BaseTool`-compatible callable.

### smolagents (HuggingFace)

```python
from skills.gpt_image.manifests.smolagents import gpt_image_tool
from smolagents import CodeAgent, HfApiModel
agent = CodeAgent(tools=[gpt_image_tool], model=HfApiModel(...))
```

### OpenClaw

Drop the parent skill directory at `~/.openclaw/workspace/skills/gpt-image/`.
OpenClaw's spec (https://docs.openclaw.ai/tools/skills) reads the same
SKILL.md frontmatter and injects a compact XML stub into the system
prompt. Status is `theoretical` because we have not run the bundle
against an OpenClaw build end-to-end.

### Hermes Agent (NousResearch)

Hermes documents itself as agentskills.io-compatible
(https://agentskills.io). Our SKILL.md is written to the agentskills.io
spec, so dropping the bundle into the Hermes skills directory should
work; if the path differs, prefer the LangChain shim.

## Adding a new runtime

1. Add a new file under `skills/gpt-image/manifests/<runtime>.{json,yml,py}`.
   Keep it ≤30 lines — the shim is just a pointer to `../SKILL.md`.
2. Append a `compatibility:` entry to `skills/gpt-image/SKILL.md`
   frontmatter with status `tested`, `shim_ready`, or `theoretical`.
3. Update `docs/skill-compatibility.md` (this file) and the README in
   `skills/gpt-image/manifests/`.
4. Add or update a test case in `tests/unit/test_skill_compat.py` that
   verifies the new manifest parses and resolves.

## License

This documentation, the SKILL.md frontmatter, and every shim under
`skills/gpt-image/manifests/` are licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The underlying `image2-workbench` CLI is Apache-2.0. See `NOTICE` in
the repo root for full attribution.
