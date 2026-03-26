from __future__ import annotations

from typing import Any, Dict, List


def run_multimedia_generator(state: dict) -> dict:
    pedagogical_structure = state.get("pedagogical_structure", {})
    metadata = state.get("metadata", {})
    title = pedagogical_structure.get("presentation_title", metadata.get("title", "Apresentação"))
    slide_sequence = pedagogical_structure.get("slide_sequence", [])

    slide_plan: List[Dict[str, Any]] = []

    # slide inicial
    slide_plan.append(
        {
            "slide_number": 0,
            "title": title,
            "bullets": [
                metadata.get("presentation_goal", "Apresentação educativa gerada pelo protótipo")
            ],
            "speaker_notes": "Apresentar o tema, o objetivo e o enquadramento da sessão.",
            "visual_description": f"Imagem de capa relacionada com {title}.",
            "image_prompt": f"Educational title slide cover about {title}, clean academic presentation style",
            "image_path": None,
            "kind": "title",
        }
    )

    for slide in slide_sequence:
        slide_plan.append(
            {
                "slide_number": slide.get("slide_number"),
                "title": slide.get("title", "Slide"),
                "bullets": slide.get("content_points", []),
                "speaker_notes": slide.get(
                    "objective",
                    "Explicar o conteúdo deste slide de forma clara e adequada ao público.",
                ),
                "visual_description": f"Elemento visual educativo relacionado com {slide.get('title', 'o tema do slide')}.",
                "image_prompt": f"Educational illustration for slide titled '{slide.get('title', 'Slide')}', clean presentation style",
                "image_path": None,
                "kind": "content",
            }
        )

    slide_plan.append(
        {
            "slide_number": len(slide_plan),
            "title": "Conclusão",
            "bullets": [
                "Síntese dos principais pontos abordados",
                "Reforço das ideias-chave da apresentação",
                "Possíveis extensões ou aplicações",
            ],
            "speaker_notes": "Fechar a apresentação com uma síntese breve e clara.",
            "visual_description": "Ícone ou ilustração simples de encerramento.",
            "image_prompt": "Minimal educational closing slide illustration, clean academic style",
            "image_path": None,
            "kind": "closing",
        }
    )

    return {
        "slide_plan": slide_plan,
        "current_step": "multimedia_generation",
        "status": "slides_completed",
        "error_message": "",
    }