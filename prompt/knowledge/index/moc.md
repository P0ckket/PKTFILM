---
name: 电影学习知识库 MOC(Map of Content)
description: 全库总地图,所有笔记按问题域进入的导航入口
type: index
status: stable
tags: [moc, index, navigation]
aliases: [总地图, master-index]
sources:
  - type: notebook
    cite: "故事元素积累6_merged.pdf"
    locator: "p.1-73"
created: 2026-04-06
updated: 2026-04-06
---

# 电影学习知识库 — Map of Content

> 这是 E:/director 知识库的**唯一入口地图**。按"问题"而非"人物"组织。
>
> **当前版本**：v1.0（基于《故事元素积累6》73页单材料，共 **36 篇笔记**）
> **下一步**：等待用户提供其他 PDF，走 ingest 工作流做增量扩展。

## 一、这个知识库想回答什么？

1. **一个故事应该被如何构造？** → [theory/](#叙事理论theory)
2. **一个人物应该被如何塑造？** → [concepts/character/](#人物)
3. **镜头/光/声/剪辑怎么选？** → [concepts/cinematic-language/](#视听语言)
4. **素材库怎么快速调用？** → [story-elements/](#故事元素素材库story-elements)
5. **电影案例怎么拆解？** → [case-studies/](#专题影片分析case-studies)
6. **艺考编讲故事怎么练？** → [director-notes/](#导演编剧练习director-notes)
7. **东方 vs 西方？类型 vs 类型？** → [comparison/](#比较卡comparison)

## 二、主题入口

### 叙事理论（theory）
- [三幕剧结构](../theory/three-act-structure.md)
- [十五节拍表（Save the Cat）](../theory/fifteen-beat-sheet.md)
- [类型叙事总览](../theory/genre-narratives-overview.md)
- [冲突六大类型](../theory/conflict-six-types.md)
- [主题表达六法](../theory/theme-expression-methods.md)
- [故事核与人物反差](../theory/story-core-and-contrast.md)

### 概念卡（concepts）

#### 人物
- [可怜/可信/可爱 三位一体](../concepts/character/character-trinity.md)
- [救猫咪时刻](../concepts/character/save-the-cat-moment.md)
- [人物弧光机制](../concepts/character/character-arc-mechanism.md)
- [欲望/目标/动机](../concepts/character/desire-goal-motivation.md)

#### 叙事机制
- [激励事件](../concepts/narrative/inciting-incident.md)
- [反差三层（人物/情节/场面）](../concepts/narrative/contrast-three-layers.md)

#### 视听语言
- [视听语言总览（景别/角度/光线/色彩/构图/运镜/蒙太奇/音响）](../concepts/cinematic-language/visual-language-overview.md)

#### 对话
- [六种台词技巧](../concepts/dialogue/dialogue-six-techniques.md)

#### 符号与意向
- [动物意向](../concepts/symbolism/animal-symbolism.md)
- [道具象征通则](../concepts/symbolism/prop-symbolism.md)

### 类型叙事（genre）
- [伙伴之情（Buddy Love）](../genre/buddy-love.md)
- [麻烦家伙（Dude with a Problem）](../genre/dude-with-a-problem.md)
- [变迁仪式（Rites of Passage）](../genre/rites-of-passage.md)
- [被制度化（Institutionalized）](../genre/institutionalized.md)
- [惊悚片要素](../genre/thriller-elements.md)

### 故事元素素材库（story-elements）
- [人物设计素材库（主角身份清单）](../story-elements/character-design-library.md)
- [反派与缺陷素材库](../story-elements/antagonist-and-flaws-library.md)
- [道具与六大用法素材库](../story-elements/props-and-six-uses-library.md)
- [场景与环境设置素材库](../story-elements/scene-and-setting-library.md)
- [悬念与冲突升级素材库](../story-elements/suspense-and-conflict-library.md)
- [情感与关系素材库](../story-elements/emotion-and-relation-library.md)
- [家庭冲突素材库](../story-elements/family-conflict-library.md)
- [医生职业素材库](../story-elements/profession-doctor.md)
- [警察职业素材库](../story-elements/profession-police.md)
- [穿着与性格表达素材库](../story-elements/costume-and-personality-library.md)

### 导演/编剧练习（director-notes）
- [五事件大纲法（艺考编讲故事）](../director-notes/five-event-outline.md)
- [反差发动机法（故事核设计）](../director-notes/contrast-engine-method.md)
- [道具生场景法（命题作文应对）](../director-notes/prop-to-scene-method.md)
- [艺考面试策略（编讲故事+锐评+故事接龙）](../director-notes/exam-interview-strategy.md)

### 专题影片分析（case-studies）
- [《霸王别姬》忠诚主题 + 五人物光谱](../case-studies/bawang-bieji.md)
- [《百元之恋》缺点驱动型弧光 + 五事件实操](../case-studies/baiyuan-zhi-lian.md)
- [《消失的爱人》双视角叙事 + 信息错位](../case-studies/xiaoshi-de-airen.md)

### 比较卡（comparison）
- [东西方故事价值标准（文以载道 vs 探索人性）](../comparison/east-west-story-standards.md)
- [伙伴之情 vs 被制度化](../comparison/buddy-love-vs-institutionalized.md)

### 反查索引（index）
- [本文件（MOC）](./moc.md)
- [影片案例索引](./film-case-index.md)
- [术语表（中英对照）](./term-glossary.md)

## 三、笔记状态约定

| 状态 | 含义 |
|---|---|
| `seed` | 仅骨架，等待素材 |
| `draft` | 有内容但未完成所有 H2 章节 |
| `stable` | 完整 v1 |
| `disputed` | 存在学界争议，已标注并列记录 |

## 四、α / Ω 运行约定

- 新摄入材料时走 `prompt/prompts/alpha-film-prompt.md` 生成器
- 优化旧笔记时走 `prompt/prompts/omega-film-prompt.md` 优化器
- 任何写盘都必须附 Changelog，不得静默覆盖

## 五、v1.0 统计

| 层 | 文件数 |
|---|---|
| theory/ | 6 |
| concepts/ | 10 |
| genre/ | 5 |
| story-elements/ | 10 |
| director-notes/ | 4 |
| comparison/ | 2 |
| case-studies/ | 3 |
| index/ | 3 |
| **合计** | **43 个入口（含 index）** |

## Changelog
- **2026-04-06 v1.1** — 所有 [[wiki-link]] 改为标准 Markdown 相对链接，兼容 VSCode 原生预览与 GitHub 渲染。
- **2026-04-06 v1.0** — 基于 故事元素积累6_merged.pdf 的 73 页全量内容建立完整 MOC。36 篇笔记 + 3 索引全部实际创建完毕。
