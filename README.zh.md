<!--
SPDX-License-Identifier: CC-BY-4.0
-->

# image2-workbench

> **image2-workbench 不止是 prompt 收藏夹，而是围绕 gpt-image-2 的
> spec-first 生产工作台。** 它把 prompt pack 变成可复现的 CLI、Skill 与
> 网页 ChatGPT 工作流，并提供成本估算、preflight 校验和本地运行 ledger。

> **状态：** v0.2.0 GitHub 源码 checkout 版本。项目仍处于 alpha，API
> 与模板格式后续可能调整；PyPI/wheel 打包留到 v0.3。

English: [README.md](./README.md)

## 为什么不止是 prompt 收藏夹？

精选 prompt 列表很有价值：它们是很好的灵感来源，也能快速展示模型吃什么
提示词。但当你需要在多个模板、尺寸、成本预算和模型 snapshot 之间复现同一
套工作流时，仅靠一份 markdown 会开始吃力。本仓库围绕三根支柱来补足这个
缺口：

- **成本可预测（`i2w cost` + `i2w batch`）。** 双轨成本模型 —— 官方
  `(size, quality)` 价格表 + 像素面积启发式兜底；提供 token-track 估算与
  Batch API 折扣路径（5 折，最长 24 小时）。详见
  [`docs/cost-modeling.md`](./docs/cost-modeling.md)。
- **错误分级（`i2w preflight` + 结构化错误信封）。** 7 个明确退出码
  （`AUTH`、`RATE_LIMIT`、`MODERATION_BLOCKED`、`VALIDATION`、
  `API_OTHER`、`INTERNAL`、`OK`），以及稳定的 `code` 字符串；shell
  脚本无需解析文字即可分支处理。本地参数校验 + 预 moderation
  在请求到达 OpenAI 之前就把"注定失败"的调用挡在门外。详见
  [`docs/error-codes.md`](./docs/error-codes.md)。
- **可观测（ledger）。** 每一次 render / edit / preflight / batch 调用
  都会向本地 ledger 追加一条 JSONL；`i2w ledger query` 按模板或
  snapshot 聚合，输出成功率与 p50/p95 时延；`i2w ledger drift`
  一条命令对比两个 snapshot 的回归情况。

prompt 收藏夹帮你探索；image2-workbench 保留这个价值，并把 prompt 变成
可执行、可审计、双语、可批处理的工作流。完整立场陈述见
[`docs/positioning.md`](./docs/positioning.md)。

## 三层形态

| 层 | 在哪运行 | 交付什么 |
|---|---|---|
| **L1 — 技能包** | Codex / Claude Code / Anthropic Skills / 任何支持 `SKILL.md` 的 agent | [`skills/gpt-image/`](./skills/gpt-image/) 极薄技能包，转发给 CLI |
| **L2 — Python CLI / SDK** | 本地终端、CI、自有 agent | 当前 checkout 中的 `i2w` 命令；包名 `image2-workbench` |
| **L3 — 纯模板** | 网页 ChatGPT、移动端、所有没有 Python 的环境 | [`docs/gallery/`](./docs/gallery/) 下的双语 markdown，可直接粘到对话框 |

L1 是 L2 的薄壳；L3 是 L2 编译器的产物 —— 同一份模板定义同时生成"可执行
命令"与"可粘贴 prompt"。

## 快速开始

clone 自己的 fork（或在本地 checkout 中工作）后：

```bash
cd image2-workbench && pip install -e ".[dev]"

i2w --help                 # 列出所有 verb
i2w doctor capabilities    # 探活：你的账户、组织、模型支持哪些能力
pytest -q                  # 跑单元 + smoke 测试
```

如果你是从 fork 中阅读，请把命令里的路径替换成你自己 fork 的 URL。

更完整的入门教程见 [`docs/getting-started.zh.md`](./docs/getting-started.zh.md)。

## V1 范围（4 个一级域、16 个模板）

- **business / 职场** — SWOT 卡、融资单页、LinkedIn 轮播、数据仪表板
- **academic / 学术科研** — 科学图、板书证明、多语言教育海报、期刊海报
- **uiux / 产品界面** — iOS 应用 mockup、网页仪表板、设计系统卡、小红书风格封面
- **anime / 娱乐** — 角色三视图、8 格漫画、城市电影海报、CCD 风格自拍

V0.3 会先补 wheel/PyPI 的模板打包，并扩展 prompt atlas、verified corpus
与 Skill pack 的故事。V2 会补 `industrial`、`ecommerce`、自动采集、插件
分发、TypeScript 端。

## 功能状态

| 组件 | 状态 |
|---|---|
| 项目骨架、分层许可、CI | 已完成 |
| CLI 命令面（`i2w` 11 个命令） | 已完成 |
| API 双后端（Images API + Responses API） | 已完成 |
| Spec-first 模板 DSL 与编译器 | 已完成 |
| 各域模板（4×4 = 16） | 已完成 |
| 语料检索 + provenance | 已完成 |
| 四类评测 rubric | 已完成 |
| 成本估算（官方 token + 启发式双轨） | 已完成 |
| 文档 + gallery 导出 | 已完成 |

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
