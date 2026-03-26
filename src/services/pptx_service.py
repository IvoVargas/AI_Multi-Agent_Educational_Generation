from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


PRIMARY = RGBColor(33, 37, 41)
ACCENT = RGBColor(52, 120, 246)
MUTED = RGBColor(108, 117, 125)
LIGHT_BG = RGBColor(245, 247, 250)
WHITE = RGBColor(255, 255, 255)

# 4:3
SLIDE_WIDTH_IN = 10.0
SLIDE_HEIGHT_IN = 7.5


def _set_slide_background(slide) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = WHITE


def _add_top_bar(slide) -> None:
    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(0),
        Inches(0),
        Inches(SLIDE_WIDTH_IN),
        Inches(0.28),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = ACCENT
    shape.line.fill.background()


def _add_footer(slide, text: str = "Gerado automaticamente pelo protótipo") -> None:
    textbox = slide.shapes.add_textbox(
        Inches(0.35),
        Inches(7.02),
        Inches(9.2),
        Inches(0.22),
    )
    tf = textbox.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(9)
    p.font.color.rgb = MUTED
    p.alignment = PP_ALIGN.RIGHT


def _add_textbox(slide, left, top, width, height, text=""):
    textbox = slide.shapes.add_textbox(left, top, width, height)
    textbox.text_frame.text = text
    return textbox


def _add_title_text(slide, title: str, size: int = 24) -> None:
    textbox = _add_textbox(
        slide,
        Inches(0.6),
        Inches(0.55),
        Inches(8.7),
        Inches(0.7),
        title,
    )
    p = textbox.text_frame.paragraphs[0]
    p.font.size = Pt(size)
    p.font.bold = True
    p.font.color.rgb = PRIMARY


def _add_subtitle_text(slide, subtitle: str) -> None:
    textbox = _add_textbox(
        slide,
        Inches(0.75),
        Inches(2.2),
        Inches(8.4),
        Inches(0.8),
        subtitle,
    )
    p = textbox.text_frame.paragraphs[0]
    p.font.size = Pt(20)
    p.font.color.rgb = MUTED
    p.alignment = PP_ALIGN.CENTER


def _add_title_visual_block(slide, visual_description: str) -> None:
    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
        Inches(1.2),
        Inches(3.1),
        Inches(7.6),
        Inches(2.3),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = LIGHT_BG
    shape.line.color.rgb = ACCENT

    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True

    p1 = tf.paragraphs[0]
    p1.text = "Sugestão visual de capa"
    p1.font.size = Pt(16)
    p1.font.bold = True
    p1.font.color.rgb = ACCENT
    p1.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = visual_description or "Imagem de capa relacionada com o tema da apresentação."
    p2.font.size = Pt(13)
    p2.font.color.rgb = PRIMARY
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(10)


def _add_body_box(slide) -> Any:
    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
        Inches(0.55),
        Inches(1.45),
        Inches(5.55),
        Inches(5.2),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = WHITE
    shape.line.color.rgb = RGBColor(220, 225, 230)
    return shape


def _add_visual_box(slide, visual_description: str) -> None:
    box = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
        Inches(6.35),
        Inches(1.45),
        Inches(3.1),
        Inches(5.2),
    )
    box.fill.solid()
    box.fill.fore_color.rgb = LIGHT_BG
    box.line.color.rgb = ACCENT

    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True

    p1 = tf.paragraphs[0]
    p1.text = "Apoio visual"
    p1.font.bold = True
    p1.font.size = Pt(15)
    p1.font.color.rgb = ACCENT
    p1.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = visual_description or "Sugestão visual não disponível."
    p2.font.size = Pt(12)
    p2.font.color.rgb = PRIMARY
    p2.space_before = Pt(10)


def _add_bullets(slide, bullets: List[str]) -> None:
    textbox = _add_textbox(
        slide,
        Inches(0.8),
        Inches(1.8),
        Inches(4.95),
        Inches(4.45),
        "",
    )

    tf = textbox.text_frame
    tf.clear()
    tf.word_wrap = True

    for idx, bullet in enumerate(bullets[:6]):
        if idx == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = bullet
        p.font.size = Pt(18)
        p.font.color.rgb = PRIMARY
        p.level = 0
        p.space_after = Pt(8)


def _add_section_label(slide, text: str) -> None:
    textbox = _add_textbox(
        slide,
        Inches(0.65),
        Inches(1.28),
        Inches(2.2),
        Inches(0.25),
        text,
    )
    p = textbox.text_frame.paragraphs[0]
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT


def _build_title_slide(slide, item: Dict[str, Any], metadata: Dict[str, Any]) -> None:
    _set_slide_background(slide)
    _add_top_bar(slide)

    _add_title_text(slide, item.get("title", "Apresentação"), size=28)
    _add_subtitle_text(
        slide,
        metadata.get("presentation_goal", "") or "Apresentação educativa",
    )
    _add_title_visual_block(slide, item.get("visual_description", ""))

    audience = metadata.get("target_audience", "").strip()
    level = metadata.get("education_level", "").strip()
    info = " | ".join(x for x in [audience, level] if x)

    if info:
        info_box = _add_textbox(
            slide,
            Inches(0.9),
            Inches(6.0),
            Inches(8.2),
            Inches(0.3),
            info,
        )
        p = info_box.text_frame.paragraphs[0]
        p.font.size = Pt(11)
        p.font.color.rgb = MUTED
        p.alignment = PP_ALIGN.CENTER

    _add_footer(slide)


def _build_content_slide(slide, item: Dict[str, Any]) -> None:
    _set_slide_background(slide)
    _add_top_bar(slide)

    _add_title_text(slide, item.get("title", "Slide"), size=23)
    _add_body_box(slide)
    _add_bullets(slide, item.get("bullets", []) or ["Conteúdo não disponível"])
    _add_visual_box(slide, item.get("visual_description", ""))

    _add_footer(slide)


def build_presentation(
    slide_plan: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    output_path: str,
) -> str:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    prs = Presentation()
    prs.slide_width = Inches(SLIDE_WIDTH_IN)
    prs.slide_height = Inches(SLIDE_HEIGHT_IN)

    blank_layout = prs.slide_layouts[6]

    for item in slide_plan:
        slide = prs.slides.add_slide(blank_layout)
        kind = item.get("kind", "content")

        if kind == "title":
            _build_title_slide(slide, item, metadata)
        else:
            _build_content_slide(slide, item)

    prs.save(str(output_file))
    return str(output_file)