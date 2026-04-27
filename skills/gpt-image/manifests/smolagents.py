# SPDX-License-Identifier: CC-BY-4.0
"""smolagents (HuggingFace) adapter — image2-workbench gpt-image skill.
Spec: https://huggingface.co/docs/smolagents/tutorials/tools
Usage:  from manifests.smolagents import gpt_image_tool
"""
from __future__ import annotations
import shutil, subprocess

def _build():  # pragma: no cover
    from smolagents import tool
    @tool
    def gpt_image(prompt_file: str, size: str = "1024x1024", quality: str = "medium") -> str:
        """Generate an image via image2-workbench (i2w render generate).
        Args:
            prompt_file: Path to a rendered prompt.md.
            size: Multiples of 16 (e.g. "1024x1024").
            quality: "low" | "medium" | "high".
        """
        if not shutil.which("i2w"):
            return "i2w not on PATH; pip install -e the workbench checkout."
        cp = subprocess.run(["i2w", "render", "generate", "--prompt-file", prompt_file,
                             "--size", size, "--quality", quality],
                            capture_output=True, text=True, timeout=300)
        return cp.stdout if cp.returncode == 0 else f"error({cp.returncode}): {cp.stderr}"
    return gpt_image

try:
    gpt_image_tool = _build()
except ImportError:
    gpt_image_tool = None
