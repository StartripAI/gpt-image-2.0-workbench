<!--
SPDX-License-Identifier: CC-BY-4.0
-->

# 快速上手

本文带你从一个干净的代码仓库走到第一张成图。除了能跑 Python，对你的账号
不做任何额外假设。

## 准备工作

- **Python 3.11 或更新版本。** 用 `python3 --version` 确认。编译器与运行
  时使用了较新的类型注解语法，CI 锁定在 3.11 与 3.12 上。
- **一个 POSIX 风格的终端。** Bash、zsh、fish 都行；下文示例以 bash 为准。
- **OpenAI API Key — 可选。** 模板渲染、能力探测、成本估算等子命令完全
  离线即可工作，只有 `i2w render generate` 与 `i2w render edit` 需要联网，
  并且要求你的组织（organization）已经通过了图像生成的**身份验证**。

如果确实要调用线上 API，每个终端会话里导出一次密钥即可：

```bash
export OPENAI_API_KEY="sk-..."
```

CLI 会通过 `python-dotenv` 自动读取当前目录的 `.env` 文件，因此把
`OPENAI_API_KEY=...` 放到项目本地的 `.env` 里也可以。

## 安装

在仓库根目录执行：

```bash
pip install -e ".[dev]"
```

`-e`（editable）让你对源码的改动立即生效。`[dev]` 这一组附加依赖会拉取
`pytest`、`ruff` 与 `mypy`。

如果你倾向用一个独立环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 校验

两条命令验证安装是否正常：

```bash
i2w --help     # 应当列出 11 个命令
pytest -q      # 单元测试与冒烟测试应当全部通过
```

输出里能看到 `catalog`、`template`、`render`、`batch`、`eval`、`cost`、
`doctor`、`preflight`、`ledger`、`gallery`、`version` 这 11 个子命令。
如果系统找不到 `i2w`，多半是 venv 没激活，重新执行上面那一步即可。

## 上手就跑的三条命令

请按顺序执行。三条命令都不会调用 OpenAI 接口，第一、二条命令甚至完全
不读你的本地仓库。

### 1. 探测当前账号的能力

```bash
i2w doctor capabilities
```

这条命令会逐项检查模型的能力面：可用的尺寸、质量等级、moderation 模式、
输出格式、组织是否已验证、是否暴露 `thinking` 参数，并打印一份整洁的
报告。如果没设置 API Key，它会回退到内置的静态默认值（来自模型说明
页），同时清晰地告诉你哪些项被跳过了。

每次换机器或换账号时先跑这一条，能避免后面被 401 折磨。

### 2. 列出可用模板

```bash
i2w template list --domain business
```

完全离线、瞬间出结果。它会扫描 `templates/business/*.yml`，按 V1 schema
做校验，然后打印每个模板的 id 和一句话简介。去掉 `--domain` 即可看到
全部四个领域。

### 3. 把模板渲染成一份可粘贴的提示词

```bash
i2w template render business_swot_card \
    --lang en \
    --vars templates/business/_vars_examples/swot_acme.yml \
    --out prompt.md
```

`--vars` 指向的是一个小 YAML 文件，里面填模板声明的变量（公司名、四象限
内容等）。每个 V1 模板都在 `templates/<domain>/_vars_examples/` 下提供了
一份可用的 demo 变量文件。各领域的 demo 文件名**并不统一** —— 完整的
"模板 → demo 变量"映射表见
[`tests/unit/test_all_templates_load.py::DEMO_VARS_MAP`](../tests/unit/test_all_templates_load.py)。
编译器会做变量替换，再走七段 DSL 编排，最终把渲染结果写到一份 `.md` 文
件里。这份文件你可以：

- 直接粘贴到 ChatGPT，靠对话生成图片，自己根本不需要联网调 API
  （下文路径 A）；或者
- 反过来喂给 `i2w render generate`，让 CLI 替你调 API
  （下文路径 B）。

v0.2 中 `--vars` 是必需参数。编译器不会假设安全的内置默认值；请传入随仓库
提供的 demo 变量文件，或传入你自己的变量文件。

## 通往一张成图的两条路径

### 路径 A — 纯网页版 ChatGPT

第 3 步渲染完成后，再也不需要 Python。输出是一份由 `--lang` 指定语言的
原始 prompt。打开 `prompt.md`，复制整个文件，粘贴进开启了图像生成的
ChatGPT 对话即可（Plus / Pro / Team 账号；gpt-image-2 就是 "create image"
工具背后的模型）。

这条路径：

- 不需要 API Key。
- 除了 ChatGPT 订阅本身，没有逐图费用。
- 适合不想管理凭据的设计师、学生、产品同学。

完整流程加两个示例，请看
[`chatgpt-web-mode.md`](./chatgpt-web-mode.md)。

### 路径 B — `i2w render generate`

当你想要落盘的产物文件、可复现的多次出图、批量生成或 CI 集成时，自己
驱动 API：

```bash
i2w render generate \
    --prompt-file prompt.md \
    --size 1536x1024 \
    --quality high \
    --out out/swot.png
```

输出文件会放在图像同级目录：

- `out/swot.png` — 图像本体。
- `out/swot.png.sidecar.json` — 旁路文件（sidecar），包含请求、响应里
  的 usage 数据，以及解析出的成本。

这条路径需要 `OPENAI_API_KEY`，并且你的组织已经验证过身份。如果还没
验证，API 会返回 403，CLI 把它收敛成一行清晰的提示，不会丢一长串
stack trace 给你。

## 常见问题排查

**`OPENAI_API_KEY is not set`。** 在 shell 中导出它，或者写到本地
`.env`。`i2w doctor capabilities` 会告诉你密钥是否被读到。

**`organization not verified for gpt-image-2`。** 在 OpenAI 控制台的
Settings → Organization 里做一次性验证。通常几分钟内通过；通过之前，
只有模板渲染和离线成本估算可以使用。

**`background: transparent is not supported on gpt-image-2`。** 模型只
接受 `auto` 或 `opaque`。校验器会提前拒绝 `transparent` 并给出清晰提
示；删掉这一项或改成 `auto` 即可。

**`size 3840x2160 is experimental`。** `2560×1440` 以上的尺寸虽然允许，
但被标记为 experimental — gpt-image-2 在最高分辨率下的稳定性还不齐整。
线上渲染前可以先跑 `i2w preflight prompt.md --size 3840x2160` 查看预警，
否则建议选 2K 区间的尺寸。

**`pytest -q` 报 import 错误。** 多半是没装 `[dev]` 附加依赖或 venv 没
激活。在 venv 里重跑 `pip install -e ".[dev]"`。

## 接下来读哪些文档

- [`prompt-craft.md`](./prompt-craft.md) — 七段式 DSL，以及如何写出真
  能让模型听懂的提示词。
- [`form-factors.md`](./form-factors.md) — 何时用 Skill bundle、何时用
  CLI、何时用纯提示词图册。
- [`chatgpt-web-mode.md`](./chatgpt-web-mode.md) — 网页版 ChatGPT 用户
  的零安装路径。
- [`licensing.md`](./licensing.md) — 分层的 Apache-2.0 + CC BY 4.0 协
  议在实际使用中怎么落地。
- [`gallery/index.md`](./gallery/index.md) — 四个 V1 领域的双语提示词
  图册。
