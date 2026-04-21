# -*- coding: utf-8 -*-
"""Build PKTFILM 电影学教程 — textbook-grade PDF (150-250 pages)."""
import os
import re
import sys
import time
import html as htmllib
from collections import OrderedDict

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# ---------------------------------------------------------------------------
# Font registration
# ---------------------------------------------------------------------------
pdfmetrics.registerFont(TTFont('SimHei', 'C:/Windows/Fonts/simhei.ttf'))
pdfmetrics.registerFont(TTFont('MSYaHei', 'C:/Windows/Fonts/msyh.ttc'))
pdfmetrics.registerFont(TTFont('MSYaHei-Bold', 'C:/Windows/Fonts/msyhbd.ttc'))

FONT_BODY = 'MSYaHei'
FONT_BODY_BOLD = 'MSYaHei-Bold'
FONT_TITLE = 'MSYaHei-Bold'

KB = 'E:/director/prompt/knowledge'
OUTPUT = 'E:/director/PKTFILM电影学教程.pdf'

# Use Chinese fullwidth curly quotes everywhere in content to avoid
# collision with the Python string delimiter '"'.
LQ = '\u201c'  # left double quote "
RQ = '\u201d'  # right double quote "


def q(s):
    """Wrap content in Chinese curly quotes."""
    return LQ + s + RQ


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
STY_BODY = ParagraphStyle(
    'body', fontName=FONT_BODY, fontSize=10.5, leading=16,
    firstLineIndent=21, alignment=TA_JUSTIFY, textColor=colors.black,
    spaceAfter=3,
)
STY_BODY_NOINDENT = ParagraphStyle('body_ni', parent=STY_BODY, firstLineIndent=0)
STY_H1 = ParagraphStyle(
    'h1', fontName=FONT_TITLE, fontSize=22, leading=30,
    alignment=TA_LEFT, textColor=colors.HexColor('#1a365d'),
    spaceBefore=6, spaceAfter=14,
)
STY_PART = ParagraphStyle(
    'part', fontName=FONT_TITLE, fontSize=28, leading=40,
    alignment=TA_CENTER, textColor=colors.HexColor('#0b2545'),
    spaceBefore=40, spaceAfter=20,
)
STY_PART_SUB = ParagraphStyle(
    'part_sub', fontName=FONT_BODY, fontSize=13, leading=20,
    alignment=TA_CENTER, textColor=colors.HexColor('#3b5998'), spaceAfter=12,
)
STY_H2 = ParagraphStyle(
    'h2', fontName=FONT_TITLE, fontSize=16, leading=24,
    alignment=TA_LEFT, textColor=colors.HexColor('#244b7a'),
    spaceBefore=14, spaceAfter=6,
)
STY_H3 = ParagraphStyle(
    'h3', fontName=FONT_TITLE, fontSize=13, leading=20,
    alignment=TA_LEFT, textColor=colors.HexColor('#2b6cb0'),
    spaceBefore=10, spaceAfter=4,
)
STY_H4 = ParagraphStyle(
    'h4', fontName=FONT_BODY_BOLD, fontSize=11, leading=17,
    alignment=TA_LEFT, textColor=colors.HexColor('#333333'),
    spaceBefore=6, spaceAfter=2,
)
STY_QUOTE = ParagraphStyle(
    'quote', fontName=FONT_BODY, fontSize=10, leading=15,
    leftIndent=18, rightIndent=10, firstLineIndent=0,
    alignment=TA_JUSTIFY, textColor=colors.HexColor('#333333'),
    backColor=colors.HexColor('#fdf6e3'),
    borderColor=colors.HexColor('#d9b382'), borderWidth=0,
    borderPadding=(6, 8, 6, 12), spaceBefore=4, spaceAfter=6,
)
STY_NOTE = ParagraphStyle(
    'note', fontName=FONT_BODY, fontSize=9.5, leading=14,
    leftIndent=14, firstLineIndent=0, textColor=colors.HexColor('#555555'),
    alignment=TA_LEFT, spaceAfter=3,
)
STY_LIST = ParagraphStyle(
    'list', fontName=FONT_BODY, fontSize=10.5, leading=16,
    leftIndent=20, firstLineIndent=-12, alignment=TA_JUSTIFY,
    spaceAfter=2,
)
STY_TOC_1 = ParagraphStyle(
    'toc1', fontName=FONT_BODY_BOLD, fontSize=12, leading=18,
    leftIndent=0, spaceAfter=2,
)
STY_TOC_2 = ParagraphStyle(
    'toc2', fontName=FONT_BODY, fontSize=10.5, leading=16,
    leftIndent=18, spaceAfter=1,
)
STY_TOC_3 = ParagraphStyle(
    'toc3', fontName=FONT_BODY, fontSize=9.5, leading=14,
    leftIndent=36, textColor=colors.HexColor('#444444'), spaceAfter=0,
)
STY_COVER_TITLE = ParagraphStyle(
    'cov_t', fontName=FONT_TITLE, fontSize=38, leading=48,
    alignment=TA_CENTER, textColor=colors.HexColor('#0b2545'),
    spaceBefore=100, spaceAfter=20,
)
STY_COVER_SUB = ParagraphStyle(
    'cov_s', fontName=FONT_BODY, fontSize=16, leading=24,
    alignment=TA_CENTER, textColor=colors.HexColor('#3b5998'),
    spaceAfter=16,
)
STY_COVER_META = ParagraphStyle(
    'cov_m', fontName=FONT_BODY, fontSize=12, leading=20,
    alignment=TA_CENTER, textColor=colors.HexColor('#555555'),
    spaceAfter=6,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def esc(s):
    return htmllib.escape(s, quote=False)


def read_md(rel):
    path = os.path.join(KB, rel).replace('\\', '/')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f'[warn] missing {rel}: {e}')
        return ''


def parse_md(content):
    if content.startswith('---'):
        end = content.find('\n---', 3)
        if end != -1:
            content = content[end + 4:]
    lines = content.split('\n')
    sections = OrderedDict()
    current = '_preamble'
    sections[current] = []
    title = None
    for ln in lines:
        if ln.startswith('# ') and title is None:
            title = ln[2:].strip()
            continue
        if ln.startswith('## '):
            current = ln[3:].strip()
            sections[current] = []
            continue
        sections.setdefault(current, []).append(ln)
    return title, sections


BOLD_PAT = re.compile(r'\*\*(.+?)\*\*')
ITAL_PAT = re.compile(r'(?<!\*)\*([^*\n]+?)\*(?!\*)')
CODE_PAT = re.compile(r'`([^`]+)`')
LINK_PAT = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')


def inline(text):
    t = esc(text)
    t = CODE_PAT.sub(lambda m: '<font color="#b95c00">' + esc(m.group(1)) + '</font>', t)
    t = LINK_PAT.sub(lambda m: '<u>' + m.group(1) + '</u>', t)
    t = BOLD_PAT.sub(lambda m: '<b>' + m.group(1) + '</b>', t)
    t = ITAL_PAT.sub(lambda m: '<i>' + m.group(1) + '</i>', t)
    return t


def make_table(rows, col_widths=None, header=True):
    if not rows:
        return None
    tbl_body_style = ParagraphStyle(
        'tcell', fontName=FONT_BODY, fontSize=9, leading=12,
        alignment=TA_LEFT, firstLineIndent=0,
    )
    tbl_head_style = ParagraphStyle(
        'thead', fontName=FONT_BODY_BOLD, fontSize=9.5, leading=12,
        alignment=TA_CENTER, textColor=colors.white, firstLineIndent=0,
    )
    wrapped = []
    for i, r in enumerate(rows):
        row_out = []
        for c in r:
            st = tbl_head_style if (i == 0 and header) else tbl_body_style
            row_out.append(Paragraph(inline(str(c)), st))
        wrapped.append(row_out)
    if col_widths is None:
        n = len(rows[0])
        total = 16 * cm
        col_widths = [total / n] * n
    t = Table(wrapped, colWidths=col_widths, repeatRows=1 if header else 0)
    ts = [
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#888888')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#bbbbbb')),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]
    if header:
        ts.append(('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')))
        for i in range(1, len(rows)):
            if i % 2 == 0:
                ts.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f0f4f8')))
    t.setStyle(TableStyle(ts))
    return t


def parse_md_table(block_lines):
    rows = []
    for ln in block_lines:
        ln = ln.strip()
        if not ln.startswith('|'):
            continue
        cells = [c.strip() for c in ln.strip('|').split('|')]
        if all(set(c) <= set('-: ') for c in cells):
            continue
        rows.append(cells)
    return rows


def render_section_lines(lines, flow):
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        s = ln.rstrip()
        if not s.strip():
            i += 1
            continue
        if s.lstrip().startswith('|'):
            block = []
            while i < n and lines[i].lstrip().startswith('|'):
                block.append(lines[i])
                i += 1
            rows = parse_md_table(block)
            if rows:
                tbl = make_table(rows)
                if tbl is not None:
                    flow.append(Spacer(1, 4))
                    flow.append(tbl)
                    flow.append(Spacer(1, 6))
            continue
        if s.startswith('### '):
            flow.append(Paragraph(inline(s[4:].strip()), STY_H3))
            i += 1
            continue
        if s.startswith('#### '):
            flow.append(Paragraph(inline(s[5:].strip()), STY_H4))
            i += 1
            continue
        if s.startswith('> '):
            block = []
            while i < n and lines[i].startswith('> '):
                block.append(lines[i][2:])
                i += 1
            flow.append(Paragraph(inline(' '.join(block)), STY_QUOTE))
            continue
        if re.match(r'^\s*[-*]\s+', s):
            while i < n and re.match(r'^\s*[-*]\s+', lines[i] or ''):
                item = re.sub(r'^\s*[-*]\s+', '', lines[i])
                flow.append(Paragraph('• ' + inline(item), STY_LIST))
                i += 1
            continue
        if re.match(r'^\s*\d+\.\s+', s):
            while i < n and re.match(r'^\s*\d+\.\s+', lines[i] or ''):
                m = re.match(r'^\s*(\d+)\.\s+(.*)', lines[i])
                if m:
                    flow.append(Paragraph(m.group(1) + '. ' + inline(m.group(2)), STY_LIST))
                i += 1
            continue
        para = [s]
        i += 1
        while i < n:
            nxt = lines[i]
            if not nxt.strip():
                break
            if nxt.lstrip().startswith(('#', '|', '-', '*', '>')):
                break
            if re.match(r'^\s*\d+\.\s+', nxt):
                break
            para.append(nxt.rstrip())
            i += 1
        flow.append(Paragraph(inline(' '.join(para)), STY_BODY))


CUR_PART = ''
CUR_CHAPTER = ''


def set_running(part, chapter):
    global CUR_PART, CUR_CHAPTER
    CUR_PART = part
    CUR_CHAPTER = chapter


class RunningHeader(Flowable):
    """Zero-height marker that updates CUR_PART/CUR_CHAPTER at layout time.

    Appending this to the story *before* a chapter heading ensures the running
    header on every subsequent page reflects the chapter currently being laid
    out, not the final values left over from story construction.
    """

    def __init__(self, part, chapter):
        Flowable.__init__(self)
        self.part = part
        self.chapter = chapter
        self.width = 0
        self.height = 0

    def wrap(self, availWidth, availHeight):
        return (0, 0)

    def draw(self):
        set_running(self.part, self.chapter)


def draw_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    if doc.page > 2:
        canvas.setFont(FONT_BODY, 8)
        canvas.setFillColor(colors.HexColor('#666666'))
        canvas.drawString(2 * cm, h - 1.3 * cm, 'PKTFILM 电影学教程 · v1.3')
        right = (CUR_PART + ' · ' + CUR_CHAPTER) if CUR_PART else ''
        canvas.drawRightString(w - 2 * cm, h - 1.3 * cm, right)
        canvas.setStrokeColor(colors.HexColor('#cccccc'))
        canvas.setLineWidth(0.3)
        canvas.line(2 * cm, h - 1.5 * cm, w - 2 * cm, h - 1.5 * cm)
    canvas.setFont(FONT_BODY, 9)
    canvas.setFillColor(colors.HexColor('#444444'))
    canvas.drawCentredString(w / 2, 1.2 * cm, '— ' + str(doc.page) + ' —')
    canvas.restoreState()


