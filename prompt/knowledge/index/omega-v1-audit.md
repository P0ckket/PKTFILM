---
name: Ω 自检报告 v1.0
description: 知识库 v1.0 完成后的全量审计——覆盖率、质量、缺口、扩展建议
type: index
status: stable
tags: [omega, audit, v1]
created: 2026-04-06
updated: 2026-04-06
---

# Ω 自检报告 v1.0

> 基于 `prompt/prompts/omega-film-prompt.md` 优化器的自检逻辑，对 v1.0 知识库做全量审计。

## 一、覆盖率审计

### 源材料覆盖
| PDF 页码范围 | 主题 | 是否覆盖 | 对应笔记 |
|---|---|---|---|
| p.1 | 主角设置（可怜/可信/可爱） | ✅ | character-trinity, character-design-library |
| p.2-3 | 故事元素（升级/愧疚/喜剧） | ✅ | emotion-and-relation-library, suspense-and-conflict-library |
| p.4-5 | 故事主题 + 表达六法 | ✅ | theme-expression-methods, family-conflict-library |
| p.6-7 | 三幕剧 + 激励事件 | ✅ | three-act-structure, inciting-incident |
| p.8-9 | 春节档 + 冯小刚 + 十大趋势 | ⚠️ 部分 | 趋势关键词未独立成卡 |
| p.10-13 | 消失的爱人 + 惊悚片 | ✅ | xiaoshi-de-airen, thriller-elements |
| p.14-19 | 主角身份 + 底层/英雄/女性/儿童 | ✅ | character-design-library |
| p.20-23 | 伙伴之情 + 麻烦家伙 + 变迁仪式 + 被制度化 | ✅ | 4 genre files |
| p.24 | 六种台词技巧 | ✅ | dialogue-six-techniques |
| p.25-27 | 视听语言 | ✅ | visual-language-overview |
| p.28 | 类型叙事总结 + 冲突六类 | ✅ | genre-narratives-overview, conflict-six-types |
| p.29-30 | 十五节拍 | ✅ | fifteen-beat-sheet |
| p.31 | 霸王别姬 | ✅ | bawang-bieji |
| p.32-36 | 故事元素散装 | ✅ | 多个 story-elements 文件 |
| p.37-39 | 动物意向 | ✅ | animal-symbolism |
| p.40 | 故事核与反差 | ✅ | story-core-and-contrast, contrast-engine-method |
| p.41-43 | 五事件大纲 + 面试策略 | ✅ | five-event-outline, exam-interview-strategy |
| p.44-47 | 道具八法练习 | ✅ | props-and-six-uses-library, prop-to-scene-method |
| p.48-49 | 百元之恋 | ✅ | baiyuan-zhi-lian, character-arc-mechanism |
| p.50-52 | 医生素材 | ✅ | profession-doctor |
| p.53-57 | 道具素材（信/手抖/桥等） | ✅ | props-and-six-uses-library |
| p.58-59 | 警察素材 | ✅ | profession-police |
| p.60 | 穿着与性格 | ✅ | costume-and-personality-library |
| p.61-73 | 道具素材（大量散装） | ✅ | props-and-six-uses-library |

**覆盖率**：73 页中 **71 页已覆盖**（97%）。p.8-9（春节档/十大趋势）仅部分覆盖。

### 笔记 Schema 合规性
| 检查项 | 合规率 | 说明 |
|---|---|---|
| YAML frontmatter | 36/36 (100%) | 所有笔记都有 type/status/tags/sources |
| 证据分层标注 | 30/36 (83%) | 索引类文件无需标注 |
| Changelog | 36/36 (100%) | 全部有 |
| [[Wiki-link]] | 36/36 (100%) | 所有笔记都有交叉引用 |
| kebab-case 文件名 | 36/36 (100%) | 全部合规 |
| 中文+英文括号术语 | 36/36 (100%) | 全部合规 |

## 二、质量评估

### 强项
1. **story-elements/ 层质量最高**——扁平化素材库风格保持一致，每个库都有"使用建议/checklist"
2. **director-notes/ 实操性强**——五事件大纲 + 反差发动机 + 道具生场景 + 面试策略形成完整的"艺考工具链"
3. **case-studies/ 理论联系实际**——每个案例都用本库的理论框架做了二次分析
4. **交叉引用网络密集**——平均每篇笔记 5-7 个 [[link]]

### 弱项
1. **concepts/ 的视听语言只有一篇总览**——景别/角度/光线/色彩/构图/运镜/蒙太奇/音响 未拆分成独立卡
2. **comparison/ 只有 2 篇**——原计划的"生活对话 vs 故事对话""反差 vs 冲突"未建
3. **genre/ 缺 5 个 Snyder 类型**——金羊毛/愚者成功/超级英雄/鬼怪屋/魔法奇迹 未建（原笔记无详细材料）
4. **p.8-9 的"十大互联网文娱趋势"未整合**——这部分更偏行业分析而非理论

## 三、缺口清单（按优先级排序）

### P1（下次对话建议做）
| 缺口 | 建议 |
|---|---|
| 视听语言拆分卡 | 将 visual-language-overview 中的 7 类拆成独立 concept 卡 |
| 生活对话 vs 故事对话 comparison 卡 | p.11 的对话对比已有素材，建 comparison 卡 |

### P2（有新 PDF 时做）
| 缺口 | 建议 |
|---|---|
| Snyder 剩余 5 类型 | 需要额外材料（Save the Cat 原书）才能建 |
| 音响/声音专项 | 原笔记对声音的讨论偏少，需新材料 |
| 剪辑/节奏专项 | 原笔记几乎未涉及剪辑理论 |
| 观众位置/认知理论 | 原笔记无这部分 |

### P3（长期扩展）
| 缺口 | 建议 |
|---|---|
| 更多 case-studies | 每引入一部新片分析就建一卡 |
| 导演个人风格卡 | 陈凯歌/李安/冯小刚/宫崎骏等 |
| 中国电影史时间线 | 需系统性材料 |
| 编剧软件/工具卡 | Final Draft / Fade In 等 |

## 四、v1.0 → v1.1 的建议行动

1. 用户提供**下一批 PDF** → 走 α 生成器增量 ingest
2. 对现有 36 篇笔记中 status=draft 的 → 逐篇走 Ω 优化器补全缺失的 H2 章节
3. 视听语言拆分 → 7 篇独立 concept 卡
4. 补建 2 篇 comparison 卡

## Changelog
- **2026-04-06 v1.0** — 首次 Ω 自检。覆盖率 97%，36 篇笔记全部实际创建。
