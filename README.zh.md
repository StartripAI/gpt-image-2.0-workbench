<!--
SPDX-License-Identifier: CC-BY-4.0
-->

# GPT Image 2.0 Workbench

面向可复现图像生成工作流的 spec-first 工作台，而不是只靠一次性 prompt 运气。

[English](./README.md)

![Version](https://img.shields.io/badge/version-v0.2.0-0f766e)
![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)
![Tests](https://img.shields.io/badge/tests-375%20passing-15803d)
![CLI](https://img.shields.io/badge/CLI-11%20commands-334155)
![License](https://img.shields.io/badge/license-Apache--2.0%20%2B%20CC--BY--4.0-6b7280)

![GPT Image 2.0 Workbench hero](./docs/assets/readme-hero.svg)

---

## 一眼看懂

| 项目 | 内容 |
|---|---|
| 核心思路 | 结构化 spec 编译成可运行 prompt、校验、渲染与 ledger 记录 |
| 模板规模 | 16 个双语模板，覆盖 business / academic / UI/UX / anime |
| 使用形态 | Skill bundle、Python CLI/SDK、纯 markdown prompt gallery |
| 生产控制 | 成本估算、Batch API dry-run payload、preflight 校验、结构化错误、本地 ledger |
| 发布状态 | `v0.2.0` 源码 checkout alpha；PyPI/wheel 打包留到 `v0.3` |

---

## 这个仓库解决什么问题

当 prompt pack 需要变成可执行工作流时，用这个仓库：

- **一次写成 spec。** 把主体、构图、精确文本块、负面约束、尺寸、质量与语言目标放进 YAML。
- **花钱前先检查。** 在真正调用 API 前校验尺寸、背景、未支持参数，估算成本，并生成 Batch API JSONL payload。
- **留下证据。** render / edit / preflight / batch 工作流可以写 sidecar 和 ledger，后续能查成功率、成本、错误分布。
- **跨形态交付。** 同一份模板可以变成 CLI 命令、agent Skill 动作，或可直接粘贴到网页对话框的 prompt。

![Spec-first workflow map](./docs/assets/workflow-map.svg)

---

## 安装

`v0.2.0` 是 GitHub/source-checkout 版本。直接从仓库安装：

```bash
git clone https://github.com/StartripAI/gpt-image-2.0-workbench.git
cd gpt-image-2.0-workbench

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

需要真实渲染时再设置 API key：

```bash
export OPENAI_API_KEY="sk-..."
```

离线模板编译、成本估算、gallery 构建、本地校验都不需要 live API 调用。

---

## 快速使用

把一个双语模板编译成英文 prompt：

```bash
i2w template render business_swot_card \
  --lang en \
  --vars templates/business/_vars_examples/swot_acme.yml \
  --out out/swot.prompt.md
```

调用图像 API 前先校验：

```bash
i2w preflight out/swot.prompt.md --template-id business_swot_card --no-moderation-api
```

比较不同尺寸与质量的成本：

```bash
i2w cost compare --size 1024x1024,1536x1024 --quality low,medium,high
```

先预览批量 payload，默认不花钱：

```bash
i2w batch sweep \
  --template business_swot_card \
  --vars templates/business/_vars_examples/swot_acme.yml \
  --route batch-api \
  --dry-run
```

确认后再生成：

```bash
i2w render generate \
  --prompt-file out/swot.prompt.md \
  --template-id business_swot_card \
  --size 1536x1024 \
  --quality medium \
  --out out/swot.png
```

![Production controls](./docs/assets/production-controls.svg)

---

## 命令面

| 命令 | 用途 |
|---|---|
| `i2w catalog` | 搜索和列出模板 / catalog 元数据 |
| `i2w template` | 列模板，并把 YAML spec 编译成 prompt |
| `i2w render` | 带本地校验和 sidecar 的生成 / 编辑 |
| `i2w batch` | 构建安全 batch sweep 和 Batch API job |
| `i2w eval` | 运行 prompt 层 rubric 检查 |
| `i2w cost` | 估算、对比、预算图像生成成本 |
| `i2w doctor` | 检查本地与运行时能力假设 |
| `i2w preflight` | API 调用前拒绝已知错误请求 |
| `i2w ledger` | 查询成功率、时延、成本和错误分布 |
| `i2w gallery` | 从模板生成可复制的 markdown gallery |
| `i2w version` | 打印当前 workbench 版本 |

---

## 模板 gallery

| 领域 | 模板数 | Gallery |
|---|---:|---|
| Business | 4 | [`docs/gallery/business.md`](./docs/gallery/business.md) |
| Academic | 4 | [`docs/gallery/academic.md`](./docs/gallery/academic.md) |
| UI/UX | 4 | [`docs/gallery/uiux.md`](./docs/gallery/uiux.md) |
| Anime | 4 | [`docs/gallery/anime.md`](./docs/gallery/anime.md) |

每个 gallery 页面都由 CLI 使用的同一份模板生成，因此“复制粘贴路径”和“可执行
工作流”不会各自漂移。

---

## 为什么有用

prompt 示例适合探索；workbench 解决复现。

`image2-workbench` 聚焦长期可用的生产环节：spec 版本化、编译期校验、明确
成本、安全批量预览、结构化失败模式、以及 ledger 支撑的可观测性。

推荐阅读：

- [`docs/getting-started.zh.md`](./docs/getting-started.zh.md)
- [`docs/form-factors.md`](./docs/form-factors.md)
- [`docs/error-codes.md`](./docs/error-codes.md)
- [`docs/cost-modeling.md`](./docs/cost-modeling.md)
- [`docs/positioning.md`](./docs/positioning.md)

---

## 许可

代码（`src/`、`tests/`、`scripts/`、`.github/`）使用 **Apache-2.0**。
模板与文档（`templates/`、`docs/`、`README*`）使用 **CC BY 4.0**。

见 [`LICENSE`](./LICENSE)、[`LICENSE-CONTENT`](./LICENSE-CONTENT) 与
[`LICENSE-CC-BY-4.0`](./LICENSE-CC-BY-4.0)。