class DocWithTOC(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            style = flowable.style.name
            txt = flowable.getPlainText()
            if style == 'h1':
                self.notify('TOCEntry', (0, txt, self.page))
            elif style == 'h2':
                self.notify('TOCEntry', (1, txt, self.page))
            elif style == 'h3':
                self.notify('TOCEntry', (2, txt, self.page))


# ---------------------------------------------------------------------------
# Writing helpers
# ---------------------------------------------------------------------------

def lead_para(text, flow):
    flow.append(Paragraph(inline(text), STY_BODY))


def narrative_intro(flow, text):
    flow.append(Paragraph(inline(text), STY_BODY))


SECTION_TITLE_CN = {
    'TL;DR': '一、核心要义',
    'Definitions': '二、术语释义',
    'Key terms': '三、关键术语与列表',
    'Context & problem': '四、问题语境',
    'Claims': '五、核心论点',
    'Method / How to use': '六、实操方法',
    'Debates & limits': '七、争议与局限',
    'Directing takeaways': '八、导演/创作要点',
    'Common confusions': '九、常见混淆',
    'Matrix': '对照矩阵',
    'One-liners': '一句话对照',
    'Non-overlapping differences': '不可互换的差异',
    'Confusions': '常见混淆',
    'Analysis recipe': '分析方法',
    'Exercises': '练习',
    'The question it answers': '本法要解答的问题',
    'Decision mapping': '决策映射',
    'Anti-patterns': '常见反例',
    'Reflection prompts': '反思提示',
    'Seed list': '素材清单',
}


def render_one_section(flow, name, lines):
    cn = SECTION_TITLE_CN.get(name, name)
    flow.append(Paragraph(inline(cn), STY_H3))
    render_section_lines(lines, flow)


def render_kb_section(flow, rel_path, section_order=None, exclude=None,
                      title_override=None, skip_common=True):
    content = read_md(rel_path)
    if not content:
        flow.append(Paragraph('[缺失文件: ' + rel_path + ']', STY_NOTE))
        return
    title, sections = parse_md(content)
    default_order = [
        'TL;DR', 'Definitions', 'Key terms', 'Context & problem',
        'Claims', 'Method / How to use', 'Debates & limits',
        'Directing takeaways', 'Common confusions',
    ]
    common_skip = {'Links & relations', 'Open questions', 'Changelog', '_preamble',
                   '[[Links]]'}
    order = section_order or default_order
    rendered = set()
    for name in order:
        if name in sections:
            render_one_section(flow, name, sections[name])
            rendered.add(name)
    for name, lines in sections.items():
        if name in rendered:
            continue
        if skip_common and name in common_skip:
            continue
        if exclude and name in exclude:
            continue
        render_one_section(flow, name, lines)
        rendered.add(name)


def chapter_heading(flow, num, title, part_label):
    flow.append(PageBreak())
    flow.append(RunningHeader(part_label, '第 ' + str(num) + ' 章'))
    flow.append(Spacer(1, 30))
    flow.append(Paragraph('第 ' + str(num) + ' 章　' + esc(title), STY_H1))
    line_tbl = Table([['']], colWidths=[16 * cm], rowHeights=[0.02 * cm])
    line_tbl.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, colors.HexColor('#2b6cb0')),
    ]))
    flow.append(line_tbl)
    flow.append(Spacer(1, 10))


def section_heading(flow, num, title):
    flow.append(Paragraph(num + '　' + esc(title), STY_H2))


def part_cover(flow, roman, name_zh, name_en, blurb):
    flow.append(PageBreak())
    flow.append(RunningHeader('Part ' + roman, esc(name_zh)))
    flow.append(Spacer(1, 60))
    flow.append(Paragraph('Part ' + roman, STY_PART))
    flow.append(Paragraph(esc(name_zh), STY_PART))
    flow.append(Paragraph(esc(name_en), STY_PART_SUB))
    flow.append(Spacer(1, 20))
    blurb_style = ParagraphStyle(
        'pblurb', parent=STY_BODY, alignment=TA_CENTER,
        firstLineIndent=0, leftIndent=60, rightIndent=60,
        textColor=colors.HexColor('#333333'), fontSize=11, leading=18,
    )
    flow.append(Paragraph(esc(blurb), blurb_style))


