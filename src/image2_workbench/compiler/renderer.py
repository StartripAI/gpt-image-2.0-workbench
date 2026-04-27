# SPDX-License-Identifier: Apache-2.0
"""Bilingual prompt renderer for the seven-section template DSL.

A single TemplateSpec yields a zh-CN prompt and an en prompt; the section
labels switch but the Jinja-evaluated body content is identical.
"""

from __future__ import annotations

from typing import Any

from jinja2 import Environment, StrictUndefined

from .schema import Spec, TemplateSpec, TextBlock

SUPPORTED_LANGS = ("zh-CN", "en")

_LABELS: dict[str, dict[str, str]] = {
    "zh-CN": {
        "subject": "主体",
        "action": "动作",
        "scene": "场景",
        "composition": "构图",
        "style": "风格",
        "text_header": "文字渲染（请按命名插槽精确呈现）",
        "preserve": "保留（编辑模式）",
        "negative": "禁止",
    },
    "en": {
        "subject": "Subject",
        "action": "Action",
        "scene": "Scene",
        "composition": "Composition",
        "style": "Style",
        "text_header": "Text to render exactly (chunked into named slots)",
        "preserve": "Preserve (edit mode only)",
        "negative": "NO",
    },
}


def _make_env() -> Environment:
    # StrictUndefined => any missing variable raises immediately at render time
    # rather than silently producing an empty string in the prompt.
    return Environment(
        undefined=StrictUndefined,
        autoescape=False,
        keep_trailing_newline=False,
        trim_blocks=False,
        lstrip_blocks=False,
    )


def _render_str(env: Environment, text: str, vars_: dict[str, Any]) -> str:
    return env.from_string(text).render(**vars_)


def _render_text_blocks(
    env: Environment,
    blocks: list[TextBlock],
    vars_: dict[str, Any],
) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for block in blocks:
        out.append((block.slot, _render_str(env, block.text, vars_)))
    return out


def _assemble(
    spec: Spec,
    rendered: dict[str, Any],
    lang: str,
) -> str:
    labels = _LABELS[lang]
    if lang == "zh-CN":
        body = [
            f"[1. {labels['subject']}] {rendered['subject']}",
            f"[2. {labels['action']}] {rendered['action']}",
            f"[3. {labels['scene']}] {rendered['scene']}",
            f"[4. {labels['composition']}] {rendered['composition']}",
            f"[5. {labels['style']}] {rendered['style']}",
        ]
    else:
        body = [
            f"[1. {labels['subject']}] {rendered['subject']}",
            f"[2. {labels['action']}] {rendered['action']}",
            f"[3. {labels['scene']}] {rendered['scene']}",
            f"[4. {labels['composition']}] {rendered['composition']}",
            f"[5. {labels['style']}] {rendered['style']}",
        ]

    if spec.text_blocks:
        body.append("")
        body.append(labels["text_header"] + ":")
        for slot, txt in rendered["text_blocks"]:
            # Templates already wrap text in their own quoting convention;
            # don't double-wrap here. See docs/error-codes.md for context.
            body.append(f"- {slot}: {txt}")

    if spec.preserve:
        body.append("")
        body.append(labels["preserve"] + ":")
        for item in spec.preserve:
            body.append(f"- {item}")

    if spec.negative:
        body.append("")
        body.append(f"{labels['negative']}: " + ", ".join(spec.negative))

    return "\n".join(body)


def render(template: TemplateSpec, vars_: dict[str, Any], lang: str) -> str:
    """Render the template into a single-language markdown prompt."""
    if lang not in SUPPORTED_LANGS:
        raise ValueError(f"unsupported lang {lang!r}; expected one of {SUPPORTED_LANGS}")
    if lang not in template.language_targets:
        raise ValueError(
            f"template {template.id!r} does not target {lang!r}; "
            f"language_targets={template.language_targets}"
        )
    env = _make_env()
    spec = template.spec
    rendered = {
        "subject": _render_str(env, spec.subject, vars_),
        "action": _render_str(env, spec.action, vars_),
        "scene": _render_str(env, spec.scene, vars_),
        "composition": _render_str(env, spec.composition, vars_),
        "style": _render_str(env, spec.style, vars_),
        "text_blocks": _render_text_blocks(env, spec.text_blocks, vars_),
    }
    return _assemble(spec, rendered, lang)


def render_both(template: TemplateSpec, vars_: dict[str, Any]) -> dict[str, str]:
    """Render both supported languages that the template targets."""
    out: dict[str, str] = {}
    for lang in template.language_targets:
        out[lang] = render(template, vars_, lang)
    return out


__all__ = ["SUPPORTED_LANGS", "render", "render_both"]
