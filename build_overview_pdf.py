# -*- coding: utf-8 -*-
"""Build PKTFILM knowledge base overview PDF."""
import os
import re
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

# ---------------------------------------------------------------------------
# Font registration
# ---------------------------------------------------------------------------
FONT_BODY = "SimHei"
FONT_TITLE = "SimHei"
FONT_BODY_BOLD = "SimHei"

pdfmetrics.registerFont(TTFont("SimHei", "C:/Windows/Fonts/simhei.ttf"))
try:
    pdfmetrics.registerFont(TTFont("MSYaHei", "C:/Windows/Fonts/msyh.ttc"))
    pdfmetrics.registerFont(TTFont("MSYaHei-Bold", "C:/Windows/Fonts/msyhbd.ttc"))
    FONT_TITLE = "MSYaHei-Bold"
    FONT_BODY = "MSYaHei"
    FONT_BODY_BOLD = "MSYaHei-Bold"
    print("Loaded MSYaHei fonts")
except Exception as exc:  # noqa: BLE001
    print(f"MSYaHei failed ({exc}); falling back to SimHei for all styles")

# ---------------------------------------------------------------------------
# File list
# ---------------------------------------------------------------------------
KB_ROOT = "E:/director/prompt/knowledge"

CHAPTERS = [
    (
        "theory",
        "第二章 叙事理论(Narrative Theory)",
        "回答'叙事为什么要这样组织'的第一层抽象规则。",
        [
            ("theory/three-act-structure.md", None),
            ("theory/fifteen-beat-sheet.md", None),
            ("theory/genre-narratives-overview.md", None),
            ("theory/conflict-six-types.md", None),
            ("theory/theme-expression-methods.md", None),
            ("theory/story-core-and-contrast.md", None),
            ("theory/film-analysis-method.md", None),
        ],
    ),
    (
        "concepts",
        "第三章 概念卡(Concepts)",
        "把理论拆成'一个概念一张卡',按人物/叙事/视听/声音/对白/符号六类组织。",
        # Expanded below via CONCEPT_SUBSECTIONS
        [],
    ),
    (
        "genre",
        "第四章 类型叙事(Genre Narratives)",
        "基于 Blake Snyder《救猫咪》十种类型中的关键模板,配合类型辨识要点。",
        [
            ("genre/buddy-love.md", None),
            ("genre/dude-with-a-problem.md", None),
            ("genre/rites-of-passage.md", None),
            ("genre/institutionalized.md", None),
            ("genre/thriller-elements.md", None),
        ],
    ),
    (
        "story-elements",
        "第五章 故事元素素材库(Story Elements Library)",
        "扁平化素材库,为笔试'编讲故事'提供即取即用的人/物/景/情素材。",
        [
            ("story-elements/character-design-library.md", None),
            ("story-elements/antagonist-and-flaws-library.md", None),
            ("story-elements/props-and-six-uses-library.md", None),
            ("story-elements/scene-and-setting-library.md", None),
            ("story-elements/suspense-and-conflict-library.md", None),
            ("story-elements/emotion-and-relation-library.md", None),
            ("story-elements/family-conflict-library.md", None),
            ("story-elements/profession-doctor.md", None),
            ("story-elements/profession-police.md", None),
            ("story-elements/costume-and-personality-library.md", None),
        ],
    ),
    (
        "director-notes",
        "第六章 导演练习(Director Notes)",
        "把理论和素材落到艺考实操:编故事、对抗引擎、道具升级、面试应对、分镜工作流。",
        [
            ("director-notes/five-event-outline.md", None),
            ("director-notes/contrast-engine-method.md", None),
            ("director-notes/prop-to-scene-method.md", None),
            ("director-notes/exam-interview-strategy.md", None),
            ("director-notes/storyboard-workflow.md", None),
        ],
    ),
    (
        "comparison",
        "第七章 比较卡(Comparisons)",
        "辨析易混淆的对立概念,通过差异定位加深理解。",
        [
            ("comparison/east-west-story-standards.md", None),
            ("comparison/buddy-love-vs-institutionalized.md", None),
            ("comparison/formalism-vs-realism.md", None),
        ],
    ),
    (
        "case-studies",
        "第八章 专题影片分析(Case Studies)",
        "把理论落到具体影片,提供可引用的案例弹药。",
        [
            ("case-studies/bawang-bieji.md", None),
            ("case-studies/baiyuan-zhi-lian.md", None),
            ("case-studies/xiaoshi-de-airen.md", None),
        ],
    ),
    (
        "index",
        "第九章 反查索引(Index)",
        "术语、影片、世界电影参考与仓库审计,用于跨层反查。",
        [
            ("index/film-case-index.md", None),
            ("index/term-glossary.md", None),
            ("index/omega-v1-audit.md", None),
            ("index/world-cinema-reference.md", None),
        ],
    ),
]

