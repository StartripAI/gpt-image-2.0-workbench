<!--
SPDX-License-Identifier: CC-BY-4.0
-->

# image2-workbench

一个多形态的 OpenAI gpt-image-2 工作台：**技能（Skill）+ 命令行（CLI）+ 双语
提示词模板**，覆盖 `商业 / 学术 / UI-UX / 动漫` 四类核心场景。

> **状态：** V1 alpha — 持续开发中。在第一个正式 tag 之前，API 与模板格式
> 仍可能调整。

English: [README.md](./README.md)

## 为什么做这个

- OpenAI 在 2026-04-21 发布 `gpt-image-2`（snapshot
  `gpt-image-2-2026-04-21`），可以胜任多语言原生排版、参考图编辑、连续叙事、
  UI 高保真原型、学术插图等真实场景；但社区生态目前还是一堆零散 prompt 仓库，
  没有模板 DSL、校验、评测和成本估算。
- 不少现有仓库甚至和官方文档相左 —— 例如默认把 `moderation` 设为 `low`、
  把"2K"写死为上限。
- 很多人最终是在**网页 ChatGPT** 而不是 Python 终端里使用，他们用不上 CLI，
  所以我们需要一种"无 runtime 也能跑"的模板形态，可以直接复制粘贴到对话框。

## 三层形态

| 层 | 在哪运行 | 交付什么 |
|---|---|---|
| **L1 — 技能包** | Codex / Claude Code / Anthropic Skills / 任何支持 `SKILL.md` 的 agent | [`skills/gpt-image/`](./skills/gpt-image/) 极薄技能包，转发给 CLI |
| **L2 — Python CLI / SDK** | 本地终端、CI、自有 agent | `i2w` 命令；包名 `image2-workbench` |
| **L3 — 纯模板** | 网页 ChatGPT、移动端、所有没有 Python 的环境 | [`docs/gallery/`](./docs/gallery/) 下的双语 markdown，可直接粘到对话框 |

L1 是 L2 的薄壳；L3 是 L2 编译器的产物 —— 同一份模板定义同时生成"可执行
命令"与"可粘贴 prompt"。

## 快速开始

```bash
git clone https://github.com/image2-workbench/image2-workbench.git
cd image2-workbench
pip install -e ".[dev]"

i2w --help                 # 列出所有 verb
i2w doctor capabilities    # 探活：你的账户、组织、模型支持哪些能力
pytest -q                  # 跑单元 + smoke 测试
```

更完整的入门教程见 [`docs/getting-started.zh.md`](./docs/getting-started.zh.md)。

## V1 范围（4 个一级域、16 个模板）

- **business / 职场** — SWOT 卡、融资单页、LinkedIn 轮播、数据仪表板
- **academic / 学术科研** — 科学图、板书证明、多语言教育海报、期刊海报
- **uiux / 产品界面** — iOS 应用 mockup、网页仪表板、设计系统卡、小红书风格封面
- **anime / 娱乐** — 角色三视图、8 格漫画、城市电影海报、CCD 风格自拍

V2 会补 `industrial`、`ecommerce`、自动采集、插件分发、TypeScript 端。

## 功能状态

| 组件 | 状态 |
|---|---|
| 项目骨架、分层许可、CI | 已完成 |
| CLI 命令面（`i2w` 八个 verb） | 进行中 |
| API 双后端（Images API + Responses API） | 进行中 |
| Spec-first 模板 DSL 与编译器 | 进行中 |
| 各域模板（4×4 = 16） | 进行中 |
| 语料检索 + provenance | 进行中 |
| 四类评测 rubric | 进行中 |
| 成本估算（官方 token + 启发式双轨） | 进行中 |
| 文档 + gallery 导出 | 进行中 |

## 许可

代码（`src/`、`tests/`、`scripts/`、`.github/`）使用 **Apache-2.0**，见
[`LICENSE`](./LICENSE)。

模板与文档（`templates/`、`docs/`、`README*`）使用 **CC BY 4.0**，见
[`LICENSE-CONTENT`](./LICENSE-CONTENT)。

`corpus/normalized/` 下的第三方 prompt 记录逐条携带许可元数据，见
[`corpus/manifests/source_registry.yml`](./corpus/manifests/source_registry.yml)。

致谢与方法论来源说明见 [`NOTICE`](./NOTICE)。

## 参与开发

请先读 [`AGENTS.md`](./AGENTS.md)：它说明了文件归属、禁止的反模式（不许从
其他仓库 copy 文案、不许使用已废弃参数）、以及 V1 的完成定义。

## 来源声明

本仓库仅在**结构层面**借鉴
[`wuyoscar/gpt_image_2_skill`](https://github.com/wuyoscar/gpt_image_2_skill)
（CC BY 4.0）的目录组织方式（Skill + CLI + 参考文档三层分离）。**没有任何
源码、prompt 原文或 README 段落被复制。** 参数边界与默认值来自 OpenAI 官方
文档。完整声明见 `NOTICE`。
