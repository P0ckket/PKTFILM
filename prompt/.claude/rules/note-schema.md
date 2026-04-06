# Note Schema（知识库笔记结构）

本文件定义 knowledge/ 下笔记的推荐结构与元数据，便于在 Obsidian / Notion / 全文检索工具中长期维护。

## YAML frontmatter（推荐字段）
每个知识库笔记建议包含：

type: concept | theory | comparison | director-note | index
status: seed | draft | stable | disputed
tags: [film-theory, directing, ...]
aliases: [可选的同义词/译名]
sources:
  - type: book | paper | lecture | interview | film
    cite: "作者. 标题. 年份/版本信息."
    locator: "chapter/page/timecode（如有）"
created: YYYY-MM-DD
updated: YYYY-MM-DD

## H2 级别的推荐章节（按类型选用）
### concept / theory
- TL;DR
- Definitions
- Key terms
- Context & problem
- Claims
- Method / How to use
- Links & relations
- Debates & limits
- Directing takeaways
- Common confusions
- Open questions
- [[Links]]
- Changelog

### comparison
- One-liners
- Matrix
- Non-overlapping differences
- Confusions
- Analysis recipe
- Exercises
- [[Links]]
- Changelog

### director-note
- The question it answers
- Decision mapping
- Exercises
- Anti-patterns
- Reflection prompts
- Seed list
- [[Links]]
- Changelog

## 命名建议
- 文件名尽量用 kebab-case，避免空格与特殊字符
- 同一概念的不同版本：优先在同文件用 Changelog 演化，不要到处复制