def chapter_objectives(flow, goals, key_questions):
    cells = []
    head_style = ParagraphStyle('obj_h', fontName=FONT_BODY_BOLD, fontSize=11,
                                leading=16, textColor=colors.white, alignment=TA_LEFT)
    body_style = ParagraphStyle('obj_b', fontName=FONT_BODY, fontSize=10,
                                leading=15, textColor=colors.HexColor('#222222'),
                                alignment=TA_LEFT)
    cells.append([Paragraph('■ 本章学习目标', head_style)])
    for i, g in enumerate(goals, 1):
        cells.append([Paragraph(str(i) + '. ' + inline(g), body_style)])
    head_idx = len(cells)
    cells.append([Paragraph('■ 本章关键问题', head_style)])
    for q_text in key_questions:
        cells.append([Paragraph('• ' + inline(q_text), body_style)])
    t = Table(cells, colWidths=[16 * cm])
    ts = [
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#244b7a')),
        ('BACKGROUND', (0, head_idx), (0, head_idx), colors.HexColor('#244b7a')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#244b7a')),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(cells)):
        if i == head_idx:
            continue
        ts.append(('BACKGROUND', (0, i), (0, i), colors.HexColor('#f4f8fb')))
    t.setStyle(TableStyle(ts))
    flow.append(t)
    flow.append(Spacer(1, 10))


def chapter_summary(flow, items):
    flow.append(Spacer(1, 8))
    flow.append(Paragraph('■ 本章小结', STY_H3))
    for i, it in enumerate(items, 1):
        flow.append(Paragraph(str(i) + '. ' + inline(it), STY_LIST))


def chapter_quiz(flow, items, hint=''):
    flow.append(Spacer(1, 6))
    flow.append(Paragraph('■ 自测题', STY_H3))
    for i, qitem in enumerate(items, 1):
        flow.append(Paragraph(str(i) + '. ' + inline(qitem), STY_LIST))
    if hint:
        flow.append(Paragraph(inline(hint), STY_NOTE))


def chapter_further(flow, items):
    flow.append(Spacer(1, 4))
    flow.append(Paragraph('■ 延伸阅读', STY_H3))
    for it in items:
        flow.append(Paragraph('• ' + inline(it), STY_LIST))


def concept_bridge(flow, text):
    flow.append(Paragraph(inline(text), STY_BODY))


# ---------------------------------------------------------------------------
# Cover / Preface / TOC
# ---------------------------------------------------------------------------

def build_cover(flow):
    flow.append(Spacer(1, 120))
    flow.append(Paragraph('PKTFILM 电影学教程', STY_COVER_TITLE))
    flow.append(Paragraph('艺考编导专业完整理论与实战指南', STY_COVER_SUB))
    flow.append(Spacer(1, 40))
    flow.append(Paragraph('v1.3　基于《故事元素积累6》+ 网络资源扩展', STY_COVER_META))
    flow.append(Paragraph('作者　P0ckket', STY_COVER_META))
    flow.append(Paragraph('2026-04-21', STY_COVER_META))
    flow.append(Spacer(1, 60))
    note_style = ParagraphStyle('cover_note', parent=STY_COVER_META,
                                fontSize=10, textColor=colors.HexColor('#888888'))
    flow.append(Paragraph(
        '本教材所有引用均以【原文】【学界常见解释】【我的理解】【你的推断】四级标注,',
        note_style))
    flow.append(Paragraph('遵循 prompt/CLAUDE.md 证据分层守则。', note_style))


PREFACE_PARAGRAPHS = [
    '艺考编导专业的学生常常在同一个困境里反复挣扎:一方面必须记忆大量名词与公式——三幕剧、十五节拍、景别角度、主题六法、反差三层;另一方面又要在 20 分钟的考场内把这些碎片整合为一个可信、有张力、能打动老师的故事。大多数教辅书的问题在于,它们把这些条目列成了词典,却没有告诉学生条目之间如何咬合。本《PKTFILM 电影学教程》的写作动机,正是为了填补这条' + q('从术语到创作') + '之间的裂缝。',
    '本书以《故事元素积累6_merged.pdf》作为原始语料,并以我在知识库项目 director-kb(E:/director)中持续建设的 56 篇原子化笔记为骨架,最后扩充了网络公开资料与经典教材中的补充论述。它不是一本摘抄,而是一次系统化的重写——所有 bullet 被展开为论述段落,所有表格被还原为结构化的对比工具,所有概念被放入电影案例的语境里重新解释。',
    '在方法论上,本教材坚持三条原则:其一,证据分层——凡陈述必标明来源层级,区分【原文/作者观点】、【学界常见解释】、【我的理解】与【你的推断】,让读者可以自行评估可靠度;其二,原子化与可链接——每一个核心概念单独成节,并在章末提供跨章延伸阅读,使得任何一章都可以作为复习入口;其三,可持续进化——本教材跟随 director-kb 的 Changelog 机制一起演化,每一版都保留前版的缝合痕迹,不做静默覆盖。',
    '对于不同的读者,本书提供三条阅读路径。第一条是' + q('笔试冲刺路径') + ':按 Part I(叙事基础)与 Part VI(艺考实战操作)的顺序,配合 Part IV 的素材库,用最短时间获得一个能考试的框架。第二条是' + q('面试应答路径') + ':优先阅读 Part II(视听语言)、Part V(专题案例研究)与附录 B(世界经典电影摄影风格速查),以便在校考面试中面对任何一部陌生电影都能做出四维分析。第三条是' + q('长期学习路径') + ':从序言、Part I 按顺序读到附录,配合延伸阅读清单逐步深入——这是把本书当作' + q('电影学入门') + '的读法。',
    '最后需要说明的是,本书的理论立场并非价值中立。它默认西方古典叙事学(三幕剧、Snyder 十分类、Freytag 冲突法)作为艺考评分的隐性基准,同时尽力在每一章的' + q('争议与局限') + '里提示东方叙事、艺术电影、实验电影等替代路径。读者若要将本书用于专业电影研究或艺术创作,请自行将本书视作脚手架——真正有价值的作品一定从脚手架之外长出来。',
]


def build_preface(flow):
    flow.append(PageBreak())
    set_running('序言', 'Preface')
    flow.append(Paragraph('序言', STY_H1))
    for p in PREFACE_PARAGRAPHS:
        flow.append(Paragraph(inline(p), STY_BODY))
    flow.append(Spacer(1, 10))
    flow.append(Paragraph('——P0ckket,2026 年 4 月', STY_NOTE))


def build_toc(flow):
    flow.append(PageBreak())
    set_running('目录', 'Contents')
    flow.append(Paragraph('目录', STY_H1))
    toc = TableOfContents()
    toc.levelStyles = [STY_TOC_1, STY_TOC_2, STY_TOC_3]
    flow.append(toc)


# ---------------------------------------------------------------------------
# Chapters
# ---------------------------------------------------------------------------

def ch1(flow):
    part = 'Part I 叙事基础'
    chapter_heading(flow, 1, '故事的骨架', part)
    chapter_objectives(
        flow,
        goals=[
            '理解三幕剧的时间比例与情节点功能,能够把一个故事分为建置-对抗-结局三段。',
            '掌握十五节拍表的完整序列,能够在一部陌生商业片中识别出至少十个节拍。',
            '掌握冲突六大类型的分类逻辑,能够为任何故事确定主导冲突动力。',
            '理解故事核与反差三层,能够用一句话概括自己的故事并识别三层张力。',
            '学会主题表达六法,能够把价值观落地到情节、人物、意向等具体手段上。',
            '获得类型叙事总览(Snyder 十分类)的基础地图,为 Part III 的展开做铺垫。',
        ],
        key_questions=[
            '一个' + q('故事') + '究竟由哪些最小单元构成?是段落、节拍、还是场次?',
            '为什么西方剧作如此强调' + q('激励事件在前 1/4') + '?背后的观众心理是什么?',
            '冲突是单一变量还是多维结构?一个故事可以只有一种冲突吗?',
            '如何判断一个故事的' + q('反差') + '是否足够支撑 2000 字的长度?',
            '主题和题材的区别在哪里?为什么主题不能被' + q('说') + '出来?',
            '类型叙事与市场类型片标签的关系是什么?它们为何正交?',
        ])
    narrative_intro(
        flow,
        '在进入任何一条具体的创作技术之前,我们必须先回答一个最根本的问题:当我们说' + q('这是一个故事') + '的时候,我们到底在谈论什么?一个故事不是一堆事件的线性堆叠,也不是若干人物的肖像画展览,而是一套有开合呼应的结构——某件事打破了平衡,某个人被迫行动,经过反复的挫折与抉择,最终某种新的秩序得以建立。本章的六节,正是从六个不同的角度,为这种' + q('结构') + '建立工具。三幕剧给出段落比例,十五节拍给出节奏刻度,冲突六类给出动力来源,故事核给出压缩公式,主题六法给出落地手段,类型叙事给出困境地图。它们互相咬合,共同构成艺考编导专业最底层的叙事词汇表。')

    section_heading(flow, '1.1', '三幕剧结构(Three-Act Structure)')
    concept_bridge(
        flow,
        '三幕剧是西方主流剧作法里最基础的' + q('段落比例') + '规定。它把一个完整故事按照大约 1:2:1 的时间比切成三段——开端(Setup)、对抗(Confrontation)、结局(Resolution),并在段与段之间安置两个情节点(Plot Point)作为接缝。其中第一情节点就是我们常说的' + q('激励事件') + ',负责彻底打破主角的生活平衡;第二情节点则在故事的第二幕末尾,为主角提供一线生机,推动其进入最终决战。在艺考编讲故事的语境下,这套比例被进一步压缩成一个硬模板:300 字的第一幕、600 字的第二幕、300 字的第三幕,加上中间的情节点嵌入,一共约 1200 字——它只是 2000 字考场作文的主骨架,还留有空间进行后续的' + q('五事件') + '扩展(详见第 22 章)。')
    render_kb_section(flow, 'theory/three-act-structure.md', exclude={'TL;DR'})

    section_heading(flow, '1.2', '十五节拍表(Fifteen-Beat Sheet)')
    concept_bridge(
        flow,
        '如果说三幕剧告诉你' + q('故事分几段') + ',那么十五节拍表则回答' + q('每一段里具体发生什么') + '。这张由 Blake Snyder 在 2005 年《救猫咪》(Save the Cat!)中提出的清单,把三幕剧内部的叙事推进进一步拆解为十五个具有明确功能的节拍(beat)。它并不是三幕剧的替代品,而是其细粒度嵌入层——开场画面与终场画面互为呼应、主题在前五分钟被含蓄提出、铺垫用来展示主角的缺失、催化剂打破平衡、争执让主角进入两难、第二幕衔接点见证主角主动进入新世界、B 故事提供反差、游戏节拍卸力展现性格、中点制造伪胜利、坏蛋逼近让内外夹击、一无所有进入最低点、灵魂黑夜完成精神重生、第三幕衔接点找到一线希望、大高潮决出胜负、终场画面与开场呼应。它同时是一个写作检查表与一个看片分析工具。')
    render_kb_section(flow, 'theory/fifteen-beat-sheet.md', exclude={'TL;DR'})

    section_heading(flow, '1.3', '冲突六大类型(Six Types of Conflict)')
    concept_bridge(
        flow,
        '传统叙事学的' + q('人与人 / 人与自然 / 人与自己') + '三分法有一个根本问题:任何一部电影通常同时包含这三种冲突,使得分类失去实践价值。原笔记 p.28 提出的六类法——信息错位、力量失衡、资源稀缺、未知的深渊、现实与理想、个体与集体——按' + q('冲突的动力来源') + '重新切分,每部影片通常只有一个主导动力。它更细,也更可操作。比如同样是' + q('主角遇到困难') + ',但' + q('主角遇到一个看不清真面目的对手') + '属于信息错位(侦探、伙伴之情的底层),' + q('主角能力远低于对手') + '属于力量失衡(愚者成功、麻烦家伙),' + q('主角在一个规则系统里被碾压') + '属于个体与集体(被制度化)——这三种冲突触发的情感曲线完全不同。')
    render_kb_section(flow, 'theory/conflict-six-types.md', exclude={'TL;DR'})

    section_heading(flow, '1.4', '故事核与人物反差(Story Core and Character Contrast)')
    concept_bridge(
        flow,
        '艺考编讲故事的第一件工作不是写人物小传,不是列事件,而是先立故事核——用一句话把整个故事概括出来。这个公式极其简洁:故事核 = 谁 + 做什么 = 人物 + 行动,而且人物与行动之间必须构成反差。如果你无法用这样一句话说清楚你的故事,那故事核就没立住,后面所有段落都救不回来。在这一节,我们不仅要掌握这个公式,还要掌握原笔记 p.40 可能最锋利的一条原创理论——反差三层:人物张力(过去 vs 当下、自我 vs 非我)、情节张力(事件 vs 人物、命运 vs 抉择)、场面张力(整体 vs 局部、和谐 vs 突兀)。这三层张力对应三个创作工种——编剧、导演、摄影美术——一部杰出的电影通常三层同时运转。')
    render_kb_section(flow, 'theory/story-core-and-contrast.md', exclude={'TL;DR'})

    section_heading(flow, '1.5', '主题表达六法(Six Methods to Express Theme)')
    concept_bridge(
        flow,
        '主题是故事的中心思想,但主题不能直接喊出来,否则就变成了口号。学生在考场上最容易犯的错误,就是把主题写成' + q('对父爱的赞美') + q('血浓于水') + '这样的价值观陈述,然后让主角在高潮处说出来——这样的故事立刻塌掉。本节介绍的六法——情节表现、人物性格、语言情感色彩、对白独白旁白、结局表现、意向传达——的共同点在于:主题必须被' + q('演') + q('看') + q('听') + q('感') + ',绝不能被' + q('说') + '。六法之间有一个从最含蓄到最明显的光谱:意向 > 情感色彩 > 人物 > 情节 > 结局 > 对白。一个及格线以上的艺考故事通常同时混用两到三种方法。')
    render_kb_section(flow, 'theory/theme-expression-methods.md', exclude={'TL;DR'})

    section_heading(flow, '1.6', '类型叙事总览(Genre Narratives Overview)')
    concept_bridge(
        flow,
        'Snyder 在《救猫咪:写给电影人》(2007)里提出的十种普适性故事类型,是对市场标签(动作/爱情/恐怖)的一次根本性重组。它不按表面情绪分类,而按' + q('故事的核心困境结构') + '分类——于是《绿皮书》与《断背山》虽然题材完全不同,但同为' + q('伙伴之情') + '型(不完整的主角 + 补足他的伙伴 + 一个被迫相处的复杂情况);《楚门的世界》与《1984》虽然气质迥异,但同为' + q('被制度化') + '型(一个规则系统 + 一种个体选择 + 一种牺牲)。本节先给出类型叙事的总览地图,Part III 将对其中五类展开详述。')
    render_kb_section(flow, 'theory/genre-narratives-overview.md', exclude={'TL;DR'})

    chapter_summary(flow, [
        '三幕剧用 1:2:1 的比例把故事切为开端、对抗、结局三段,两个情节点是段落接缝。',
        '十五节拍表在三幕剧内再切出十五个具有明确功能的节拍,从开场画面到终场画面首尾呼应。',
        '冲突六类按动力来源划分,每部影片通常只有一个主导动力;它比' + q('三分法') + '更可操作。',
        '故事核 = 人物 + 行动,人物与行动之间必须构成反差;反差分人物、情节、场面三层。',
        '主题不能被说出来,而应通过情节、人物、语言色彩、对白、结局、意向六种手段被' + q('看到') + '。',
        '类型叙事是按困境结构而非市场情绪划分的十种普适范式,每种对应一组两难选择。',
    ])
    chapter_quiz(flow, [
        '简答:三幕剧中第一情节点和第二情节点各承担什么叙事功能?请写出至少三点差异。',
        '分析:以一部你熟悉的商业片为例,标注出其中至少八个十五节拍对应的时间位置。',
        '简答:为什么说冲突六类中的' + q('未知的深渊') + '与 Lovecraft 的宇宙恐怖观相通?',
        '分析:把' + q('一个法官包庇了一起杀人案') + '改写为有强反差的一句话故事核,并写出所用反差手法。',
        '简答:主题表达六法之中,为什么' + q('对白法') + '最容易用力过猛?举出两种避免方法。',
        '简答:' + q('伙伴之情') + '与' + q('被制度化') + '在困境结构上有何根本差异?参考第 14 章答案提示。',
        '练习:给定题目' + q('重男轻女') + ',请用' + q('类型-两难-主题') + '链条选出最合适的类型叙事并说明理由。',
        '简答:在艺考 2000 字编讲故事中,三幕剧的 300 + 600 + 300 硬比例为何还要留出 800 字空间?',
        '分析:用反差三层解析《霸王别姬》任选一场戏中同时运转的人物、情节、场面张力。',
        '简答:为什么 Snyder 的十分类在作者电影(侯孝贤、小津)面前会失效?写出至少两点原因。',
    ], hint='(答案提示见本章 1.1 / 1.2 / 1.3 / 1.4 / 1.5 / 1.6 各节,以及第 14 章类型方法论辨析)')
    chapter_further(flow, [
        '本书第 2 章 人物的构建:三位一体与欲望目标是故事核的具体落地',
        '本书第 3 章 叙事机制:激励事件与反差三层的独立展开',
        '本书第 13 章 Snyder 类型浅说:五种具体类型的详述',
        '附录 A 术语表:本章所有英文术语的完整中英对照',
    ])


def ch2(flow):
    part = 'Part I 叙事基础'
    chapter_heading(flow, 2, '人物的构建', part)
    chapter_objectives(flow,
        goals=[
            '掌握' + q('可怜 / 可信 / 可爱') + '三位一体的人物身份设计法,能够为任意主角检查三层钩子。',
            '理解救猫咪时刻的原理与适用情境,尤其是' + q('强势角色优先') + '的本土化补充。',
            '区分欲望(抽象)与目标(具体)的差异,并能为任一故事拆解' + q('缺点→困境→欲望→目标') + '链条。',
            '掌握人物弧光的三种启动方式(被动型、救赎型、责任型)及其选型原则。',
        ],
        key_questions=[
            '为什么说' + q('可爱') + '比' + q('可怜') + '更重要?这条优先级在文化差异中是否稳定?',
            '救猫咪时刻如果过于刻意,会不会反而变成' + q('塑料微笑') + '?如何避免?',
            '欲望与目标的拆分,对写作的具体益处是什么?',
            '人物弧光是否必须是正向的?负向弧光在艺考中能用吗?',
        ])
    narrative_intro(flow,
        '如果说第 1 章回答' + q('故事的骨架是什么') + ',本章则回答' + q('谁在这具骨架上行走') + '。人物不是故事的装饰品,而是驱动整套结构运转的动力源。观众在 90 分钟或 2000 字的篇幅里之所以愿意留下,不是因为情节曲折,而是因为他们信了一个具体的人并愿意跟他走到最后。本章的四节——三位一体、救猫咪时刻、欲望目标动机、人物弧光——分别对应人物设计的四个维度:身份的共情钩子、好感的锁定时机、动作的驱动系统、变化的演化路径。四者合起来,构成一个可操作的人物发动机。')

    section_heading(flow, '2.1', '可怜 / 可信 / 可爱三位一体(Character Trinity)')
    concept_bridge(flow,
        '这是艺考编讲故事最核心的人物身份设计法。' + q('可怜') + '让观众同情,' + q('可信') + '让观众觉得真实,' + q('可爱') + '让观众主动想看他过得好——三者不是并列,而是同一个人身上同时存在的三层钩子,缺一个观众就会松手。原笔记 p.1 给出的优先级是' + q('可爱 > 可信 > 可怜') + ',因为只有可怜的主角会变成悲情新闻、只有可信的主角会变成纪录片、只有可爱的主角会变成偶像剧——三者齐备,观众才愿意跟他走完 2000 字。')
    render_kb_section(flow, 'concepts/character/character-trinity.md', exclude={'TL;DR'})

    section_heading(flow, '2.2', '救猫咪时刻(Save the Cat Moment)')
    concept_bridge(flow,
        'Blake Snyder 2005 年在《救猫咪》里提出的这个概念,是' + q('可爱') + '维度的具体操作:主角出场后做的一件' + q('无功利的美好小事') + '——对孩子好、帮助下属、捡回失物、与动物互动。这件事不需要惊天动地,关键在于' + q('无偿') + ':没人看、没奖励、没目的。原笔记 p.33 特别补充的一条是' + q('救猫咪尤其适用于强势角色') + ',因为医生、律师、富商这类自带权威身份的主角在观众眼里天然带有' + q('反派潜质') + ',若不设救猫咪时刻,观众会默认他是坏人。这条本土化补充比 Snyder 原书的普适讨论更实用。')
    render_kb_section(flow, 'concepts/character/save-the-cat-moment.md', exclude={'TL;DR'})

    section_heading(flow, '2.3', '欲望 / 目标 / 动机(Desire / Goal / Motivation)')
    concept_bridge(flow,
        '学生写人物时最常踩的坑是把欲望和目标混为一谈——要么主角' + q('只有想法没有动作') + '(想变富但整部片什么都没做),要么' + q('只有动作没有想法') + '(一直在做事但不知道为什么)。本节的关键区分是:欲望是抽象的(想变富、想被爱、想自由),目标是具体的(去抢劫银行、结婚、离开这个国家),动机是触发欲望落到目标的外部或内部原因(母亲生病、一封信、一个死去的朋友)。欲望分原始(名利权情)与高级(奉献、牺牲、正义)两档,后者通常在人物弧光后半才浮现。')
    render_kb_section(flow, 'concepts/character/desire-goal-motivation.md', exclude={'TL;DR'})

    section_heading(flow, '2.4', '人物弧光机制(Character Arc Mechanism)')
    concept_bridge(flow,
        '弧光不是心理描写,而是' + q('缺点与目标反复碰撞') + '的结构。p.48 给出的单向链条——缺点→困境→欲望→目标→行动→结局——把整条弧光拆成六个节点,强制你回答:变什么?为什么要变?变的动力是什么?怎么变?其中最关键的机械前提是:主角不改变缺点就不能达成目标——这是弧光的内核。原笔记还给出三种典型的弧光启动方式:被动型(讨厌的人找上门)、救赎型(主角为过错弥补)、责任型(被迫接手一个不愿承担的任务)。三者对应不同的故事长度与情感调性。')
    render_kb_section(flow, 'concepts/character/character-arc-mechanism.md', exclude={'TL;DR'})

    chapter_summary(flow, [
        '人物三位一体的三层钩子是同一个人身上的共存维度,优先级为' + q('可爱 > 可信 > 可怜') + '。',
        '救猫咪时刻是' + q('可爱') + '的具体操作,必须无功利、且对强势角色尤其必要。',
        '欲望抽象、目标具体——写作时先定欲望再翻译为目标;原始欲望(名利权情)与高级欲望(奉献牺牲正义)两档之间的跨越是弧光的核心跳跃。',
        '人物弧光是' + q('缺点阻碍目标→主角被迫改变缺点→目标达成或不达成') + '的反馈循环,三种启动方式可按故事长度灵活选择。',
    ])
    chapter_quiz(flow, [
        '简答:原笔记为什么坚持' + q('可爱 > 可信 > 可怜') + '的优先级?这个排序在反英雄故事里成立吗?',
        '分析:以《教父》中维多·柯里昂为例,分析其' + q('救猫咪时刻') + '是如何被设计成' + q('顺便发生') + '的。',
        '练习:给一个你熟悉的艺考题目(如' + q('我的母亲') + '),写出主角的三位一体三层钩子。',
        '简答:欲望与动机的差异是什么?请用一句不超过二十字的口诀说清楚。',
        '分析:把' + q('我想变得富有') + '这一欲望翻译为至少三种不同性格(勤奋、冲动、懒惰)下的不同目标。',
        '简答:《百元之恋》的女主未赢得拳赛,为何仍属于' + q('正向弧光') + '?',
        '简答:人物弧光的三种启动方式各适合哪种故事长度与情感调性?',
        '分析:如果主角的缺点在故事中始终未被修正,故事是否一定失败?举两个反例。',
    ], hint='(答案提示见本章 2.1 / 2.2 / 2.3 / 2.4,以及第 20 章《百元之恋》案例展开)')
    chapter_further(flow, [
        '本书第 3 章 叙事机制:激励事件与欲望的耦合',
        '本书第 20 章 《百元之恋》缺点驱动型弧光完整案例',
        '本书第 15 章 人物素材库:更多可怜/可信/可爱的素材',
    ])


def ch3(flow):
    part = 'Part I 叙事基础'
    chapter_heading(flow, 3, '叙事机制', part)
    chapter_objectives(flow,
        goals=[
            '理解激励事件的时间位置、强度要求与' + q('难 + 一线生机') + '的内在张力。',
            '掌握困境的三种触发形态(突变/缓变/他人带来)及其对应的写作难度。',
            '独立展开反差三层理论,能够用之为任何剧本初稿做' + q('张力诊断') + '。',
        ],
        key_questions=[
            '激励事件与' + q('第一次冲突') + '的差异究竟在哪里?',
            '反差三层是否必须三层同时存在?各层之间有没有权重?',
        ])
    narrative_intro(flow,
        '本章把第 1 章中反复提及但未独立展开的两个叙事机制——激励事件与反差三层——分别放大考察。前者是三幕剧的' + q('情节点 1') + '与十五节拍表的' + q('催化剂') + '在同一概念下的不同命名;后者是原笔记 p.40 可能最有理论野心的一次原创,它把叙事张力拆分为人物、情节、场面三层。两者互为表里:激励事件是张力的触发点,反差三层是张力的展开面。')

    section_heading(flow, '3.1', '激励事件(Inciting Incident)')
    render_kb_section(flow, 'concepts/narrative/inciting-incident.md', exclude={'TL;DR'})

    section_heading(flow, '3.2', '反差三层:人物 / 情节 / 场面')
    render_kb_section(flow, 'concepts/narrative/contrast-three-layers.md', exclude={'TL;DR'})

    chapter_summary(flow, [
        '激励事件必须在故事前 1/4 发生,必须彻底打破平衡,必须催化主角动机,并同时留' + q('一线生机') + '。',
        '困境的三种触发形态各有写作难度:突变最易但易显巧合,缓变最考验伏笔,他人带来最适合' + q('离水之鱼') + '配方。',
        '反差三层——人物张力、情节张力、场面张力——各有两对对立项,杰出作品三层同时运转。',
        '三层分别对应三个创作工种(编剧、导演、摄影美术),其中场面张力最易被学生忽略。',
    ])
    chapter_quiz(flow, [
        '简答:激励事件的六条合格检查清单分别是什么?',
        '分析:以《亲爱的》《十七岁的单车》《这个杀手不太冷》三片为例,分别说明它们的困境触发形态。',
        '简答:反差三层理论中' + q('人物张力') + '的两对对立项分别适合用什么手段外化?',
        '分析:选一部你熟悉的电影,找出其中至少一个场面张力的具体镜头(画面中的不协调)。',
        '简答:为什么说' + q('人物张力是藏出来的,情节张力是等出来的,场面张力是设计出来的') + '?',
        '练习:为题目' + q('最后一次见面') + '构思激励事件的三种不同触发形态写作版本。',
    ], hint='(答案提示见本章 3.1 / 3.2,以及第 1 章 1.4 故事核反差原则)')
    chapter_further(flow, [
        '本书第 1 章 故事的骨架(三幕剧结构)',
        '本书第 22 章 五事件大纲法(激励事件 = 第二事件)',
    ])


def ch4(flow):
    part = 'Part II 视听语言'
    chapter_heading(flow, 4, '场面调度', part)
    chapter_objectives(flow,
        goals=[
            '获得视听语言八大类的总览地图,理解景别、角度、运动、光线、画幅、构图、色彩、声音之间的系统关系。',
            '掌握场面调度的核心——走位(blocking)与 180° 轴线规则。',
            '能够为一个简单场景(如两人对话)设计基础的走位与机位方案。',
        ],
        key_questions=[
            '为什么' + q('场面调度') + '既包括摄影机内的安排,也包括摄影机的位置选择?',
            '180° 规则的本质是什么?什么时候可以' + q('越轴') + '?',
        ])
    narrative_intro(flow,
        '从本章开始,我们从叙事的' + q('文字骨架') + '进入电影的' + q('视听肉身') + '。视听语言是把一个故事转化为一段可观看的时间的技术总和——它包含八大类:景别、角度、运动、光线、画幅、构图、色彩、声音。本章先用 4.1 节给出总览表,然后在 4.2 节讨论所有视听语言的共同起点——场面调度(mise-en-scène)与走位(blocking)。在后续第 5 至 12 章,八大类会被分别展开。')

    section_heading(flow, '4.1', '视听语言总览(Visual Language Overview)')
    render_kb_section(flow, 'concepts/cinematic-language/visual-language-overview.md', exclude={'TL;DR'})

    section_heading(flow, '4.2', '场面调度与走位(Blocking and Mise-en-scène)')
    render_kb_section(flow, 'concepts/cinematic-language/blocking-mise-en-scene.md', exclude={'TL;DR'})

    chapter_summary(flow, [
        '视听语言由八大类构成:景别、角度、运动、光线、画幅、构图、色彩、声音——它们不是并列而是相互叠加。',
        '场面调度(mise-en-scène)同时包含画面内元素的布置与摄影机位置的选择。',
        '走位(blocking)是演员在空间中的运动路径,必须在摄影前完成设计。',
        '180° 轴线规则是保证空间连续性的基础,越轴有特定情境下的表达价值(迷失、错位、分裂)。',
    ])
    chapter_quiz(flow, [
        '简答:请列出视听语言的八大类并说明它们各自处理的问题。',
        '分析:选一部熟悉的电影中的对话场景,画出其走位与机位示意图。',
        '简答:什么情况下可以' + q('越轴') + '?举两部电影中越轴的例子及其表达意图。',
        '简答:mise-en-scène 与' + q('摄影构图') + '的关系与差异是什么?',
        '练习:为一场' + q('男女主在咖啡馆分手') + '的戏设计三种不同走位,分别对应和解、对抗、冷漠三种基调。',
        '简答:场面调度如何承载主题?举一个具体的例子说明。',
    ], hint='(答案提示见本章 4.1 / 4.2 和附录 A)')
    chapter_further(flow, [
        '本书第 5-9 章 景别、角度、运动、光线、画幅与构图的分章展开',
        '本书第 19 章 《霸王别姬》忠诚的五重光谱——走位与戏台空间分析',
    ])


def ch5(flow):
    part = 'Part II 视听语言'
    chapter_heading(flow, 5, '景别与镜头功能', part)
    chapter_objectives(flow,
        goals=[
            '掌握从大远景到大特写的完整景别谱系及其叙事功能。',
            '熟悉 OTS、美式中景、意式中景等特殊景别的使用语境。',
            '获得' + q('景别美学原则') + '的决策清单。',
        ],
        key_questions=[
            '为什么特写是电影的' + q('情感加速器') + '?过度使用会产生什么副作用?',
            '在同一场戏里,景别序列如何反映人物的情感位移?',
        ])
    narrative_intro(flow,
        '景别(shot types)是摄影机与被摄主体之间的距离选择,它决定了观众在心理距离上站在哪里。远景让观众保持旁观,特写则把观众推进主角的瞳孔。景别的选择从来不是技术问题,而是伦理问题——导演在决定景别的那一刻,就在决定观众与人物的情感距离。')

    section_heading(flow, '5.1', '景别系统(Shot Types)')
    render_kb_section(flow, 'concepts/cinematic-language/shot-types.md', exclude={'TL;DR'})

    section_heading(flow, '5.2', '景别选择的美学原则')
    concept_bridge(flow,
        '景别的美学原则可以浓缩为三条:一、从远到近对应' + q('从客观到主观') + '的心理移动;二、同一场戏内的景别序列应该与情感的起伏同步;三、特写只在情感峰值使用,否则贬值。以下几个经典案例可以说明这些原则的落实:希区柯克的《迷魂记》中 Scottie 看向 Madeleine 的特写被严格控制在关键情感节点,这使得特写一出现就带有不可逆的情感重量;《谁先爱上他的》结尾三妹的特写长久停留,把' + q('原谅') + '这一抽象主题落到一张脸上;而戈达尔的《精疲力尽》大量使用远景 + 中景的交替,刻意避开特写,以此保持人物的' + q('客观距离') + ',让观众始终停留在观察者位置而非共情者位置。')
    flow.append(Paragraph('景别选择决策表', STY_H4))
    rows = [
        ['情境', '首选景别', '理由'],
        ['人物进入新环境', '大远景 / 远景', '让环境对人物产生压倒感'],
        ['两人交谈(平等)', '双人中景', '同一画框建立对等关系'],
        ['两人交谈(权力不对等)', '单人特写 + 过肩', '强势者被框进小景框'],
        ['情感爆发瞬间', '特写 / 大特写', '消除一切环境干扰'],
        ['动作场面', '全景 / 中景', '保留动作完整性'],
        ['日常平静段落', '中景', '最接近人眼距离,舒适'],
        ['悬念铺设', '远景带小特写', '让观众看到但没完全看清'],
        ['结尾告别 / 和解', '中景 → 远景 → 大远景', '情感抽离,空间吞没人物'],
    ]
    flow.append(make_table(rows))

    chapter_summary(flow, [
        '景别是观众与人物之间的心理距离表,从大远景到大特写形成连续光谱。',
        '特写是情感加速器,过度使用会让关键时刻失去重量。',
        '一场戏内的景别序列应与情感曲线同步,' + q('从远到近') + '对应' + q('从客观到主观') + '。',
        'OTS、美式中景、意式中景等特殊景别有各自适用的语境与权力暗示。',
    ])
    chapter_quiz(flow, [
        '简答:列出从大远景到大特写的完整景别并说明各自的心理距离含义。',
        '分析:以《迷魂记》或《谁先爱上他的》为例,分析导演在关键场景的景别使用策略。',
        '简答:OTS(过肩)、美式中景、意式中景各自的视觉特征是什么?',
        '简答:为什么' + q('在同一场戏内从中景切到特写') + '比' + q('直接用特写开场') + '效果更强?',
        '练习:为一场' + q('父女久别重逢') + '的戏设计 5-7 个景别的序列,并说明每个景别的情感意图。',
        '简答:大远景何时承担主观功能?举一个打破' + q('大远景 = 客观') + '惯例的例子。',
        '分析:观察戈达尔的某一部电影,分析他为何刻意回避特写。',
        '简答:景别过渡的硬切与渐变(推拉)在观众心理效果上有何差异?',
    ], hint='(答案提示见本章 5.1 / 5.2,以及第 7 章 7.1 基础运动)')
    chapter_further(flow, [
        '本书第 7 章 摄影机运动(推拉与景别过渡)',
        '本书第 9 章 画幅与构图(景别与画幅的耦合)',
        '附录 B 世界经典电影摄影风格速查',
    ])


def ch6(flow):
    part = 'Part II 视听语言'
    chapter_heading(flow, 6, '摄影角度', part)
    chapter_objectives(flow,
        goals=[
            '掌握平视、仰视、俯视、斜视、鸟瞰五种基本角度的心理效应。',
            '理解角度与权力关系之间的符号学对应。',
        ],
        key_questions=[
            '为什么仰视天然带权威?这种习惯是否在所有文化中稳定?',
            '斜视角(Dutch angle)除了' + q('不安') + ',还能表达什么?',
        ])

    section_heading(flow, '6.1', '五种基本角度(Camera Angles)')
    render_kb_section(flow, 'concepts/cinematic-language/camera-angles.md', exclude={'TL;DR'})

    section_heading(flow, '6.2', '角度与权力关系')
    concept_bridge(flow,
        '摄影角度的符号学核心是权力。仰视让被摄者变大,俯视让其变小,平视把主体放在与观众同等的位置。这套惯例在好莱坞经典时代被大量体制化——《公民凯恩》的仰视镜头使凯恩被' + q('顶住了天花板') + '的压迫;《教父》大量使用俯视镜头俯瞰柯里昂家族的餐桌,把餐桌拍成' + q('审判席') + ';希区柯克《惊魂记》的仰视+俯视交替出现在 Norman 与 Marion 对话的戏中,预示着权力的悄然翻转。角度不是简单的物理位置,而是一次关于' + q('谁在看') + q('谁被看') + q('谁有裁判权') + '的伦理声明。')

    chapter_summary(flow, [
        '摄影角度直接投射权力关系:仰视=权威,俯视=弱势,平视=对等,斜视=失衡,鸟瞰=命运。',
        '角度的使用在好莱坞被体制化,但不同文化里的感知并不完全稳定。',
        '斜视角除了不安,也可表达诗意混乱、梦境、醉意、主观视角切换。',
    ])
    chapter_quiz(flow, [
        '简答:列出五种基本角度并说明各自的心理暗示。',
        '分析:以《公民凯恩》或《教父》为例,分析一段仰/俯视交替的场景及其权力意义。',
        '简答:斜视角(Dutch angle)在哪些情境下可以不表达' + q('不安') + '?举两例。',
        '简答:仰视能否用于反派塑造?效果是什么?',
        '练习:设计一场' + q('教师训学生') + '的戏,用角度的渐变反映权力翻转。',
        '简答:鸟瞰镜头在当代无人机普及后,是否已经贬值?',
    ], hint='(答案提示见本章 6.1 / 6.2,以及第 19 章《霸王别姬》分析)')
    chapter_further(flow, [
        '本书第 4 章 场面调度:角度选择与走位的耦合',
        '本书第 19 章 《霸王别姬》戏台上下的角度对比',
    ])


def ch7(flow):
    part = 'Part II 视听语言'
    chapter_heading(flow, 7, '摄影机运动', part)
    chapter_objectives(flow,
        goals=[
            '掌握推、拉、摇、移、跟、升、降七种基础运动的功能与适用时机。',
            '了解十四种常见运动设备(dolly、crane、steadicam、gimbal 等)的特点。',
            '记住 31 种运镜类型的速查表,能够在作品分析中准确命名。',
            '专题掌握 Dolly Zoom(希区柯克变焦)的原理与使用语境。',
        ],
        key_questions=[
            '推镜头与变焦推(zoom-in)在视觉心理上为何不同?',
            '长镜头是否天然优于切换?两者的美学立场分别是什么?',
        ])
    render_kb_section(flow, 'concepts/cinematic-language/camera-movement.md', exclude={'TL;DR'})

    section_heading(flow, '7.4', 'Dolly Zoom 专题(希区柯克变焦)')
    concept_bridge(flow,
        'Dolly Zoom 是希区柯克 1958 年在《迷魂记》中首次使用的技术——摄影机在轨道上推进的同时镜头反向变焦,或反之。这造成一个奇异的视觉效果:人物大小不变,但背景被压缩或拉伸。它的心理效应是' + q('世界在动而我没动') + ',精准对应眩晕、失重、现实脱落的主观体验。斯皮尔伯格在《大白鲨》中用它表达男主看见鲨鱼的瞬间;杰克逊的《指环王》用它表现佛罗多被戒指吞噬的时刻。Dolly Zoom 之所以难用,是因为它的视觉极端性使其一出现就必然成为场景的记忆点——用错位置,整部电影都会被这一镜头' + q('绑架') + '。')

    chapter_summary(flow, [
        '七种基础运动——推、拉、摇、移、跟、升、降——各自对应不同的心理效应和空间处理。',
        '运镜设备从手持到机械臂再到稳定器,物质基础决定可实现的运动类型。',
        '31 种运镜类型速查表是分析片段时准确命名的必备工具。',
        'Dolly Zoom 是视觉化' + q('眩晕/失重/世界脱落') + '的专属技术,使用须慎。',
    ])
    chapter_quiz(flow, [
        '简答:推、拉、摇、移、跟、升、降七种运动的基本心理效应分别是什么?',
        '分析:以一部长镜头闻名的电影(如《1917》《俄罗斯方舟》)为例,分析长镜头的美学立场。',
        '简答:dolly 与 steadicam 在视觉质感上有何差异?适用场景各自是什么?',
        '简答:变焦推(zoom-in)与 dolly-in 的根本差异是什么?',
        '练习:为一场' + q('主角得知家人去世') + '的戏设计一个 Dolly Zoom 镜头的位置与方向。',
        '简答:希区柯克在《迷魂记》中首次使用 Dolly Zoom 的初衷是什么?',
        '分析:标注一部你熟悉的电影的前五分钟,列出出现的所有运镜类型。',
        '简答:当代无人机镜头是否已让传统 crane 运动贬值?请结合作品讨论。',
        '简答:手持运动在当代电影中被广泛使用,它的表达立场是什么?',
        '简答:长镜头是否必然优于切换?请从' + q('叙事控制权') + '角度讨论。',
    ], hint='(答案提示见本章 7.1-7.4,以及附录 B 世界经典电影风格)')
    chapter_further(flow, [
        '本书第 4 章 场面调度:运动与走位的配合',
        '附录 B 世界经典电影摄影风格速查:67 部电影的运动风格标记',
    ])


def ch8(flow):
    part = 'Part II 视听语言'
    chapter_heading(flow, 8, '光线设计', part)
    chapter_objectives(flow,
        goals=[
            '区分硬光与软光的视觉特征和情绪功能。',
            '掌握三点布光系统(key / fill / back)的基础原理。',
            '理解高调与低调(high-key / low-key)的情绪对比。',
            '熟悉顺光、侧光、逆光、顶光以及伦勃朗光、分割光等专门布光方案。',
        ],
        key_questions=[
            '为什么低调布光在黑色电影(film noir)中成为类型标签?',
            '自然光(如侯孝贤、是枝裕和)与人工布光的美学立场差异?',
        ])
    render_kb_section(flow, 'concepts/cinematic-language/lighting-techniques.md', exclude={'TL;DR'})

    chapter_summary(flow, [
        '硬光带来明确阴影与戏剧感,软光带来均匀柔和与写实感——两者是情绪的二元对立基座。',
        '三点布光是电影光的语法底层:主光(key)定形、辅光(fill)填暗、背光(back)分离前后。',
        '高调与低调不仅是明暗比例,更是类型与情绪的符号声明。',
        '伦勃朗光、分割光、蝴蝶光等经典布光方案各有肖像学功能,应当灵活组合。',
    ])
    chapter_quiz(flow, [
        '简答:硬光与软光的视觉差异是什么?各自适合什么题材?',
        '简答:三点布光中主光、辅光、背光各自承担什么功能?缺一个会怎样?',
        '简答:低调布光为何成为 film noir 的类型标签?从内容层面找两个原因。',
        '分析:以是枝裕和或侯孝贤为例,分析其对自然光的偏好的美学立场。',
        '简答:伦勃朗光的视觉特征是什么?它如何传达' + q('沉思') + '的情绪?',
        '练习:为' + q('深夜审讯室') + '一场戏设计低调布光方案。',
        '简答:顺光与逆光对人物情绪的影响各自是什么?',
        '简答:顶光在何种情境下表达' + q('天意 / 命运') + '?在何种情境下表达' + q('压迫') + '?',
    ], hint='(答案提示见本章 8.1-8.4,以及附录 B)')
    chapter_further(flow, [
        '本书第 9 章 画幅与构图(光影在构图内的分布)',
        '附录 B 世界经典电影摄影风格速查(光线风格标记)',
    ])


def ch9(flow):
    part = 'Part II 视听语言'
    chapter_heading(flow, 9, '画幅与构图', part)
    chapter_objectives(flow,
        goals=[
            '熟悉从 1.33 到 2.76 的完整画幅历史及其美学含义。',
            '掌握 15 种核心构图法的视觉识别与使用时机。',
            '了解 13 种色调系统(warm / cool / monochrome / pastel / high-contrast 等)。',
            '建立' + q('情绪-构图-景别') + '三者联动的决策映射。',
        ],
        key_questions=[
            '为什么 Anamorphic 变形镜头在当代又被大量使用?',
            '对称构图与非对称构图各自对应什么世界观?',
        ])
    section_heading(flow, '9.1', '画幅比例史(Aspect Ratios)')
    render_kb_section(flow, 'concepts/cinematic-language/aspect-ratios.md', exclude={'TL;DR'})

    section_heading(flow, '9.2', '15 种核心构图法(Composition Styles)')
    render_kb_section(flow, 'concepts/cinematic-language/composition-styles.md', exclude={'TL;DR'})

    section_heading(flow, '9.3', '13 种色调系统')
    concept_bridge(flow,
        '色调系统可以按' + q('色温 × 饱和度 × 对比度') + '三轴组合,形成 13 种常用色调。暖调(warm)适合亲密与怀旧;冷调(cool)适合孤独与疏离;单色(monochrome)强化主题集中度;粉彩(pastel)适合童话与梦境;高对比适合戏剧性类型(黑色电影、犯罪片);低对比适合散文电影与日常题材。色调不是后期调色的技术问题,而是前期美术与灯光的协同设计——调色只能' + q('修正') + '错误的前期,不能创造色调本身。')

    section_heading(flow, '9.4', '情绪-构图-景别速查')
    rows = [
        ['情绪', '首选构图', '首选景别', '典型色调'],
        ['孤独 / 疏离', '对称中置 + 大量负空间', '大远景', '冷调 / 低饱和'],
        ['亲密 / 依偎', '双人中景 + 向心', '中景 / 近景', '暖调 / 中饱和'],
        ['压迫 / 窒息', '框中框 / 顶部压迫', '中近景', '低调 / 高对比'],
        ['眩晕 / 错乱', '斜视角 + 非对称', '特写', '单色 / 变形'],
        ['冲突 / 对抗', '对角线 / 分离构图', '双人中景 OTS', '高对比 / 冷暖并置'],
        ['和解 / 救赎', '对称 / 圆形构图', '远景渐近', '暖调渐亮'],
        ['审判 / 权威', '俯视 + 中央对称', '中景俯视', '冷调'],
        ['回忆 / 怀旧', '前景遮挡 + 中心', '中近景', '暖调 / 低饱和'],
    ]
    flow.append(make_table(rows))

    chapter_summary(flow, [
        '画幅不仅是画框比例,更是世界观的声明——Anamorphic 对应' + q('被压缩的命运') + ',1.33 对应' + q('方正与古典') + ',2.35+ 对应' + q('地平线的诗意') + '。',
        '15 种构图法不是互斥选项,而是叠加语法——一个镜头可以同时是三分法 + 框中框 + 引导线。',
        '色调系统是前期与后期共同作用的结果,调色只能修正,不能创造。',
        '情绪、构图、景别三者应同步设计;一份完整的分镜表必须同时给出三项决策。',
    ])
    chapter_quiz(flow, [
        '简答:从 1.33 到 2.76 的主要画幅比例各自对应什么历史时期与美学倾向?',
        '简答:Anamorphic 镜头为何在当代又被大量使用?它的' + q('光斑') + '是如何形成的?',
        '分析:以韦斯·安德森的一部电影为例,分析其对称构图与色调系统的协同设计。',
        '练习:为一场' + q('老母亲在厨房独自包饺子') + '的戏,设计构图 + 景别 + 色调的组合方案。',
        '简答:对称构图与非对称构图分别暗示什么世界观?',
        '简答:框中框(frame within frame)的心理效应是什么?何时使用有风险?',
        '简答:为什么冷暖并置构图常常出现在冲突场景?',
        '分析:对比《布达佩斯大饭店》与《七宗罪》的色调系统,说明前期美术的协同逻辑。',
        '简答:引导线构图如何把观众的视线' + q('推') + '到画面深处?',
        '简答:黄金分割与三分法在实操上是否等价?',
    ], hint='(答案提示见本章 9.1-9.4,以及附录 B)')
    chapter_further(flow, [
        '本书第 5 章 景别与镜头功能',
        '本书第 8 章 光线设计',
        '附录 B 世界经典电影摄影风格速查',
    ])


def ch10(flow):
    part = 'Part II 视听语言'
    chapter_heading(flow, 10, '声音设计', part)
    chapter_objectives(flow,
        goals=[
            '区分画内音(diegetic)与画外音(non-diegetic)的叙事边界。',
            '理解拟音(Foley)、环境音、人造声各自的功能。',
            '掌握音乐与沉默的叙事作用——沉默不是' + q('没有声音') + ',而是' + q('选择不出声') + '。',
            '接触 Michel Chion 的视听契约与三种聆听模式(因果/语义/简化)。',
        ],
        key_questions=[
            '音画对位与音画同步各自的美学立场?',
            '为什么' + q('电影里的沉默比音乐更难用') + '?',
        ])
    render_kb_section(flow, 'concepts/sound/sound-design.md', exclude={'TL;DR'})

    chapter_summary(flow, [
        '画内音与画外音的边界不是技术问题,而是叙事立场——把观众放在哪里听?',
        '拟音(Foley)不是' + q('还原真实') + ',而是' + q('重构可听性') + ';电影里的脚步声从来不是真的脚步。',
        '音乐与沉默互为镜像——最强的音乐瞬间往往紧接着一段沉默,反之亦然。',
        'Chion 的三种聆听模式帮助分析声音如何在信息、因果、质感三个层面同时运作。',
    ])
    chapter_quiz(flow, [
        '简答:画内音与画外音的判定标准是什么?举一个两者边界模糊的例子。',
        '简答:拟音与' + q('同期声') + '的差异是什么?拟音可以' + q('造假') + '到何种程度?',
        '分析:以一部你熟悉的电影为例,分析其沉默段落的叙事功能。',
        '简答:Chion 的' + q('视听契约') + '是什么?它如何解释' + q('观众为什么接受不真实的声音') + '?',
        '练习:为' + q('两人在雨中分别') + '的戏设计声音层级(雨声、脚步、呼吸、音乐、沉默)。',
        '简答:音乐的主题动机(leitmotif)为何容易被用力过猛?',
    ], hint='(答案提示见本章 10.1-10.4,以及第 19 章《霸王别姬》京剧音乐分析)')
    chapter_further(flow, [
        '本书第 11 章 对白艺术(声音的语言层)',
        '本书第 19-21 章 案例研究中的声音使用',
    ])


def ch11(flow):
    part = 'Part II 视听语言'
    chapter_heading(flow, 11, '对白艺术', part)
    chapter_objectives(flow,
        goals=[
            '掌握六种台词技巧:潜台词、反问、重复、错位、沉默、打断。',
            '区分' + q('生活对话') + '与' + q('故事对话') + '的本质差异。',
        ],
        key_questions=[
            '什么样的台词一出口就' + q('脏') + '了整场戏?如何避免?',
            '潜台词的' + q('潜') + '在哪里?如何让观众听到没被说出的话?',
        ])
    render_kb_section(flow, 'concepts/dialogue/dialogue-six-techniques.md', exclude={'TL;DR'})

    section_heading(flow, '11.2', '生活对话 vs 故事对话')
    concept_bridge(flow,
        '生活对话充满冗余、重复、走神、客套——这是真实的,但不是戏剧的。故事对话则是经过筛选的生活对话:它保留真实的节奏感,但每一句都承担叙事或情感功能。一个典型对照是:生活里你会说' + q('我最近工作挺忙的,也没什么新鲜事') + ',故事里这句话要么被删除,要么被重写为' + q('我最近不想回家') + '——同样信息密度,后者直接指向冲突。艺考写作中最容易犯的错误是写成' + q('会议记录式对白') + '——人物轮流开口,每句话都在讲事实,没有一句有潜台词。')

    chapter_summary(flow, [
        '六种台词技巧各自处理信息、情感、权力的不同层面。',
        '故事对话是' + q('筛过的生活对话') + '——节奏真实,密度戏剧。',
        '潜台词是台词的隐形骨架——嘴上说 A,心里想 B,观众感受到 B。',
        '沉默与打断同样是' + q('台词') + '的一部分,且往往比说出口的话更有力。',
    ])
    chapter_quiz(flow, [
        '简答:列出六种台词技巧,并各举一个电影中的例子。',
        '分析:把一段' + q('生活对话') + '改写为' + q('故事对话') + ',保留信息密度但注入戏剧功能。',
        '简答:潜台词如何通过走位、道具、表情等非语言手段被' + q('听到') + '?',
        '简答:为什么重复是台词设计中最危险也最有力的技巧?',
        '练习:为一场' + q('男女主第一次见面') + '的戏写出含三次打断的对白。',
    ], hint='(答案提示见本章 11.1 / 11.2,以及 Part V 案例研究)')
    chapter_further(flow, [
        '本书第 10 章 声音设计',
        '本书第 19 章 《霸王别姬》对白与戏词的互文',
    ])


def ch12(flow):
    part = 'Part II 视听语言'
    chapter_heading(flow, 12, '符号与意象', part)
    chapter_objectives(flow,
        goals=[
            '掌握常见动物意象的文化语义与电影化用法。',
            '掌握道具象征的通则——一件道具如何从' + q('物件') + '变成' + q('意义锚') + '。',
        ],
        key_questions=[
            '为什么' + q('狗') + '在东方与西方电影中的象征含义存在差异?',
            '一件道具要出现几次才能被观众认出' + q('象征') + '?',
        ])
    section_heading(flow, '12.1', '动物意象(Animal Symbolism)')
    render_kb_section(flow, 'concepts/symbolism/animal-symbolism.md', exclude={'TL;DR'})

    section_heading(flow, '12.2', '道具象征通则(Prop Symbolism)')
    render_kb_section(flow, 'concepts/symbolism/prop-symbolism.md', exclude={'TL;DR'})

    chapter_summary(flow, [
        '动物意象自带文化前理解——狼、鹰、猫、狗、鱼在中西方语义并不完全同构。',
        '道具从' + q('物件') + '变为' + q('象征') + '的过程需要至少三次出现,且每次承担不同情感含义。',
        '符号的力量来自' + q('不说破') + '——一旦台词点明,象征即失效。',
    ])
    chapter_quiz(flow, [
        '简答:狼与狗在东西方电影中的象征差异是什么?',
        '分析:以《霸王别姬》中的宝剑或《公民凯恩》中的雪球为例,分析道具的三次出现如何积累意义。',
        '简答:道具象征与动物意象在创作中的使用顺序是什么?',
        '练习:设计一件贯穿全片的道具,写出它在开场、中点、结尾三次出现的情感含义。',
        '简答:为什么说' + q('意象最好的放置方法是藏而不是显') + '?',
    ], hint='(答案提示见本章 12.1 / 12.2,以及 Part IV 素材库)')
    chapter_further(flow, [
        '本书第 1 章 主题表达六法(意象传达即第六法)',
        '本书第 16 章 道具素材库',
        '本书第 19 章 《霸王别姬》道具使用分析',
    ])


def ch13(flow):
    part = 'Part III 类型叙事'
    chapter_heading(flow, 13, 'Snyder 类型浅说', part)
    chapter_objectives(flow,
        goals=[
            '掌握 Snyder 十分类中本书收录的五种类型的核心结构。',
            '能够判断一个故事属于哪种类型叙事,并推导其两难与主题。',
        ],
        key_questions=[
            '一个故事是否可以同时属于两种类型?主副类型如何区分?',
            '中国观众熟悉的' + q('武侠') + q('宫斗') + q('仙侠') + '各自属于 Snyder 的哪几类?',
        ])
    narrative_intro(flow,
        '第 1.6 节给出了类型叙事的总览,本章把其中五种——伙伴之情、麻烦家伙、变迁仪式、被制度化、惊悚片——一一展开。每种类型都有自己的三元素、两难选择、节拍配方与主题方向。这些类型是 Snyder 十分类的子集,选择它们是因为原笔记已有独立篇章;其余五类(金羊毛、Whydunit、Monster in the House、Out of the Bottle、Superhero)会在后续版本补充。')

    section_heading(flow, '13.1', '伙伴之情(Buddy Love)')
    render_kb_section(flow, 'genre/buddy-love.md', exclude={'TL;DR'})

    section_heading(flow, '13.2', '麻烦家伙(Dude with a Problem)')
    render_kb_section(flow, 'genre/dude-with-a-problem.md', exclude={'TL;DR'})

    section_heading(flow, '13.3', '变迁仪式(Rites of Passage)')
    render_kb_section(flow, 'genre/rites-of-passage.md', exclude={'TL;DR'})

    section_heading(flow, '13.4', '被制度化(Institutionalized)')
    render_kb_section(flow, 'genre/institutionalized.md', exclude={'TL;DR'})

    section_heading(flow, '13.5', '惊悚片要素(Thriller Elements)')
    render_kb_section(flow, 'genre/thriller-elements.md', exclude={'TL;DR'})

    chapter_summary(flow, [
        '伙伴之情 = 不完整主角 + 伙伴 + 复杂情况,两难是' + q('社交 vs 自我') + '。',
        '麻烦家伙 = 无辜主角 + 祸从天降 + 生死考验,两难是' + q('逃避 vs 面对') + '。',
        '变迁仪式 = 生活问题 + 错误方法 + 真正方法,两难是' + q('接受 vs 逃避') + '。',
        '被制度化 = 规则集体 + 一种选择 + 一种牺牲,两难是' + q('两种思想体系之间的选择') + '。',
        '惊悚片强调' + q('主角知道某事但无法证明') + '的心理处境,核心是认知恐怖而非物理恐怖。',
    ])
    chapter_quiz(flow, [
        '简答:五种类型的三元素各自是什么?',
        '简答:' + q('伙伴之情') + '与' + q('爱情片') + '的差异是什么?',
        '分析:以《楚门的世界》为例,说明它为何属于' + q('被制度化') + '而非' + q('伙伴之情') + '。',
        '练习:为' + q('一个年轻医生在小镇发现医疗黑幕') + '设计惊悚片结构。',
        '简答:变迁仪式的三种典型生活问题是什么?',
        '简答:' + q('麻烦家伙') + '与' + q('被制度化') + '的核心差异是什么?(提示:对手是人还是规则系统)',
        '分析:选一部中国电影,判断它主导的类型叙事并说明理由。',
        '简答:类型叙事的' + q('混合') + '是否允许?主副类型如何划分?',
    ], hint='(答案提示见本章 13.1-13.5,以及第 14 章方法论辨析)')
    chapter_further(flow, [
        '本书第 14 章 方法论辨析:类型之间的对立与比较',
        '本书第 19 章 《霸王别姬》(伙伴之情 + 被制度化的混血)',
    ])


def ch14(flow):
    part = 'Part III 类型叙事'
    chapter_heading(flow, 14, '方法论辨析', part)
    chapter_objectives(flow,
        goals=[
            '理解形式主义与现实主义的根本分歧及其电影史谱系。',
            '掌握东西方故事价值标准的差异,尤其是' + q('文以载道') + '与' + q('探索人性') + '的对立。',
            '能够在伙伴之情与被制度化之间做精细区分,避免混淆。',
        ],
        key_questions=[
            '形式主义与现实主义是二元对立,还是光谱上的两极?',
            '东方叙事传统在艺考评分体系中是否被系统性低估?',
        ])
    section_heading(flow, '14.1', '形式主义 vs 现实主义(Formalism vs Realism)')
    render_kb_section(flow, 'comparison/formalism-vs-realism.md')

    section_heading(flow, '14.2', '东西方故事价值标准')
    render_kb_section(flow, 'comparison/east-west-story-standards.md')

    section_heading(flow, '14.3', '伙伴之情 vs 被制度化')
    render_kb_section(flow, 'comparison/buddy-love-vs-institutionalized.md')

    chapter_summary(flow, [
        '形式主义(爱森斯坦、格里菲斯)强调蒙太奇与构造,现实主义(巴赞、德西卡)强调长镜头与真实——两者是光谱两极,大部分作品在中间。',
        '东方叙事倾向' + q('文以载道') + ',强调家国与教化;西方倾向' + q('探索人性') + ',强调个体与疑问——这是艺考评分的隐性基准。',
        '伙伴之情与被制度化都有' + q('关系') + '元素,但前者对抗是' + q('自我 vs 他人') + ',后者是' + q('个体 vs 规则') + '——不要混淆。',
    ])
    chapter_quiz(flow, [
        '简答:形式主义与现实主义各自的代表导演与代表作是什么?',
        '简答:巴赞为何反对蒙太奇的过度使用?他的理论基础是什么?',
        '分析:把一部中国艺术电影放入' + q('东西方价值标准') + '坐标,说明它偏向哪一边。',
        '简答:伙伴之情与被制度化的' + q('对抗') + '对象有何本质差异?',
        '练习:为一个含' + q('爱情副线') + '的故事,判断它属于伙伴之情主类型还是爱情副线。',
        '简答:艺考评分系统为何默认西方叙事?这是否公平?',
    ], hint='(答案提示见本章 14.1-14.3,以及第 1.6 节类型总览)')
    chapter_further(flow, [
        '本书第 13 章 Snyder 类型浅说',
        '附录 B 世界经典电影摄影风格速查(包含中西方导演对照)',
    ])


def ch15(flow):
    part = 'Part IV 素材库'
    chapter_heading(flow, 15, '人物素材库', part)
    chapter_objectives(flow,
        goals=[
            '获得大量可直接套用的人物设计素材。',
            '掌握反派塑造与缺陷设计的素材库。',
            '熟悉穿着与性格的映射惯例。',
        ],
        key_questions=[
            '如何从' + q('素材') + '生成' + q('人物') + '而不只是' + q('标签') + '?',
        ])
    narrative_intro(flow,
        '素材库不是词典,而是可调用的原子池。本章以及第 16-18 章收集原笔记中整理的各类素材表格与清单——人物、反派、穿着、道具、场景、情感、家庭冲突、职业——用扁平化的方式保留它们最原始的面貌。使用原则是:先立故事核,再到素材库调取;不能反过来。')
    section_heading(flow, '15.1', '人物设计(Character Design Library)')
    render_kb_section(flow, 'story-elements/character-design-library.md', exclude={'TL;DR'})
    section_heading(flow, '15.2', '反派与缺陷(Antagonist and Flaws)')
    render_kb_section(flow, 'story-elements/antagonist-and-flaws-library.md', exclude={'TL;DR'})
    section_heading(flow, '15.3', '穿着与性格(Costume and Personality)')
    render_kb_section(flow, 'story-elements/costume-and-personality-library.md', exclude={'TL;DR'})

    chapter_summary(flow, [
        '人物素材库提供可直接套用的身份、性格、缺陷、穿着等原子。',
        '反派的塑造需要' + q('立场正当') + '——反派不是邪恶,是另一套合理的价值观。',
        '穿着是人物性格的无声自我介绍,惯例的使用与打破都是表达手段。',
    ])
    chapter_quiz(flow, [
        '简答:如何让一个反派' + q('立场正当') + '而不是单纯邪恶?',
        '练习:从素材库中选三条反差较大的缺陷组合,构造一个可信主角。',
        '简答:穿着与性格的映射惯例有哪些常见陷阱?如何避免?',
        '分析:以一部电影为例,说明其反派为何' + q('比主角更立体') + '。',
    ], hint='(答案提示见本章 15.1-15.3,以及第 2 章人物构建)')
    chapter_further(flow, [
        '本书第 2 章 人物的构建:三位一体与欲望目标',
        '本书第 18 章 职业素材库',
    ])


def ch16(flow):
    part = 'Part IV 素材库'
    chapter_heading(flow, 16, '道具与场景素材库', part)
    chapter_objectives(flow,
        goals=[
            '掌握' + q('道具八法') + '(或六法)的完整谱系——道具的多种功能。',
            '熟悉常见场景与环境的情绪惯例。',
            '了解悬念与冲突升级的素材库。',
        ],
        key_questions=[
            '一个场景的' + q('环境') + '如何成为' + q('第三个人物') + '?',
        ])
    section_heading(flow, '16.1', '道具与六用法(Props Library)')
    render_kb_section(flow, 'story-elements/props-and-six-uses-library.md', exclude={'TL;DR'})
    section_heading(flow, '16.2', '场景与环境(Scene and Setting)')
    render_kb_section(flow, 'story-elements/scene-and-setting-library.md', exclude={'TL;DR'})
    section_heading(flow, '16.3', '悬念与冲突升级(Suspense and Conflict)')
    render_kb_section(flow, 'story-elements/suspense-and-conflict-library.md', exclude={'TL;DR'})

    chapter_summary(flow, [
        '道具八法将道具的功能拆分为身份、记忆、冲突、象征等多重维度。',
        '场景本身就是一个人物——它有情绪、性格与轨迹。',
        '悬念升级的素材库提供从' + q('小异常') + '到' + q('大危机') + '的连续阶梯。',
    ])
    chapter_quiz(flow, [
        '简答:道具的' + q('八法') + '分别是什么?各举一例。',
        '练习:为一个' + q('老房子') + '场景写出它作为' + q('第三个人物') + '的性格描述。',
        '简答:悬念升级的阶梯如何避免' + q('一步到位') + '的坍塌?',
        '分析:以一部悬疑片为例,拆解其从' + q('小异常') + '到' + q('大危机') + '的升级链。',
    ], hint='(答案提示见本章 16.1-16.3,以及第 24 章道具生场景法)')
    chapter_further(flow, [
        '本书第 24 章 道具生场景法(含火柴完整例)',
        '本书第 12 章 符号与意象',
    ])


def ch17(flow):
    part = 'Part IV 素材库'
    chapter_heading(flow, 17, '情感与关系素材库', part)
    chapter_objectives(flow,
        goals=[
            '获得情感与关系的细分素材。',
            '掌握家庭冲突的典型模式。',
        ],
        key_questions=[
            '家庭冲突为何是艺考命题的高频区?',
        ])
    section_heading(flow, '17.1', '情感与关系(Emotion and Relation)')
    render_kb_section(flow, 'story-elements/emotion-and-relation-library.md', exclude={'TL;DR'})
    section_heading(flow, '17.2', '家庭冲突(Family Conflict)')
    render_kb_section(flow, 'story-elements/family-conflict-library.md', exclude={'TL;DR'})

    chapter_summary(flow, [
        '情感与关系的素材应当细分——' + q('母女') + '比' + q('家人') + '更可写,' + q('老同学') + '比' + q('朋友') + '更可写。',
        '家庭冲突是艺考命题的高频区,因为它兼顾了个人性与社会性。',
    ])
    chapter_quiz(flow, [
        '简答:为什么' + q('母女矛盾') + '比' + q('家人矛盾') + '更适合 2000 字编讲故事?',
        '练习:从素材库选一对关系与一个典型冲突,写出故事核。',
        '简答:家庭冲突的类型学中,哪几类最容易走向和解?哪几类最容易走向破碎?',
    ], hint='(答案提示见本章 17.1 / 17.2,以及 Part VI 艺考实战)')
    chapter_further(flow, [
        '本书第 26 章 艺考面试策略(家庭题材应答模板)',
        '本书第 19-21 章 案例研究',
    ])


def ch18(flow):
    part = 'Part IV 素材库'
    chapter_heading(flow, 18, '职业素材库', part)
    chapter_objectives(flow,
        goals=[
            '熟悉医生与警察两个高频职业的叙事素材。',
            '掌握' + q('职业 + 道德困境') + '的典型公式。',
        ],
        key_questions=[
            '为什么医生与警察是艺考最常见的职业选择?',
        ])
    section_heading(flow, '18.1', '医生职业(Profession: Doctor)')
    render_kb_section(flow, 'story-elements/profession-doctor.md', exclude={'TL;DR'})
    section_heading(flow, '18.2', '警察职业(Profession: Police)')
    render_kb_section(flow, 'story-elements/profession-police.md', exclude={'TL;DR'})

    chapter_summary(flow, [
        '医生与警察都属于' + q('职业自带道德困境') + '的人物——他们每天在做决定。',
        '职业叙事的核心是' + q('专业性 + 道德困境') + '的双重展示。',
    ])
    chapter_quiz(flow, [
        '简答:医生题材与警察题材在动机档位上分别属于哪一档?',
        '分析:以一部医疗题材或警匪题材电影为例,分析其道德困境的结构。',
        '练习:为一位' + q('偏远小镇医生') + '设计一个道德困境故事核。',
    ], hint='(答案提示见本章 18.1 / 18.2,以及第 26 章面试策略)')
    chapter_further(flow, [
        '本书第 15 章 人物素材库',
        '本书第 17 章 情感与关系',
    ])


def ch19(flow):
    part = 'Part V 专题案例'
    chapter_heading(flow, 19, '《霸王别姬》忠诚的五重光谱', part)
    chapter_objectives(flow,
        goals=[
            '理解《霸王别姬》作为' + q('伙伴之情 + 被制度化') + '混合类型的经典性。',
            '分析影片中的忠诚概念如何被拆成五层表达。',
            '掌握影片中视听语言(戏台、色彩、京剧音乐)的主题功能。',
        ],
        key_questions=[
            '程蝶衣的' + q('不疯魔不成活') + '是疯癫还是忠诚?',
            '影片如何用' + q('戏台内/外') + '的对比完成政治寓言?',
        ])
    narrative_intro(flow,
        '《霸王别姬》(陈凯歌,1993)常被称作' + q('中国电影的最高峰') + '之一,但它的结构价值往往被其史诗气质遮蔽。从类型叙事看,它是' + q('伙伴之情') + '与' + q('被制度化') + '的混血;从反差三层看,它同时运转人物、情节、场面三层张力;从主题表达六法看,它几乎用了全部六种手段。本章对影片做完整拆解。')
    render_kb_section(flow, 'case-studies/bawang-bieji.md', exclude={'TL;DR'})
    chapter_summary(flow, [
        '《霸王别姬》是伙伴之情与被制度化的经典混血。',
        '影片用' + q('戏台内/外') + '的对比完成了从个人情感到时代政治的主题升迁。',
        '忠诚在影片中被展开为五层:对艺术、对师父、对戏中人、对爱人、对自我。',
    ])
    chapter_quiz(flow, [
        '简答:《霸王别姬》属于 Snyder 哪两种类型的混血?各占多少比重?',
        '分析:用反差三层分析影片中' + q('戏台内外') + '的一个镜头。',
        '简答:程蝶衣的' + q('不疯魔不成活') + '如何体现人物张力中的' + q('自我 vs 非我') + '?',
        '简答:影片如何用道具(宝剑)完成主题表达的第六法(意向传达)?',
        '练习:选一场对白戏,分析六种台词技巧中出现的三种以上。',
    ], hint='(答案提示见本章,以及第 1.5 节主题表达六法)')
    chapter_further(flow, [
        '本书第 1 章 主题表达六法',
        '本书第 14 章 东西方故事价值标准',
    ])


def ch20(flow):
    part = 'Part V 专题案例'
    chapter_heading(flow, 20, '《百元之恋》缺点驱动型弧光', part)
    chapter_objectives(flow,
        goals=[
            '完整拆解《百元之恋》的' + q('缺点→困境→欲望→目标') + '弧光链条。',
            '理解女主' + q('拳赛未赢但打完') + '为何仍算正向弧光。',
        ],
        key_questions=[
            '为什么结尾的' + q('输了但打完了') + '比' + q('赢了') + '更有力?',
        ])
    render_kb_section(flow, 'case-studies/baiyuan-zhi-lian.md', exclude={'TL;DR'})
    chapter_summary(flow, [
        '《百元之恋》是' + q('缺点驱动型弧光') + '的教科书案例。',
        '结尾的' + q('输了但打完了') + '证明了' + q('目标可以未达,但缺点必须修正') + '的弧光定律。',
    ])
    chapter_quiz(flow, [
        '简答:女主的缺点是什么?这个缺点如何阻碍目标的达成?',
        '分析:拆解影片中' + q('第一次想走→留下→报名拳赛') + '的转折。',
        '简答:配角(拳击手、店长)如何' + q('参与') + '主角弧光?',
        '练习:以影片为模板,把' + q('缺点→困境→欲望→目标') + '链条重写为一个艺考故事。',
    ], hint='(答案提示见本章,以及第 2.4 节人物弧光)')
    chapter_further(flow, [
        '本书第 2 章 人物的构建',
    ])


def ch21(flow):
    part = 'Part V 专题案例'
    chapter_heading(flow, 21, '《消失的爱人》双视角叙事', part)
    chapter_objectives(flow,
        goals=[
            '理解双视角叙事的结构优势与风险。',
            '分析影片如何利用信息错位冲突驱动悬念。',
        ],
        key_questions=[
            '双视角叙事是否必然优于单视角?它的代价是什么?',
        ])
    render_kb_section(flow, 'case-studies/xiaoshi-de-airen.md', exclude={'TL;DR'})
    chapter_summary(flow, [
        '双视角叙事的核心是信息错位冲突的系统化运用。',
        '视角切换必须精确——过早切换破坏悬念,过晚切换让观众失去共情。',
    ])
    chapter_quiz(flow, [
        '简答:双视角叙事与单视角叙事各自的结构优势是什么?',
        '分析:影片的中点切换发生在什么位置?它如何改变观众对主角的判断?',
        '简答:双视角叙事的最大风险是什么?',
        '练习:为一个' + q('夫妻离婚') + '的故事核设计双视角叙事的切换位置。',
    ], hint='(答案提示见本章,以及第 1.3 节冲突六类信息错位)')
    chapter_further(flow, [
        '本书第 1 章 冲突六大类型',
        '本书第 13.5 节 惊悚片要素',
    ])


def ch22(flow):
    part = 'Part VI 艺考实战'
    chapter_heading(flow, 22, '五事件大纲法', part)
    chapter_objectives(flow,
        goals=[
            '掌握' + q('五事件') + '结构——开场、发展 1、发展 2、危机、结局——的字数比例与职能。',
            '能够在 20 分钟内用五事件法构思一个 2000 字的故事。',
        ],
        key_questions=[
            '五事件与十五节拍的对应关系是什么?',
        ])
    narrative_intro(flow,
        '五事件大纲法是艺考编讲故事最实用的落地工具。它把 2000 字均匀切成五段——每段 400 字——并为每一段分配明确的节拍任务。它是三幕剧与十五节拍表在艺考语境下的' + q('压缩版') + '。')
    render_kb_section(flow, 'director-notes/five-event-outline.md', exclude={'TL;DR'})
    chapter_summary(flow, [
        '五事件 = 开场、发展 1、发展 2、危机、结局,每段约 400 字。',
        '它是三幕剧与十五节拍的艺考压缩版——开场对应铺垫+催化剂,危机对应一无所有+灵魂黑夜。',
        '使用它最忌' + q('均分字数却没有节拍推进') + '——五段必须有情感曲线的起伏。',
    ])
    chapter_quiz(flow, [
        '简答:五事件各自对应十五节拍中的哪些节拍?',
        '练习:以' + q('最后一次见面') + '为题,用五事件大纲法写出每段的核心情节。',
        '简答:危机事件(第四事件)为何是五事件中最重的一段?',
        '简答:五事件法与' + q('五幕剧') + '有什么区别?',
    ], hint='(答案提示见本章,以及第 1.2 节十五节拍)')
    chapter_further(flow, [
        '本书第 23 章 反差发动机法',
        '本书第 24 章 道具生场景法',
    ])


def ch23(flow):
    part = 'Part VI 艺考实战'
    chapter_heading(flow, 23, '反差发动机法', part)
    chapter_objectives(flow,
        goals=[
            '掌握用反差推动故事前进的具体写作流程。',
            '能够快速为一个题目生成三种不同反差方案。',
        ],
        key_questions=[
            '反差发动机与' + q('离水之鱼') + '是同一个东西吗?',
        ])
    render_kb_section(flow, 'director-notes/contrast-engine-method.md', exclude={'TL;DR'})
    chapter_summary(flow, [
        '反差发动机法把反差三层显式地' + q('点燃') + '——让每一层张力都承担推进功能。',
        '它与' + q('离水之鱼') + '互补:离水之鱼解决起点反差,反差发动机解决持续反差。',
    ])
    chapter_quiz(flow, [
        '简答:反差发动机与' + q('离水之鱼') + '的区别是什么?',
        '练习:为' + q('一个内向的主角被迫上台演讲') + '构思三种不同强度的反差。',
        '简答:如何判断反差' + q('过大变成荒诞') + '?',
    ], hint='(答案提示见本章,以及第 1.4 节故事核与人物反差)')
    chapter_further(flow, [
        '本书第 1 章 故事核与反差',
        '本书第 3 章 反差三层',
    ])


def ch24(flow):
    part = 'Part VI 艺考实战'
    chapter_heading(flow, 24, '道具生场景法', part)
    chapter_objectives(flow,
        goals=[
            '掌握从一件道具反推场景与情节的创作流程。',
            '跟随' + q('火柴') + '完整例,理解一件道具如何支撑整部故事。',
        ],
        key_questions=[
            '为什么' + q('道具先行') + '比' + q('人物先行') + '更适合考场 20 分钟?',
        ])
    render_kb_section(flow, 'director-notes/prop-to-scene-method.md', exclude={'TL;DR'})
    chapter_summary(flow, [
        '道具生场景法从具体物件反推空间、情感、冲突——更适合考场紧迫时间。',
        q('火柴') + '的完整例显示一件小物如何通过三次出现支撑完整故事。',
    ])
    chapter_quiz(flow, [
        '简答:道具生场景法的四个步骤是什么?',
        '练习:选一件常见物件(手帕、水杯、钥匙),写出它在三个场景中的不同功能。',
        '简答:道具的' + q('三次出现') + '原则如何与情感曲线同步?',
        '分析:用道具生场景法为题目' + q('秋天') + '设计故事核。',
    ], hint='(答案提示见本章,以及第 12.2 节道具象征)')
    chapter_further(flow, [
        '本书第 12 章 符号与意象',
        '本书第 16 章 道具素材库',
    ])


def ch25(flow):
    part = 'Part VI 艺考实战'
    chapter_heading(flow, 25, '分镜头工作流', part)
    chapter_objectives(flow,
        goals=[
            '掌握分镜头脚本的基本字段(景别/角度/运动/时长/内容/音效)。',
            '理解 Animatic(预演动画)的功能与简易制作方法。',
        ],
        key_questions=[
            '分镜头是' + q('剧本的翻译') + '还是' + q('导演的重写') + '?',
        ])
    render_kb_section(flow, 'director-notes/storyboard-workflow.md', exclude={'TL;DR'})
    chapter_summary(flow, [
        '分镜头脚本是剧本到视听语言的翻译层,其字段规范是入门必修。',
        'Animatic 是分镜头的动态预演,可以提前发现节奏问题。',
    ])
    chapter_quiz(flow, [
        '简答:分镜头脚本的标准字段包括哪些?',
        '练习:为一段 30 秒的冲突戏画 8 个分镜头,标注景别、角度、时长、内容。',
        '简答:Animatic 与分镜头静态稿的差异是什么?',
    ], hint='(答案提示见本章,以及 Part II 视听语言)')
    chapter_further(flow, [
        '本书第 4-9 章 视听语言各章',
    ])


def ch26(flow):
    part = 'Part VI 艺考实战'
    chapter_heading(flow, 26, '艺考面试策略', part)
    chapter_objectives(flow,
        goals=[
            '掌握面试常见问题的应答框架。',
            '建立' + q('看片储备→理论储备→思辨储备') + '三层应答体系。',
        ],
        key_questions=[
            '面试老师真正想听什么?',
        ])
    render_kb_section(flow, 'director-notes/exam-interview-strategy.md', exclude={'TL;DR'})
    chapter_summary(flow, [
        '面试的核心不是' + q('答得全') + ',而是' + q('答得真') + '——老师要判断你是不是爱看电影。',
        '看片 + 理论 + 思辨三层储备是稳定应答的基础。',
    ])
    chapter_quiz(flow, [
        '简答:面试常见的五类问题分别是什么?',
        '练习:为' + q('请谈一部让你震撼的电影') + '设计你的应答版本。',
        '简答:如何在面试中避免' + q('堆术语') + '的陷阱?',
        '分析:面试中如果碰到你没看过的电影被问到,应该如何得体回答?',
    ], hint='(答案提示见本章,以及附录 B)')
    chapter_further(flow, [
        '附录 B 世界经典电影摄影风格速查',
        '附录 C 影片案例索引',
    ])


def ch27(flow):
    part = 'Part VI 艺考实战'
    chapter_heading(flow, 27, '影片分析方法论', part)
    chapter_objectives(flow,
        goals=[
            '掌握' + q('两遍观影法') + '——第一遍体验,第二遍分析。',
            '熟悉四维分析框架:叙事/视听/主题/类型。',
            '获得剧本格式速查表。',
        ],
        key_questions=[
            '分析一部电影是否必须' + q('讲得出每一个镜头') + '?',
        ])
    render_kb_section(flow, 'theory/film-analysis-method.md', exclude={'TL;DR'})
    chapter_summary(flow, [
        '两遍观影法把' + q('体验') + '与' + q('分析') + '分开,避免在第一遍就被结构分析撕碎情感。',
        '四维分析框架(叙事 / 视听 / 主题 / 类型)是一份完整影评的骨架。',
        '剧本格式速查让你在考场上快速写出可读的剧本片段。',
    ])
    chapter_quiz(flow, [
        '简答:两遍观影法的分工是什么?',
        '练习:用四维框架分析一部你最近看过的电影,每一维写 100 字。',
        '简答:剧本格式中' + q('场景标题') + '(scene heading)应当如何书写?',
        '分析:影评写作中' + q('主题') + '与' + q('类型') + '两维是否可以合并?',
    ], hint='(答案提示见本章,以及 Part V 案例研究)')
    chapter_further(flow, [
        '本书第 19-21 章 专题案例研究',
    ])


def app_a(flow):
    part = '附录'
    chapter_heading(flow, 'A', '术语表(完整中英对照)', part)
    narrative_intro(flow,
        '本附录收录全书涉及的所有专业术语,采用中文-英文原文-简要释义三列制。它同时是复习检索工具与面试备考清单。')
    render_kb_section(flow, 'index/term-glossary.md', exclude={'TL;DR'}, skip_common=True)


def app_b(flow):
    part = '附录'
    chapter_heading(flow, 'B', '世界经典电影摄影风格速查', part)
    narrative_intro(flow,
        '本附录汇总 67 部经典电影与多部代表性动画长片的摄影风格标记,每一条均记录了导演、摄影指导、代表镜头、色彩策略与影响。它是面试的快速应答库——被问到一部电影时可以立即调取。')
    render_kb_section(flow, 'index/world-cinema-reference.md', exclude={'TL;DR'}, skip_common=True)


def app_c(flow):
    part = '附录'
    chapter_heading(flow, 'C', '影片案例索引', part)
    narrative_intro(flow,
        '本附录按影片名索引全书提及的所有案例,方便反向检索——如果你想知道《迷魂记》在本书哪几章被讨论,查本附录即可。')
    render_kb_section(flow, 'index/film-case-index.md', exclude={'TL;DR'}, skip_common=True)


def app_d(flow):
    part = '附录'
    chapter_heading(flow, 'D', '版本演进与 Ω 审计报告', part)
    narrative_intro(flow,
        '本附录记录本知识库的版本演进历程,以及 2026-04 做的一次完整 Omega 审计——按原子化、可链接、可演化三原则对全部 56 篇笔记做了审查,给出改进建议与变更记录。')
    render_kb_section(flow, 'index/omega-v1-audit.md', exclude={'TL;DR'}, skip_common=True)

    flow.append(Paragraph('本教材 Changelog', STY_H3))
    rows = [
        ['版本', '日期', '变更'],
        ['v1.3', '2026-04-21', '从 31 页目录式摘要升级为 150+ 页完整教科书;所有 56 篇知识库笔记被重写为论述;新增序言、章末小结、自测、延伸阅读结构'],
        ['v1.2', '2026-04-08', '新增分镜/画幅/构图/世界电影参考 8 篇扩展笔记'],
        ['v1.1', '2026-04-07', '全库 wiki-link 替换为标准 Markdown 相对链接'],
        ['v1.0', '2026-04-06', '基于《故事元素积累6_merged.pdf》建立 48 篇初始笔记'],
    ]
    flow.append(make_table(rows))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build():
    t_start = time.time()
    frame = Frame(
        2 * cm, 1.7 * cm,
        A4[0] - 4 * cm, A4[1] - 3.4 * cm,
        id='normal', leftPadding=0, bottomPadding=0,
        rightPadding=0, topPadding=0,
    )
    page_tpl = PageTemplate(id='pages', frames=[frame], onPage=draw_page)

    doc = DocWithTOC(
        OUTPUT, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.7 * cm, bottomMargin=1.7 * cm,
        title='PKTFILM 电影学教程', author='P0ckket',
    )
    doc.addPageTemplates([page_tpl])

    story = []
    set_running('', '')
    # Reset running-header state at layout time as well, so multiBuild's
    # second pass doesn't inherit the final chapter's label on cover/preface/TOC.
    story.append(RunningHeader('', ''))
    build_cover(story)
    build_preface(story)
    build_toc(story)

    part_cover(story, 'I', '叙事基础', 'Narrative Foundations',
        '故事不是事件的堆叠,是有开合呼应的结构。本部分从三幕剧到十五节拍,从冲突到反差,从主题六法到类型总览,为全书搭建叙事词汇表。')
    ch1(story); ch2(story); ch3(story)

    part_cover(story, 'II', '视听语言', 'Cinematic Language',
        '从叙事的文字骨架进入电影的视听肉身。本部分按八大类——场面调度、景别、角度、运动、光线、画幅构图、声音、对白、符号——逐章展开。')
    ch4(story); ch5(story); ch6(story); ch7(story); ch8(story)
    ch9(story); ch10(story); ch11(story); ch12(story)

    part_cover(story, 'III', '类型叙事', 'Genre',
        '类型不是市场标签,是困境结构。本部分展开 Snyder 十分类中本库收录的五类,并以方法论辨析章完成对立理论的比较。')
    ch13(story); ch14(story)

    part_cover(story, 'IV', '故事元素素材库', 'Story Elements Library',
        '素材库是可调用的原子池。本部分以扁平化方式保留人物、道具、场景、情感、职业的素材清单,遵循先立故事核再调素材的使用原则。')
    ch15(story); ch16(story); ch17(story); ch18(story)

    part_cover(story, 'V', '专题案例研究', 'Case Studies',
        '理论的用处在于被具体作品激活。本部分对三部作品——《霸王别姬》《百元之恋》《消失的爱人》——做完整拆解,示范本书所有理论如何在实际作品中咬合。')
    ch19(story); ch20(story); ch21(story)

    part_cover(story, 'VI', '艺考实战操作', 'Exam Practice',
        '所有理论最终都要在考场上落地。本部分给出六条可直接执行的工作流:五事件大纲、反差发动机、道具生场景、分镜头工作流、面试策略、影片分析方法。')
    ch22(story); ch23(story); ch24(story); ch25(story); ch26(story); ch27(story)

    part_cover(story, 'App', '附录', 'Appendices',
        '术语表、世界电影速查、案例索引与版本演进审计——长期检索与面试备考的必备工具。')
    app_a(story); app_b(story); app_c(story); app_d(story)

    story.append(PageBreak())
    story.append(Spacer(1, 200))
    end_style = ParagraphStyle('end', parent=STY_COVER_META, fontSize=14,
                               textColor=colors.HexColor('#0b2545'))
    story.append(Paragraph('—— PKTFILM 电影学教程 v1.3 终 ——', end_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph('感谢陪伴。下一版将在 v1.4 中补全 Snyder 剩余 5 类与更多案例。', STY_COVER_META))

    print(f'[build] multiBuild flowables={len(story)}')
    doc.multiBuild(story)
    elapsed = time.time() - t_start

    try:
        from pypdf import PdfReader
        reader = PdfReader(OUTPUT)
        pages = len(reader.pages)
    except Exception as e:
        pages = -1
        print(f'[warn] pypdf read failed: {e}')

    size = os.path.getsize(OUTPUT)
    print(f'[done] {OUTPUT}')
    print(f'  pages: {pages}')
    print(f'  size:  {size/1024:.1f} KB ({size/1024/1024:.2f} MB)')
    print(f'  time:  {elapsed:.1f}s')
    return pages, size, elapsed


if __name__ == '__main__':
    build()
