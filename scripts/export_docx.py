#!/usr/bin/env python3
"""Export the computational working draft from its Markdown source files."""
from pathlib import Path
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
PARTS = (
    "chapters/01_results_sequence_quality.md",
    "chapters/02_results_guided_generation.md",
    "chapters/03_methods_computational.md",
    "chapters/04_figure_legends.md",
    "references/method-references.md",
)
PREAMBLE = """# 160 bp 增强子生成：计算部分工作稿

版本日期：2026-10-07。状态：按投稿结构组织的工作稿，尚不能直接投稿。本文档仅覆盖用户确认的计算部分；原始结果、最终模型和图件未核实，待核实项须在投稿前清零。当前采用通用排版，目标期刊尚未指定。
"""


def merged_text():
    return PREAMBLE.rstrip() + "\n\n" + "\n\n".join(
        (ROOT / name).read_text(encoding="utf-8").strip() for name in PARTS
    ) + "\n"


def paragraphs(text):
    for block in re.split(r"\n\s*\n", text.strip()):
        match = re.match(r"^(#{1,6})\s+(.+)$", block, re.DOTALL)
        if match:
            yield len(match.group(1)), match.group(2).strip()
        else:
            yield 0, block.replace("\n", " ").strip()


def set_font(style, east_asia, size, bold=False):
    style.font.name = "Times New Roman"
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = RGBColor(0, 0, 0)
    props = style.element.get_or_add_rPr()
    for node in (props.rFonts, props.find(qn("w:color"))):
        if node is not None:
            for attribute in list(node.attrib):
                if "theme" in attribute.lower():
                    del node.attrib[attribute]
    props.rFonts.set(qn("w:eastAsia"), east_asia)
    props.rFonts.set(qn("w:cs"), "Times New Roman")


def export():
    text = merged_text()
    target = ROOT / "manuscript"
    target.mkdir(exist_ok=True)
    (target / "computational_sections_zh.md").write_text(text, encoding="utf-8")
    doc = Document()
    doc.core_properties.title = "160 bp 增强子生成：计算部分工作稿"
    doc.core_properties.author = ""
    doc.core_properties.subject = "Working draft; not submission ready"
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2.5)
    section.left_margin = section.right_margin = Cm(2.5)
    normal = doc.styles["Normal"]
    set_font(normal, "宋体", 12)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.first_line_indent = Pt(24)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.widow_control = True
    for level, size in ((1, 18), (2, 14), (3, 12)):
        style = doc.styles[f"Heading {level}"]
        set_font(style, "黑体", size, bold=True)
        style.paragraph_format.first_line_indent = Pt(0)
        style.paragraph_format.line_spacing = 1.25
        style.paragraph_format.space_before = Pt(18 if level > 1 else 0)
        style.paragraph_format.space_after = Pt(8)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.alignment = (
            WD_ALIGN_PARAGRAPH.CENTER if level == 1 else WD_ALIGN_PARAGRAPH.LEFT
        )
    for level, content in paragraphs(text):
        if level:
            paragraph = doc.add_heading(content, level=min(level, 3))
        else:
            paragraph = doc.add_paragraph(content)
            if content.startswith("版本日期："):
                paragraph.paragraph_format.first_line_indent = Pt(0)
                paragraph.paragraph_format.space_after = Pt(12)
                for run in paragraph.runs:
                    run.font.size = Pt(10.5)
            elif content.startswith(("[1]", "[2]")):
                paragraph.paragraph_format.first_line_indent = Pt(0)
        # Explicit runs prevent Word theme fonts from overriding Chinese headings.
        for run in paragraph.runs:
            run.font.name = "Times New Roman"
            props = run._r.get_or_add_rPr()
            props.rFonts.set(qn("w:eastAsia"), "黑体" if level else "宋体")
            props.rFonts.set(qn("w:cs"), "Times New Roman")
            run.font.color.rgb = RGBColor(0, 0, 0)
    footer = section.footer.paragraphs[0]
    footer.alignment = 1
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)
    doc.save(target / "computational_sections_zh.docx")
    print("Exported synchronized Markdown and DOCX working drafts")


if __name__ == "__main__":
    export()
