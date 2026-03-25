from __future__ import annotations

from typing import Any, Dict, List


def _build_slide_plan(slide_sequence: List[Dict[str, Any]], theme: str) -> List[Dict[str, Any]]:
    slide_plan: List[Dict[str, Any]] = []

    for slide in slide_sequence:
        title = slide.get("title", "Slide")
        content_points = slide.get("content_points", [])

        slide_plan.append(
            {
                "slide_number": slide.get("slide_number"),
                "title": title,
                "bullets": content_points or [
                    "Ponto principal 1",
                    "Ponto principal 2",
                    "Ponto principal 3",
                ],
                "speaker_notes": f"Explicar {title.lower()} de forma adequada ao público-alvo.",
                "visual_description": f"Imagem ou ilustração educativa relacionada com {title.lower()} e com o tema {theme}.",
                "image_prompt": f"Educational slide illustration about {title} in the context of {theme}, clean presentation style",
                "image_path": None,
            }
        )

    return slide_plan


def run_multimedia_generator(state: dict) -> dict:
    pedagogical_structure = state.get("pedagogical_structure", {})
    metadata = state.get("metadata", {})

    theme = pedagogical_structure.get(
        "presentation_title",
        metadata.get("title", "Tema"),
    )
    slide_sequence = pedagogical_structure.get("slide_sequence", [])

    slide_plan = _build_slide_plan(slide_sequence, theme)

    return {
        "slide_plan": slide_plan,
        "current_step": "multimedia_generation",
        "status": "slides_completed",
    }