CONCEPT_SUBSECTIONS = [
    (
        "人物(Character)",
        [
            "concepts/character/character-trinity.md",
            "concepts/character/save-the-cat-moment.md",
            "concepts/character/character-arc-mechanism.md",
            "concepts/character/desire-goal-motivation.md",
        ],
    ),
    (
        "叙事(Narrative)",
        [
            "concepts/narrative/inciting-incident.md",
            "concepts/narrative/contrast-three-layers.md",
        ],
    ),
    (
        "视听语言(Cinematic Language)",
        [
            "concepts/cinematic-language/visual-language-overview.md",
            "concepts/cinematic-language/blocking-mise-en-scene.md",
            "concepts/cinematic-language/shot-types.md",
            "concepts/cinematic-language/camera-angles.md",
            "concepts/cinematic-language/camera-movement.md",
            "concepts/cinematic-language/lighting-techniques.md",
            "concepts/cinematic-language/aspect-ratios.md",
            "concepts/cinematic-language/composition-styles.md",
        ],
    ),
    (
        "声音(Sound)",
        [
            "concepts/sound/sound-design.md",
        ],
    ),
    (
        "对白(Dialogue)",
        [
            "concepts/dialogue/dialogue-six-techniques.md",
        ],
    ),
    (
        "符号(Symbolism)",
        [
            "concepts/symbolism/animal-symbolism.md",
            "concepts/symbolism/prop-symbolism.md",
        ],
    ),
]

# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    fm = {}
    if not m:
        return fm
    block = m.group(1)
    current_key = None
    for raw in block.splitlines():
        if not raw.strip():
            continue
        # Simple "key: value" lines (we ignore list continuations for our needs)
        km = re.match(r"^([A-Za-z_][A-Za-z0-9_\-]*)\s*:\s*(.*)$", raw)
        if km:
            key = km.group(1).strip()
            val = km.group(2).strip()
            fm[key] = val
            current_key = key
        # list items and nested values are ignored (we don't need them)
    return fm


def body_after_frontmatter(text: str) -> str:
    m = FRONTMATTER_RE.match(text)
    if m:
        return text[m.end():]
    return text


def extract_section(body: str, header_regex: str) -> str:
    """Extract the content under an H2 matching header_regex, until next H2 or EOF."""
    pat = re.compile(rf"^##\s+{header_regex}\s*\n(.*?)(?=^##\s|\Z)", re.DOTALL | re.MULTILINE)
    m = pat.search(body)
    if not m:
        return ""
    return m.group(1).strip()


def clean_text(t: str) -> str:
    # Strip markdown link wrappers [text](url) -> text
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    # Remove bold/italics markers
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", t)
    # Remove backticks
    t = t.replace("`", "")
    # Remove remaining markdown artifacts
    return t.strip()


