# Claude Code 电影理论知识库文件包

这是给你直接放进仓库用的最小可用版本，参考了 `vibe-coding-cn` 的组织思路，并对齐 Claude Code 的 `CLAUDE.md / rules / skills / agents` 机制。

## 包含内容
- `.claude/CLAUDE.md`：总控规则
- `.claude/rules/`：长期规则与笔记结构
- `.claude/skills/`：3 个可直接调用的工作流
- `.claude/agents/`：1 个研究型 subagent
- `prompts/`：alpha / omega 元提示词
- `sources/`：放原始资料
- `knowledge/`：放最终知识库

## 推荐用法
1. 把整个文件包拷到你的项目根目录
2. 在 Claude Code 中打开该仓库
3. 先用 `/ingest-film-theory` 摄入 1-2 份材料
4. 再用 `/compare-film-theories` 做比较
5. 最后用 `/build-director-study-note` 把理论转成导演练习

## 建议的第一批材料
- 课堂笔记
- 书摘
- 论文摘要
- 导演访谈摘录
- 你自己的观片分析

## 最小目录
```text
sources/
knowledge/
prompts/
.claude/
```
