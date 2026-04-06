# Quickstart

## 1. 创建目录（如果还没有）
```bash
mkdir -p .claude/rules .claude/skills .claude/agents prompts sources knowledge
mkdir -p .claude/skills/ingest-film-theory .claude/skills/compare-film-theories .claude/skills/build-director-study-note
```

## 2. 复制本包内容到你的仓库根目录

## 3. 在 Claude Code 中测试
```text
/ingest-film-theory sources/week-01-notes.md knowledge/theory/week-01-seed.md
/compare-film-theories realism montage knowledge/comparison/realism-vs-montage.md
/build-director-study-note knowledge/theory/week-01-seed.md knowledge/director-notes/week-01-practice.md
```

## 4. 推荐顺序
- 先种 10-20 条核心笔记
- 再跑一轮 omega 优化
- 然后继续扩展 skill / rules / note schema