def xml_escape(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def extract_bullet_points(body: str, max_points: int = 5) -> list:
    """Extract bullet-like core points. Prefer Claims / Key terms / list items."""
    points = []
    # Try Claims section first
    for header in ("Claims", "Key terms", "Takeaways", "Definitions", "Matrix",
                   "Decision mapping", "Non-overlapping differences", "One-liners",
                   "The question it answers"):
        sec = extract_section(body, re.escape(header))
        if not sec:
            continue
        # Split into top-level bullets / numbered items
        lines = sec.splitlines()
        buf = ""
        for line in lines:
            raw = line.rstrip()
            if not raw.strip():
                if buf:
                    points.append(buf.strip())
                    buf = ""
                continue
            if re.match(r"^\s*(?:\d+\.|\-|\*)\s+", raw):
                if buf:
                    points.append(buf.strip())
                item = re.sub(r"^\s*(?:\d+\.|\-|\*)\s+", "", raw)
                buf = item
            elif buf and raw.startswith(" "):
                buf += " " + raw.strip()
            elif raw.startswith("|"):  # table row
                # Skip header separator
                if re.match(r"^\|[\s\-:|]+\|$", raw):
                    continue
                cells = [c.strip() for c in raw.strip("|").split("|")]
                if cells and cells[0] and not cells[0].startswith("---"):
                    merged = " — ".join(c for c in cells if c)
                    points.append(merged)
        if buf:
            points.append(buf.strip())
        if points:
            break
    cleaned = []
    for p in points:
        p = clean_text(p)
        # Drop overly short
        if len(p) < 4:
            continue
        # Truncate long
        if len(p) > 180:
            p = p[:178].rstrip() + "…"
        cleaned.append(p)
        if len(cleaned) >= max_points:
            break
    return cleaned


def extract_method(body: str) -> list:
    """Return up to 3 condensed method steps."""
    candidates = ["Method / How to use", "Method", "Analysis recipe",
                  "Decision mapping", "Exercises"]
    for header in candidates:
        sec = extract_section(body, re.escape(header))
        if not sec:
            continue
        steps = []
        buf = ""
        for line in sec.splitlines():
            raw = line.rstrip()
            if re.match(r"^\s*(?:\d+\.|###\s+Step\s*\d+|\-|\*)\s+", raw):
                if buf:
                    steps.append(buf.strip())
                item = re.sub(r"^\s*(?:\d+\.|###\s+Step\s*\d+|\-|\*)\s+", "", raw)
                buf = item
            elif buf and raw.strip() and not raw.startswith("#"):
                buf += " " + raw.strip()
            elif not raw.strip():
                if buf:
                    steps.append(buf.strip())
                    buf = ""
        if buf:
            steps.append(buf.strip())
        if steps:
            cleaned = []
            for s in steps:
                s = clean_text(s)
                if len(s) < 4:
                    continue
                if len(s) > 160:
                    s = s[:158].rstrip() + "…"
                cleaned.append(s)
                if len(cleaned) >= 3:
                    break
            if cleaned:
                return cleaned
    return []


def extract_tldr(body: str) -> str:
    sec = extract_section(body, "TL;DR")
    if sec:
        # Take first paragraph
        paragraph = sec.split("\n\n")[0]
        paragraph = re.sub(r"\s+", " ", paragraph).strip()
        paragraph = clean_text(paragraph)
        if len(paragraph) > 600:
            paragraph = paragraph[:598] + "…"
        return paragraph
    # Fallback: first non-header paragraph
    for para in body.split("\n\n"):
        p = para.strip()
        if not p or p.startswith("#"):
            continue
        p = re.sub(r"\s+", " ", p)
        p = clean_text(p)
        if len(p) > 600:
            p = p[:598] + "…"
        return p
    return ""


def read_note(rel_path: str) -> dict:
    full = os.path.join(KB_ROOT, rel_path).replace("\\", "/")
    with open(full, "r", encoding="utf-8") as f:
        text = f.read()
    fm = parse_frontmatter(text)
    body = body_after_frontmatter(text)
    return {
        "rel_path": rel_path,
        "name": fm.get("name", rel_path),
        "description": fm.get("description", ""),
        "type": fm.get("type", ""),
        "status": fm.get("status", ""),
        "tags": fm.get("tags", ""),
        "tldr": extract_tldr(body),
        "points": extract_bullet_points(body, max_points=5),
        "method": extract_method(body),
    }


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
styles = getSampleStyleSheet()

style_cover_title = ParagraphStyle(
    "CoverTitle", parent=styles["Normal"], fontName=FONT_TITLE,
    fontSize=32, leading=40, alignment=1, textColor=colors.HexColor("#1a1a1a"),
    spaceAfter=14,
)
style_cover_sub = ParagraphStyle(
    "CoverSub", parent=styles["Normal"], fontName=FONT_BODY,
    fontSize=14, leading=22, alignment=1, textColor=colors.HexColor("#333333"),
    spaceAfter=30,
)
style_cover_meta = ParagraphStyle(
    "CoverMeta", parent=styles["Normal"], fontName=FONT_BODY,
    fontSize=12, leading=20, alignment=1, textColor=colors.HexColor("#444"),
    spaceAfter=8,
)
style_cover_badge = ParagraphStyle(
    "CoverBadge", parent=styles["Normal"], fontName=FONT_TITLE,
    fontSize=13, leading=20, alignment=1, textColor=colors.HexColor("#b33c1a"),
    spaceAfter=12,
)
style_cover_intro = ParagraphStyle(
    "CoverIntro", parent=styles["Normal"], fontName=FONT_BODY,
    fontSize=10.5, leading=18, alignment=4, textColor=colors.HexColor("#333"),
    leftIndent=1*cm, rightIndent=1*cm,
)

style_h1 = ParagraphStyle(
    "H1", parent=styles["Normal"], fontName=FONT_TITLE,
    fontSize=20, leading=28, spaceBefore=0, spaceAfter=14,
    textColor=colors.HexColor("#101820"),
)
style_h2 = ParagraphStyle(
    "H2", parent=styles["Normal"], fontName=FONT_TITLE,
    fontSize=16, leading=22, spaceBefore=14, spaceAfter=8,
    textColor=colors.HexColor("#1a365d"),
)
style_h3 = ParagraphStyle(
    "H3", parent=styles["Normal"], fontName=FONT_TITLE,
    fontSize=13, leading=18, spaceBefore=10, spaceAfter=5,
    textColor=colors.HexColor("#2c5282"),
)
style_h4 = ParagraphStyle(
    "H4", parent=styles["Normal"], fontName=FONT_BODY_BOLD,
    fontSize=11, leading=16, spaceBefore=6, spaceAfter=3,
    textColor=colors.HexColor("#2a4365"),
)
style_body = ParagraphStyle(
    "Body", parent=styles["Normal"], fontName=FONT_BODY,
    fontSize=10.5, leading=17, spaceAfter=6,
    textColor=colors.HexColor("#1a1a1a"),
)
style_body_small = ParagraphStyle(
    "BodySmall", parent=styles["Normal"], fontName=FONT_BODY,
    fontSize=9.5, leading=15, spaceAfter=4,
    textColor=colors.HexColor("#333"),
)
style_bullet = ParagraphStyle(
    "Bullet", parent=style_body, fontSize=10.5, leading=16,
    leftIndent=14, bulletIndent=2, spaceAfter=3,
)
style_meta = ParagraphStyle(
    "Meta", parent=styles["Normal"], fontName=FONT_BODY,
    fontSize=9, leading=13, textColor=colors.HexColor("#666"),
    spaceAfter=4,
)
style_toc1 = ParagraphStyle(
    "TOC1", parent=styles["Normal"], fontName=FONT_TITLE,
    fontSize=12, leading=18, leftIndent=0, spaceAfter=3,
)
style_toc2 = ParagraphStyle(
    "TOC2", parent=styles["Normal"], fontName=FONT_BODY,
    fontSize=10.5, leading=16, leftIndent=18, spaceAfter=2,
)
style_toc3 = ParagraphStyle(
    "TOC3", parent=styles["Normal"], fontName=FONT_BODY,
    fontSize=10, leading=15, leftIndent=36, spaceAfter=1,
    textColor=colors.HexColor("#444"),
)


# ---------------------------------------------------------------------------
# Bookmark / heading flowables with TOC hooking
# ---------------------------------------------------------------------------
_bookmark_counter = {"n": 0}


def heading(text: str, level: int, style: ParagraphStyle):
    _bookmark_counter["n"] += 1
    key = f"h{_bookmark_counter['n']}"
    escaped = xml_escape(text)
    p = Paragraph(f'<a name="{key}"/>{escaped}', style)
    p._bookmarkName = key
    p._outlineLevel = level
    p._headingLevel = level
    return p


class HeadingParagraph(Paragraph):
    """Paragraph that notifies doc TOC with level & text."""

    def __init__(self, text, style, level):
        self._level = level
        self._raw_text = text
        super().__init__(text, style)

    def draw(self):
        super().draw()
        # Outline / bookmark — only for headings that also notify TOC,
        # to keep outline levels contiguous.
        bn = getattr(self, "_bookmark_name", None)
        notify = getattr(self, "_notify_toc", False)
        if bn and notify:
            self.canv.bookmarkPage(bn)
            self.canv.addOutlineEntry(self._raw_text, bn, level=self._level, closed=False)
        # Notify TOC
        self.canv.beginForm  # noqa: B018
        try:
            from reportlab.platypus.tableofcontents import TableOfContents  # noqa: F401
        except Exception:
            pass


def make_heading(text: str, level: int, style: ParagraphStyle, notify_toc: bool = True):
    _bookmark_counter["n"] += 1
    key = f"h{_bookmark_counter['n']}"
    safe = xml_escape(text)
    p = HeadingParagraph(f'<a name="{key}"/>{safe}', style, level)
    p._bookmark_name = key
    p._raw_text = text
    p._notify_toc = notify_toc
    p._level = level
    return p


# ---------------------------------------------------------------------------
# Doc template with header/footer & TOC notify
# ---------------------------------------------------------------------------
class PKTDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        frame = Frame(
            self.leftMargin, self.bottomMargin,
            self.width, self.height, id="main",
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        )
        self.addPageTemplates([
            PageTemplate(id="cover", frames=frame, onPage=_draw_cover_bg),
            PageTemplate(id="body", frames=frame,
                         onPage=_draw_header_footer),
        ])

    def afterFlowable(self, flowable):
        notify = getattr(flowable, "_notify_toc", False)
        if notify and isinstance(flowable, HeadingParagraph):
            text = flowable._raw_text
            level = flowable._level
            key = flowable._bookmark_name
            self.notify("TOCEntry", (level, text, self.page, key))


def _draw_cover_bg(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#f8f7f2"))
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    # Accent bar
    canvas.setFillColor(colors.HexColor("#b33c1a"))
    canvas.rect(0, A4[1] - 6, A4[0], 6, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#1a365d"))
    canvas.rect(0, 0, A4[0], 4, fill=1, stroke=0)
    canvas.restoreState()


def _draw_header_footer(canvas, doc):
    canvas.saveState()
    # Header line
    canvas.setFont(FONT_BODY, 8.5)
    canvas.setFillColor(colors.HexColor("#666"))
    canvas.drawString(doc.leftMargin, A4[1] - 1.2*cm,
                      "PKTFILM 知识库总览 · v1.3")
    canvas.drawRightString(A4[0] - doc.rightMargin, A4[1] - 1.2*cm,
                           "Film Theory & Directing KB")
    canvas.setStrokeColor(colors.HexColor("#cccccc"))
    canvas.setLineWidth(0.4)
    canvas.line(doc.leftMargin, A4[1] - 1.35*cm,
                A4[0] - doc.rightMargin, A4[1] - 1.35*cm)
    # Footer page number
    canvas.setFont(FONT_BODY, 9)
    canvas.setFillColor(colors.HexColor("#444"))
    total = getattr(canvas, "_total_pages", None)
    page_str = (f"第 {doc.page} 页 / 共 {total} 页"
                if total else f"第 {doc.page} 页")
    canvas.drawCentredString(A4[0] / 2, 1.0*cm, page_str)
    canvas.restoreState()


# ---------------------------------------------------------------------------
# Flowable builders
# ---------------------------------------------------------------------------
def status_badge(status: str) -> str:
    status = (status or "").strip().lower()
    color_map = {
        "stable": "#2f855a",
        "draft": "#b7791f",
        "seed": "#718096",
        "disputed": "#c53030",
    }
    c = color_map.get(status, "#718096")
    if not status:
        status = "unspecified"
    return f'<font color="{c}"><b>[{status}]</b></font>'


def bullet_list(items: list, style=style_bullet):
    out = []
    for it in items:
        out.append(Paragraph(f"• {xml_escape(it)}", style))
    return out


def note_block(note: dict):
    out = []
    head = xml_escape(note["name"])
    out.append(make_heading(head, 3, style_h4, notify_toc=False))
    meta_parts = []
    if note["type"]:
        meta_parts.append(f'类型: {note["type"]}')
    if note["status"]:
        meta_parts.append(f'状态: {status_badge(note["status"])}')
    if note["rel_path"]:
        meta_parts.append(f'<font color="#888">文件: {xml_escape(note["rel_path"])}</font>')
    if meta_parts:
        out.append(Paragraph("  ·  ".join(meta_parts), style_meta))
    if note["description"]:
        out.append(Paragraph(
            f'<b>描述</b>: {xml_escape(note["description"])}', style_body_small))
    if note["tldr"]:
        out.append(Paragraph(
            f'<b>TL;DR</b>: {xml_escape(note["tldr"])}', style_body_small))
    if note["points"]:
        out.append(Paragraph('<b>核心要点</b>', style_body_small))
        out.extend(bullet_list(note["points"]))
    if note["method"]:
        out.append(Paragraph('<b>关键方法</b>', style_body_small))
        out.extend(bullet_list(note["method"]))
    out.append(Spacer(1, 4))
    return out


# ---------------------------------------------------------------------------
# Build document
# ---------------------------------------------------------------------------
def build_cover():
    story = []
    story.append(Spacer(1, 4.5*cm))
    story.append(Paragraph("PKTFILM 电影学习知识库", style_cover_title))
    story.append(Paragraph(
        "Film Theory &amp; Directing Knowledge Base<br/>总览与精要",
        style_cover_sub))
    story.append(Spacer(1, 0.6*cm))
    story.append(Paragraph("v1.3  |  56 篇笔记", style_cover_badge))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("作者: P0ckket(艺考编导生)", style_cover_meta))
    story.append(Paragraph("日期: 2026-04-21", style_cover_meta))
    story.append(Spacer(1, 2.2*cm))
    story.append(Paragraph(
        "本文档基于《故事元素积累6》73 页高中艺考笔记,与 filmtheory.net、"
        "DirectorsConsole、Storyboarder 等网络资源整合而成,是一个可持续进化的"
        "电影理论与创作知识库。全书按'理论 → 概念 → 类型 → 素材 → 练习 → "
        "比较 → 案例 → 索引'八层组织,服务笔试编讲故事、影片分析与面试应对。",
        style_cover_intro))
    story.append(PageBreak())
    return story


def build_toc():
    toc = TableOfContents()
    toc.levelStyles = [style_toc1, style_toc2, style_toc3]
    story = []
    story.append(make_heading("目录(Contents)", 0, style_h1, notify_toc=False))
    story.append(Spacer(1, 6))
    story.append(toc)
    story.append(PageBreak())
    return story


def build_executive_summary():
    story = []
    story.append(make_heading("第一章 执行摘要(Executive Summary)", 0, style_h1))
    story.append(make_heading("1.1 目的与方法论", 1, style_h2))
    story.append(Paragraph(
        "本知识库的<b>北极星目标</b>是:把高中艺考期间积累的纸面笔记、课堂语录"
        "与看片心得,转化为一个<b>可检索、可演化、可复用</b>的电影理论与导演"
        "实践资产,而不是一次性的'读书总结'或'影评集'。它服务两个用途——"
        "电影研究/课程复习,以及导演决策/编讲故事训练。", style_body))
    story.append(Paragraph(
        "方法上,知识库遵循<b>原子化(Atomic)</b>原则:一个概念一张卡,通过 YAML "
        "frontmatter 和 H2 级别的标准 schema 统一元数据。理论与实操严格分层,"
        "笔记之间用双向链接构成网状结构——每当写下一个新判断,都能回溯到它"
        "的证据来源(原文/学界/我的理解/推断)。", style_body))
    story.append(Paragraph(
        "知识库的'进化路径'是 α/Ω 双循环:α 负责生成新笔记,Ω 负责定期审计"
        "并提出升级建议。冲突不静默覆盖,而是并列记录争议+增补待核实项。",
        style_body))

    story.append(make_heading("1.2 架构总览", 1, style_h2))
    story.append(Paragraph(
        "<font color='#555'>下图以文字树形展示八层结构与笔记归属。</font>",
        style_body_small))
    tree = [
        "knowledge/",
        "├── theory/               (7) 叙事'为什么这样讲'的抽象规则",
        "├── concepts/             (18) 人物/叙事/视听/声音/对白/符号",
        "│   ├── character/        (4)",
        "│   ├── narrative/        (2)",
        "│   ├── cinematic-language/ (8)",
        "│   ├── sound/            (1)",
        "│   ├── dialogue/         (1)",
        "│   └── symbolism/        (2)",
        "├── genre/                (5) Snyder 十种类型选讲",
        "├── story-elements/       (10) 扁平化素材卡,服务编讲故事",
        "├── director-notes/       (5) 导演练习/艺考实操手册",
        "├── comparison/           (3) 易混淆概念辨析",
        "├── case-studies/         (3) 专题影片分析",
        "└── index/                (4) 术语/影片/世界电影/审计",
    ]
    tree_style = ParagraphStyle(
        "Tree", parent=style_body, fontName="Courier", fontSize=9.2,
        leading=13, textColor=colors.HexColor("#222"))
    for line in tree:
        story.append(Paragraph(xml_escape(line), tree_style))

    story.append(Spacer(1, 10))
    story.append(make_heading("1.3 统计数据", 1, style_h2))
    table_data = [
        ["层(Layer)", "笔记数", "主要用途"],
        ["理论 (theory)", "7", "叙事的'为什么'"],
        ["概念 (concepts)", "18", "拆解的'是什么'"],
        ["类型 (genre)", "5", "Snyder 类型模板"],
        ["素材库 (story-elements)", "10", "快速查阅素材"],
        ["导演练习 (director-notes)", "5", "应试操作手册"],
        ["比较卡 (comparison)", "3", "辨析易混淆概念"],
        ["案例分析 (case-studies)", "3", "把理论落到影片"],
        ["索引 (index)", "4", "反查工具"],
        ["合计", "56", "——"],
    ]
    tbl = Table(table_data, colWidths=[5.5*cm, 2.2*cm, 7.3*cm], hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), FONT_BODY),
        ("FONTNAME", (0, 0), (-1, 0), FONT_TITLE),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("BACKGROUND", (0, 1), (-1, -2),
         colors.HexColor("#f7f7f2")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2),
         [colors.HexColor("#f7f7f2"), colors.white]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e6d9c7")),
        ("FONTNAME", (0, -1), (-1, -1), FONT_TITLE),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#bfbfbf")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 12))

    story.append(make_heading("1.4 核心方法论", 1, style_h2))
    principles = [
        ("证据分层", "所有理论陈述标注【原文】/【学界】/【我的理解】/【你的推断】,"
                   "防止把'我觉得'写成'作者说'。"),
        ("原子化笔记", "一个概念一张卡,多数笔记控制在 200-800 字;避免在一个文件里堆叠多个独立概念。"),
        ("标准化 schema", "YAML frontmatter(name/type/status/tags/sources)+ 固定 H2 结构"
                        "(TL;DR / Definitions / Claims / Method / Links & relations / Changelog)。"),
        ("可持续进化", "status 字段追踪成熟度(seed→draft→stable→disputed);"
                    "每篇笔记带 Changelog,冲突并列不覆盖。"),
        ("跨层关联", "Links & relations 字段建立人物↔叙事↔视听的网状引用,"
                   "用 MOC/索引做反查入口。"),
    ]
    for i, (title, desc) in enumerate(principles, 1):
        story.append(Paragraph(
            f"<b>{i}. {xml_escape(title)}</b> —— {xml_escape(desc)}",
            style_body))
    story.append(PageBreak())
    return story


def build_chapter(chapter_id: str, title: str, intro: str,
                  notes: list, sub_sections: list = None):
    story = []
    story.append(make_heading(title, 0, style_h1))
    if intro:
        story.append(Paragraph(xml_escape(intro), style_body))
        story.append(Spacer(1, 4))
    if sub_sections:
        for sub_title, rel_paths in sub_sections:
            story.append(make_heading(sub_title, 1, style_h2))
            for rp in rel_paths:
                n = read_note(rp)
                story.extend(note_block(n))
    else:
        for rel, _ in notes:
            n = read_note(rel)
            story.extend(note_block(n))
    story.append(PageBreak())
    return story


def build_usage_guide():
    story = []
    story.append(make_heading("第十章 艺考实战使用指南", 0, style_h1))
    story.append(Paragraph(
        "本章把前九章的笔记串成四条'路线图',直接对应艺考四种典型任务。"
        "路径里的中括号数字为推荐使用顺序,每一步可以点到即止,也可以深入翻原笔记。",
        style_body))

    story.append(make_heading("10.1 笔试'编讲故事'题", 1, style_h2))
    story.append(Paragraph(
        "考试情境: 2.5 小时写 2000 字故事,通常给一个题眼或道具/场景提示。",
        style_body_small))
    path1 = [
        "Step 1 · 抓核——读《故事核与反差》+《冲突六分类》锁定题眼冲突",
        "Step 2 · 搭骨——套《三幕结构》(300/600/300)或《五事件大纲》(400×5)",
        "Step 3 · 填肉——从《人物素材库》《道具六用法》《场景素材库》三张素材卡取元素",
        "Step 4 · 升温——用《对抗引擎法》或《道具升级法》推进矛盾;插入《救猫时刻》",
        "Step 5 · 锁题——用《主题表达法》在结尾做反差照应",
    ]
    story.extend(bullet_list(path1))

    story.append(make_heading("10.2 笔试'影片分析'题", 1, style_h2))
    story.append(Paragraph(
        "考试情境: 看片 1-2 遍后,写 1500-2000 字分析,通常指定某个角度(声音/"
        "视听语言/主题等)。",
        style_body_small))
    path2 = [
        "Step 1 · 锁定角度——读《影片分析方法》建立'形式入口→主题命题'链路",
        "Step 2 · 拆视听——按《视听语言总览》分景别/角度/运动/灯光/构图五轴切片",
        "Step 3 · 上叙事——用《三幕结构》《契机事件》定位关键转折",
        "Step 4 · 调案例——查《专题影片分析》三案例做对照援引",
        "Step 5 · 收主题——用《主题表达法》回到'导演想说什么',避免只停在技术层",
    ]
    story.extend(bullet_list(path2))

    story.append(make_heading("10.3 面试'故事接龙/锐评'", 1, style_h2))
    path3 = [
        "Step 1 · 打开——《面试策略》列出'三秒破题'模板",
        "Step 2 · 接龙——《人物设计素材库》+《情感关系素材库》提供快速人物组合",
        "Step 3 · 升阶——《道具六用法》里挑 1 件道具启动二幕",
        "Step 4 · 锐评片——用《东方西方故事标准》辨析中外片差异,显示视野",
        "Step 5 · 收口——用一句具象画面收尾(不抽象总结)",
    ]
    story.extend(bullet_list(path3))

    story.append(make_heading("10.4 日常训练建议", 1, style_h2))
    daily = [
        "每周 1 篇影片分析小作业,走 10.2 路线;评分维度: 形式入口→命题→论证是否闭环",
        "每周 2 个'道具-场景-情感'三元组,仅 300 字微故事,训练《对抗引擎法》",
        "每月补 1 个世界电影参考(参见 world-cinema-reference.md),扩非华语案例弹药",
        "看片时同步做《影片分析方法》里的'五轴速记',禁止只写剧情",
        "每 6 周跑一次 Ω 审计(omega-v1-audit.md),更新 status 字段",
    ]
    story.extend(bullet_list(daily))
    story.append(PageBreak())
    return story


def build_versions():
    story = []
    story.append(make_heading("第十一章 版本与演进", 0, style_h1))
    story.append(make_heading("11.1 版本历史", 1, style_h2))
    versions = [
        ("v1.0", "知识库雏形:theory 7 篇 + concepts/character 4 篇 + genre 5 篇 + "
                "story-elements 10 篇初版;全部 wiki-link 未规范。"),
        ("v1.1", "骨架补齐:补 director-notes 5 篇、comparison 3 篇、"
                "case-studies 3 篇;首次做 Ω 审计 omega-v1-audit.md。"),
        ("v1.2", "视听语言扩展:新增 cinematic-language 8 篇(overview/blocking/"
                "shot-types/angles/movement/lighting/aspect/composition)及 sound/"
                "dialogue/symbolism 分枝。"),
        ("v1.3", "跨库整合:合入 world-cinema-reference,批量把 wiki-link 替换为"
                "标准 Markdown 相对链接;输出本总览文档。"),
    ]
    for tag, desc in versions:
        story.append(Paragraph(
            f"<b>{tag}</b> —— {xml_escape(desc)}", style_body))

    story.append(make_heading("11.2 待扩展 Backlog", 1, style_h2))
    story.append(Paragraph(
        "下列条目摘自 <i>index/omega-v1-audit.md</i> 的优先级队列,"
        "以 P1 / P2 / P3 划分。",
        style_body_small))
    backlog = [
        ("P1", "新增《剪辑节奏与蒙太奇》概念卡,填补 concepts/editing 空白分枝"),
        ("P1", "把 case-studies 扩充到 5 部,至少覆盖 1 部西方经典 + 1 部亚洲非华语"),
        ("P1", "为所有 stable 笔记补齐 Changelog 栏位,当前部分缺失"),
        ("P2", "建立 concepts/performance 分枝(表演设计/方法派/类型化表演)"),
        ("P2", "把 story-elements/ 中的扁平卡按'冷/暖/中性'贴上情感色温标签"),
        ("P2", "为 genre 每类补一张'反类型'卡,提示常见陷阱"),
        ("P3", "引入电影史时间线索引(新浪潮/作者论/港台新电影)"),
        ("P3", "做 Obsidian → Notion 结构迁移脚本"),
        ("P3", "为术语表补充 IPA/英文语音,用于面试英语提问场景"),
    ]
    for tag, desc in backlog:
        story.append(Paragraph(
            f"<b>[{tag}]</b> {xml_escape(desc)}", style_body_small))

    story.append(make_heading("11.3 下一步计划", 1, style_h2))
    plan = [
        "短期(1 个月内): 完成 P1 三项,输出 v1.4",
        "中期(3 个月内): 按周迭代 case-studies,目标 12 部影片档案",
        "长期(艺考前): 走完一轮 Ω 审计,把 status 全部推到 stable,并导出复习 PDF",
    ]
    story.extend(bullet_list(plan))
    story.append(PageBreak())
    return story


def build_appendix_terms():
    story = []
    story.append(make_heading("附录 A 术语表精选(Glossary)", 0, style_h1))
    story.append(Paragraph(
        "自 <i>index/term-glossary.md</i> 提取的核心中英对照,按字母顺序排列。",
        style_body_small))
    terms = [
        ("Aspect Ratio", "画幅比", "银幕宽高比;2.39:1 史诗、1.85:1 主流、1.33:1 经典、1:1 极简"),
        ("Back Lighting", "逆光", "光源在被摄体背后,常用于剪影与神圣化"),
        ("Beat", "节拍", "最小戏剧单元,一次动作-反应往来"),
        ("Blocking", "走位", "人+物+机位在空间里的布置关系"),
        ("Buddy Love", "伙伴之爱", "Snyder 类型:两个人因互补而被迫同行并改变彼此"),
        ("Camera Angle", "摄影机角度", "高/平/低/荷兰角,决定观众与人物的权力关系"),
        ("Character Arc", "人物弧光", "主角从'错误信念'到'认知修正'的变化轨迹"),
        ("Composition", "构图", "画面内元素的几何与权重组织"),
        ("Conflict", "冲突", "内-内/内-外/人-人/人-社会/人-自然/人-自我六类"),
        ("Contrast", "反差", "外部(人物间)/内部(人物内)/戏剧(境遇)三层"),
        ("Dialogue", "对白", "六技法:信息/冲突/潜台词/特征/节奏/风格"),
        ("Dude With a Problem", "麻烦男人", "普通人被迫进入非常态事件"),
        ("Fifteen Beats", "十五节拍", "Snyder《救猫咪》节拍表"),
        ("Formalism", "形式主义", "把电影语言视为抽象表意系统(爱森斯坦)"),
        ("Genre", "类型", "由'问题+解题模板'定义的叙事类"),
        ("Inciting Incident", "激励事件", "打破主角生活平衡的首个不可逆事件"),
        ("Institutionalized", "体制化", "Snyder 类型:个人 vs 系统,选择同化/反抗/死亡"),
        ("Lighting", "灯光", "主光/辅光/轮廓光三点布光为基础"),
        ("Mise-en-scène", "场面调度", "摄影机前的一切物质安排"),
        ("Montage", "蒙太奇", "镜头并置产生第三义的剪辑观"),
        ("Motivation", "动机", "生存/关系/理想,动机越'理想'越难催化"),
        ("Plot Point", "情节点", "幕与幕接缝的硬转折"),
        ("Predicament", "困境", "'难+一线生机',是戏剧推进的燃料"),
        ("Prop", "道具", "六用法:身份/关系/冲突/伏笔/象征/类型化"),
        ("Realism", "现实主义", "把电影语言视为记录真实的透明媒介(巴赞)"),
        ("Rites of Passage", "成长仪式", "Snyder 类型:主角通过痛苦穿越人生门槛"),
        ("Save the Cat", "救猫时刻", "让观众在开场即共情主角的微型善举"),
        ("Setup", "建置", "第一幕三要素:主角/前提/情景"),
        ("Shot Type", "景别", "远/全/中/近/特五级景别"),
        ("Sound Design", "声音设计", "对白/音乐/音效/环境声四轨层"),
        ("Story Core", "故事核", "故事最不可压缩的因果引擎"),
        ("Subplot", "副线", "与主线呼应的小情节,常承担主题投射"),
        ("Subtext", "潜台词", "对白表面 vs 真实意图的落差"),
        ("Symbol", "象征", "可反复出现并指向抽象意义的形象"),
        ("Theme", "主题", "导演想让观众带走的命题"),
        ("Three-Act", "三幕", "1:2:1 的段落比例结构"),
        ("Thriller", "惊悚", "以'信息不对称+倒计时'制造悬念的类型"),
        ("Tracking Shot", "跟拍镜头", "机位随被摄体运动的镜头"),
        ("Trinity (Character)", "人物三位一体", "欲望+动机+障碍的三角结构"),
    ]
    rows = [["英文(English)", "中文", "简要释义"]]
    for en, zh, desc in terms:
        rows.append([en, zh, desc])
    tbl = Table(rows, colWidths=[4.6*cm, 2.4*cm, 8.0*cm], hAlign="LEFT",
                repeatRows=1)
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), FONT_BODY),
        ("FONTNAME", (0, 0), (-1, 0), FONT_TITLE),
        ("FONTSIZE", (0, 0), (-1, -1), 9.2),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#f7f7f2"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#bfbfbf")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(tbl)
    story.append(PageBreak())
    return story


