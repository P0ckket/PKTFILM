---
name: compare-film-theories
description: 比较两个或多个电影理论/概念/学者（film theory concepts），输出可复习的比较卡（comparison note），并可写入 knowledge/。
argument-hint: "[theory_A_or_path] [theory_B_or_path] [optional_output_path]"
disable-model-invocation: true
allowed-tools: Read Grep Glob Write Edit
model: sonnet
effort: high
---

你正在执行“电影理论比较（comparison）”工作流。目标是帮助我在概念层面建立清晰区分与可迁移的分析框架。

你收到的参数如下：
$ARGUMENTS

## 输入约定
- $0：理论 / 概念 A
- $1：理论 / 概念 B
- $2（可选）：输出路径
- 若 $0/$1 是名称而非路径：
  - 先用 Grep/Glob 在 knowledge/ 中寻找最相关笔记
  - 找不到就问我是否允许先基于常见框架生成草案（标“待核实”）

## 比较维度（默认必须覆盖）
- 研究对象（object of study）
- 核心问题（central question）
- 方法论与证据类型（method & evidence）
- 对电影本质/媒介的假设（ontology / medium specificity）
- 对形式与现实的立场（form vs realism）
- 对观众位置的理解（spectatorship）
- 对导演实践的启发（directing implications）
- 局限与批评（limits & critiques）
- 适用场景与不适用场景（when to use / when not）

## 输出格式（必须可直接保存）
- H1 标题：`A vs B：<一句话题眼>`
- YAML frontmatter：type / status / tags / sources
- 各理论一句话定位（one-liners）
- 对照表（matrix）
- 根本差异（non-overlapping differences）
- 容易混淆点（confusions）
- 典型文本 / 代表论述
- 分析 recipe
- 导演训练：2-3 个练习（exercises）
- 双向链接建议（[[...]]）
- Changelog（若写盘或修改必填）

## 写盘规则
- 若提供输出路径：新建用 Write，已有用 Edit 追加，不静默覆盖
- 若未提供：只输出“建议路径 + 正文”，不写盘

## 输出验收清单
- 是否指出“看似相同但不可混同”的点？
- 是否给出至少 1 个 matrix？
- 是否把“导演启发”写成可执行练习，而不是口号？
