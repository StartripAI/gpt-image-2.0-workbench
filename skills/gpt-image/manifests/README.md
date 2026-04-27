<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# gpt-image manifests

This directory holds platform-specific shim files that let the
`gpt-image` Skill bundle (one parent directory up) be discovered and
installed by agent runtimes beyond Claude Code / Codex.

The `SKILL.md` next to this directory is the canonical, runtime-neutral
artifact (agentskills.io spec). The shims below are minimum-viable
adapters that point each runtime at it.

## Files

| File              | Runtime                    | Status      |
| ----------------- | -------------------------- | ----------- |
| `claude.json`     | Claude Code, Anthropic API | tested      |
| `codex.yml`       | OpenAI Codex CLI / API     | tested      |
| `langchain.py`    | LangChain (BaseTool)       | shim_ready  |
| `smolagents.py`   | HuggingFace smolagents     | shim_ready  |
| `openclaw.json`   | OpenClaw runtime           | theoretical |
| `hermes.yml`      | Hermes Agent (NousResearch)| theoretical |

## Install (per runtime)

### Claude Code / Anthropic Skills
```bash
ln -s "$(pwd)/skills/gpt-image" ~/.claude/skills/gpt-image
```

### OpenAI Codex
```bash
ln -s "$(pwd)/skills/gpt-image" ~/.codex/skills/gpt-image
```

### LangChain
```python
from skills.gpt_image.manifests.langchain import gpt_image_tool
agent = AgentExecutor.from_agent_and_tools(..., tools=[gpt_image_tool])
```

### smolagents
```python
from skills.gpt_image.manifests.smolagents import gpt_image_tool
agent = CodeAgent(tools=[gpt_image_tool], model=HfApiModel(...))
```

### OpenClaw / Hermes (theoretical)
Drop the parent skill directory at `~/.openclaw/workspace/skills/gpt-image/`
or the equivalent Hermes path. Both runtimes claim agentskills.io
compatibility — see `docs/skill-compatibility.md` in the repo root for
the latest references.

## Adding a runtime

1. Add a new shim file here (≤30 lines).
2. Append a `compatibility:` entry in `../SKILL.md` frontmatter.
3. Update `tests/unit/test_skill_compat.py` and `docs/skill-compatibility.md`.