def build_appendix_full_list(all_notes):
    story = []
    story.append(make_heading("附录 B 全部笔记一览表(Master List)", 0, style_h1))
    story.append(Paragraph(
        "本表列出全部 56 篇笔记的文件名、中文名、类型、状态与所属层,"
        "用于最终反查。",
        style_body_small))
    rows = [["#", "文件名", "中文名", "类型", "状态", "层"]]
    for i, n in enumerate(all_notes, 1):
        layer = n["rel_path"].split("/")[0]
        short = n["rel_path"].split("/")[-1].replace(".md", "")
        rows.append([
            str(i),
            short,
            n["name"],
            n["type"] or "-",
            n["status"] or "-",
            layer,
        ])
    tbl = Table(rows, colWidths=[0.7*cm, 4.0*cm, 5.6*cm, 2.0*cm, 1.8*cm, 2.3*cm],
                hAlign="LEFT", repeatRows=1)
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), FONT_BODY),
        ("FONTNAME", (0, 0), (-1, 0), FONT_TITLE),
        ("FONTSIZE", (0, 0), (-1, -1), 8.6),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#f7f7f2"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#bfbfbf")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
    ]))
    story.append(tbl)
    return story


def all_relative_paths():
    paths = []
    for cid, _, _, notes in CHAPTERS:
        if cid == "concepts":
            for _, sub_paths in CONCEPT_SUBSECTIONS:
                paths.extend(sub_paths)
        else:
            for rel, _ in notes:
                paths.append(rel)
    return paths


