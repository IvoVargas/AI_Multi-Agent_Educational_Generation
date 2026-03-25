from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from pptx import Presentation


def build_presentation(
    slide_plan: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    output_path: str,
) -> str:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    prs = Presentation()

    # Slide de título
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    slide.shapes.title.text = metadata.get("title", "") or "Apresentação Gerada"
    subtitle = slide.placeholders[1]
    subtitle.text = metadata.get("presentation_goal", "") or "Protótipo multiagente"

    # Slides de conteúdo
    content_layout = prs.slide_layouts[1]
    for item in slide_plan:
        content_slide = prs.slides.add_slide(content_layout)
        content_slide.shapes.title.text = item.get("title", "Slide")

        body = content_slide.placeholders[1].text_frame
        body.clear()

        bullets = item.get("bullets", [])
        if not bullets:
            bullets = ["Conteúdo não disponível"]

        for idx, bullet in enumerate(bullets):
            if idx == 0:
                body.text = bullet
            else:
                p = body.add_paragraph()
                p.text = bullet

    # Slide final
    final_slide = prs.slides.add_slide(content_layout)
    final_slide.shapes.title.text = "Conclusão"
    final_body = final_slide.placeholders[1].text_frame
    final_body.text = "Síntese dos principais pontos apresentados."
    p = final_body.add_paragraph()
    p.text = "Material gerado automaticamente pelo protótipo."

    prs.save(str(output_file))
    return str(output_file)