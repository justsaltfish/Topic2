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
PREAMBLE = """# 160 bp 增强子生成：计算部分核验稿

版本日期：2026-10-07。正文已依据既有序列、逐样本预测、代码和日志核验更新。最终模型、阈值及投稿期刊仍待作者确认；历史记录冲突及统计限制另列核对清单。
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
    doc.core_properties.title = "160 bp 增强子生成：计算部分核验稿"
    doc.core_properties.author = ""
    doc.core_properties.subject = "Verified archive analysis; author decisions pending"
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
        image_name = None
        if level == 2 and content.startswith("Results 2."):
            image_name = "figure1_sequence_quality.png"
        elif level == 2 and content == "Computational Methods":
            image_name = "figure2_guided_generation.png"
        if image_name:
            figure = ROOT / "figures/results" / image_name
            if figure.is_file():
                picture = doc.add_paragraph()
                picture.paragraph_format.first_line_indent = Pt(0)
                picture.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                picture.paragraph_format.page_break_before = True
                picture.add_run().add_picture(str(figure), width=Cm(16))
        if level:
            paragraph = doc.add_heading(content, level=min(level, 3))
            if image_name:
                paragraph.paragraph_format.page_break_before = True
        else:
            paragraph = doc.add_paragraph(content)
            if content.startswith("版本日期："):
                paragraph.paragraph_format.first_line_indent = Pt(0)
                paragraph.paragraph_format.space_after = Pt(12)
                for run in paragraph.runs:
                    run.font.size = Pt(10.5)
            elif re.match(r"^\[\d+\]", content):
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
    footer.paragraph_format.first_line_indent = Pt(0)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)
    doc.save(target / "computational_sections_zh.docx")
    print("Exported synchronized Markdown and DOCX working drafts")


if __name__ == "__main__":
    export()
