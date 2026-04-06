---
name: build-director-study-note
description: 把电影理论或影片分析材料转译为“导演学习笔记（director study note）”，强调镜头/场面调度/声音/剪辑等可实践决策，并可写入 knowledge/。
argument-hint: "[input_or_path] [optional_output_path]"
disable-model-invocation: true
allowed-tools: Read Grep Glob Write Edit
model: sonnet
effort: high
---

你正在执行“导演学习转译（director-oriented translation）”工作流：把理论从“讲得通”变成“拍得出来 / 分析得动”。

你收到的参数如下：
$ARGUMENTS

## 输入约定
- $0：输入材料（文件 / 目录 / 正文）
- $1（可选）：输出路径

## 先做任务简报（6 行以内）
- Goal / Non-goals / Inputs / Outputs / Context / Risks

## 产出类型选择（必须明确选择其一）
A) 影片分析导向（analysis-first）
B) 创作导向（practice-first）

若用户未说明，默认选择 B，并问 1 个关键问题：题材 / 类型 / 限制是什么。

## 输出结构（必须可直接保存）
- H1：主题
- YAML frontmatter：type: director-note / status / tags / sources
- 这条理论到底在回答什么问题（the question it answers）
- 概念拆解（concept breakdown）
- 导演决策映射（decision mapping）
  - 镜头与景别（shot size / lensing as language）
  - 场面调度（mise-en-scène / blocking）
  - 表演引导（performance direction）
  - 剪辑与节奏（editing / rhythm）
  - 声画关系（sound-image relation）
  - 叙事视角（narration / POV）
- 练习卡（exercises）：至少 3 个，可在 1-2 小时内完成
- 反例与误区（anti-patterns）：至少 3 条
- 复盘问题（reflection prompts）：至少 5 条
- 下一步阅读 / 看片种子列表（seed list）：最多 8 条
- 双向链接建议（[[...]]）
- Changelog（若写盘或修改必填）

## 写盘规则
- 若提供输出路径：新建 Write，已有 Edit 追加，不静默覆盖
- 若未提供：输出“建议路径 + 正文”，不写盘

## 输出验收清单
- 是否至少给出 3 个可执行练习？
- 是否明确了反例与误区？
- 是否把术语转成导演可用的决策语言？