def main():
    out_path = "E:/director/PKTFILM_知识库总览.pdf"
    doc = PKTDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=2.1*cm,
        rightMargin=2.1*cm,
        topMargin=1.9*cm,
        bottomMargin=1.6*cm,
        title="PKTFILM 电影学习知识库 v1.3",
        author="P0ckket",
    )

    # Force using body template after cover
    story = []
    # Cover (uses 'cover' page template - first page)
    story.extend(build_cover())
    # Switch to body template by issuing a NextPageTemplate-less approach:
    # use a special flowable to change page template
    from reportlab.platypus.doctemplate import NextPageTemplate
    # We already emitted PageBreak after cover. Insert NextPageTemplate before it:
    # Rebuild story with proper templates
    story = []
    story.extend([NextPageTemplate("body")])
    story.extend(build_cover())  # this ends with PageBreak

    # TOC
    story.extend(build_toc())

    # Chapter 1
    story.extend(build_executive_summary())

    # Chapters 2-9
    all_notes = []
    for cid, title, intro, notes in CHAPTERS:
        if cid == "concepts":
            story.extend(build_chapter(
                cid, title, intro, [], sub_sections=CONCEPT_SUBSECTIONS))
            for _, sub_paths in CONCEPT_SUBSECTIONS:
                for rp in sub_paths:
                    all_notes.append(read_note(rp))
        else:
            story.extend(build_chapter(cid, title, intro, notes))
            for rel, _ in notes:
                all_notes.append(read_note(rel))

    # Ch 10, 11
    story.extend(build_usage_guide())
    story.extend(build_versions())

    # Appendix
    story.extend(build_appendix_terms())
    story.extend(build_appendix_full_list(all_notes))

    # multiBuild for TOC
    doc.multiBuild(story)

    print(f"\nWritten: {out_path}")
    size = os.path.getsize(out_path)
    print(f"Size: {size/1024:.1f} KB")

    from pypdf import PdfReader
    reader = PdfReader(out_path)
    print(f"Total pages: {len(reader.pages)}")


if __name__ == "__main__":
    main()
