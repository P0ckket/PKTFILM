---
name: ingest-film-theory
description: 把电影理论/电影研究资料（书摘、论文、课堂笔记、访谈、影片分析）摄入为结构化知识库笔记（concept/theory/index），并可直接写入 knowledge/。
argument-hint: "[input_or_path] [optional_output_path]"
disable-model-invocation: true
allowed-tools: Read Grep Glob Write Edit
model: sonnet
effort: high
---

你正在执行“电影理论知识摄入（ingestion）”工作流。目标是把输入材料转化为可进入知识库的 Markdown 产物，而不是泛泛总结。

## 输入约定
- 第 1 个参数（$0）：输入材料。可以是：
  - 文件路径
  - 目录路径
  - 或者我直接粘贴的文本
- 第 2 个参数（$1，可选）：输出文件路径
  - 若未提供：先输出“建议路径 + 文件名”，再给出正文（不写盘）。

你收到的参数如下：
$ARGUMENTS

## 执行步骤（必须按顺序）
### 任务简报
先写 4 行以内：
- Goal / Non-goals / Inputs / Outputs

### 收集与读取材料
- 若 $0 是目录：用 Glob 列出其中的 .md/.txt，再选最相关文件 Read。
- 若 $0 是文件：直接 Read。
- 若 $0 是正文：不调用读取工具，把它当作唯一材料。

### 证据分层抽取
从材料中抽取并标注四层：
- 【原文/作者观点】
- 【学界常见解释】
- 【我的理解】
- 【你的推断】

### 决定产物粒度
默认策略：
- 先产出 1 个“主笔记”（type: theory 或 concept）
- 若材料包含 3 个以上可独立复用的概念，额外给出“拆分方案”

### 生成知识库笔记正文
输出的 Markdown 必须包含：
- 标题（H1）
- YAML frontmatter（至少包含：type / status / tags / sources）
- 一句话概括（TL;DR）
- 核心定义（Definitions）
- 关键术语表（Key terms）
- 历史语境 / 问题意识（Context & problem）
- 核心命题（Claims）
- 方法与分析入口（Method / How to use）
- 与其他概念的关系（Links & relations）
- 争议点与局限（Debates & limits）
- 导演实践启发（Directing takeaways）
- 容易混淆点（Common confusions）
- 待追问问题（Open questions）
- 建议双向链接（[[...]]）
- Changelog（若修改旧文件则必填）

### 写盘规则
- 若 $1 指向新文件：用 Write 创建。
- 若 $1 已存在：不要覆盖全文；用 Edit 追加“新增小节/修订小节 + Changelog”。

## 输出验收清单
- 是否把推断写成事实？（不得）
- 是否给出可链接的 [[概念]]？
- 是否包含“导演实践启发”且不空泛？
- 是否给出至少 3 个“待追问问题”？
- 若写盘：是否避免静默覆盖并记录 Changelog？
