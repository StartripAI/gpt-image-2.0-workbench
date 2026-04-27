"""image2-workbench: a multi-surface OpenAI gpt-image-2 workbench.

Three form factors share a single Python core:
  L1 — Skill bundle (skills/gpt-image/) usable in Codex / Claude Code / Anthropic Skills
  L2 — Python CLI (`i2w`) and SDK for local terminals, CI, and custom agents
  L3 — Bilingual prompt templates that can be copy-pasted into web ChatGPT
       without any runtime
"""

__version__ = "0.1.0"

try:
    from .compiler.schema import TemplateSpec  # noqa: F401  re-export when ready
except ImportError:
    pass

__all__ = ["__version__"]
