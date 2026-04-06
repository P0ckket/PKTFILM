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
- [[../theory/three-act-structure]] 三幕剧结构
- [[../theory/fifteen-beat-sheet]] 十五节拍表（Save the Cat）
- [[../theory/genre-narratives-overview]] 类型叙事总览
- [[../theory/conflict-six-types]] 冲突六大类型
- [[../theory/theme-expression-methods]] 主题表达六法
- [[../theory/story-core-and-contrast]] 故事核与人物反差

### 概念卡（concepts）

#### 人物
- [[../concepts/character/character-trinity]] 可怜/可信/可爱 三位一体
- [[../concepts/character/save-the-cat-moment]] 救猫咪时刻
- [[../concepts/character/character-arc-mechanism]] 人物弧光机制
- [[../concepts/character/desire-goal-motivation]] 欲望/目标/动机

#### 叙事机制
- [[../concepts/narrative/inciting-incident]] 激励事件
- [[../concepts/narrative/contrast-three-layers]] 反差三层（人物/情节/场面）

#### 视听语言
- [[../concepts/cinematic-language/visual-language-overview]] 视听语言总览（景别/角度/光线/色彩/构图/运镜/蒙太奇/音响）

#### 对话
- [[../concepts/dialogue/dialogue-six-techniques]] 六种台词技巧

#### 符号与意向
- [[../concepts/symbolism/animal-symbolism]] 动物意向
- [[../concepts/symbolism/prop-symbolism]] 道具象征通则

### 类型叙事（genre）
- [[../genre/buddy-love]] 伙伴之情（Buddy Love）
- [[../genre/dude-with-a-problem]] 麻烦家伙（Dude with a Problem）
- [[../genre/rites-of-passage]] 变迁仪式（Rites of Passage）
- [[../genre/institutionalized]] 被制度化（Institutionalized）
- [[../genre/thriller-elements]] 惊悚片要素

### 故事元素素材库（story-elements）
- [[../story-elements/character-design-library]] 人物设计素材库（主角身份清单）
- [[../story-elements/antagonist-and-flaws-library]] 反派与缺陷素材库
- [[../story-elements/props-and-six-uses-library]] 道具与六大用法素材库
- [[../story-elements/scene-and-setting-library]] 场景与环境设置素材库
- [[../story-elements/suspense-and-conflict-library]] 悬念与冲突升级素材库
- [[../story-elements/emotion-and-relation-library]] 情感与关系素材库
- [[../story-elements/family-conflict-library]] 家庭冲突素材库
- [[../story-elements/profession-doctor]] 医生职业素材库
- [[../story-elements/profession-police]] 警察职业素材库
- [[../story-elements/costume-and-personality-library]] 穿着与性格表达素材库

### 导演/编剧练习（director-notes）
- [[../director-notes/five-event-outline]] 五事件大纲法（艺考编讲故事）
- [[../director-notes/contrast-engine-method]] 反差发动机法（故事核设计）
- [[../director-notes/prop-to-scene-method]] 道具生场景法（命题作文应对）
- [[../director-notes/exam-interview-strategy]] 艺考面试策略（编讲故事+锐评+故事接龙）

### 专题影片分析（case-studies）
- [[../case-studies/bawang-bieji]] 《霸王别姬》忠诚主题 + 五人物光谱
- [[../case-studies/baiyuan-zhi-lian]] 《百元之恋》缺点驱动型弧光 + 五事件实操
- [[../case-studies/xiaoshi-de-airen]] 《消失的爱人》双视角叙事 + 信息错位

### 比较卡（comparison）
- [[../comparison/east-west-story-standards]] 东西方故事价值标准（文以载道 vs 探索人性）
- [[../comparison/buddy-love-vs-institutionalized]] 伙伴之情 vs 被制度化

### 反查索引（index）
- [[./moc]] 本文件
- [[./film-case-index]] 影片案例索引
- [[./term-glossary]] 术语表（中英对照）

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
- **2026-04-06 v1.0** — 基于 故事元素积累6_merged.pdf 的 73 页全量内容建立完整 MOC。36 篇笔记 + 3 索引全部实际创建完毕。
