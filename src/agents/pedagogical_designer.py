from __future__ import annotations

from typing import Any, Dict, List


def _build_slide_sequence(
    theme: str,
    main_topics: List[str],
    num_slides: int,
) -> List[Dict[str, Any]]:
    sequence: List[Dict[str, Any]] = []

    topics = main_topics[: max(1, num_slides - 2)]
    if not topics:
        topics = ["introdução", "desenvolvimento", "síntese"]

    for index, topic in enumerate(topics, start=1):
        sequence.append(
            {
                "slide_number": index,
                "title": f"{topic.capitalize()}",
                "objective": f"Apresentar {topic} no contexto de {theme}",
                "content_points": [
                    f"Explicação principal sobre {topic}",
                    f"Relação de {topic} com o tema",
                    f"Exemplo ou observação relevante",
                ],
            }
        )

    return sequence


def run_pedagogical_designer(state: dict) -> dict:
    metadata = state.get("metadata", {})
    content_analysis = state.get("content_analysis", {})

    theme = content_analysis.get("theme", metadata.get("title", "Tema"))
    main_topics = content_analysis.get("main_topics", [])
    num_slides = int(metadata.get("num_slides", 6))

    slide_sequence = _build_slide_sequence(theme, main_topics, num_slides)

    pedagogical_structure = {
        "presentation_title": metadata.get("title", "").strip() or f"Introdução a {theme}",
        "learning_objectives": [
            f"Compreender os aspetos centrais de {theme}",
            f"Identificar aplicações, exemplos ou limitações de {theme}",
        ],
        "sections": [
            {
                "section_title": "Introdução",
                "goal": "Apresentar o tema e o seu contexto",
                "topics": main_topics[:2] or ["conceitos fundamentais"],
            },
            {
                "section_title": "Desenvolvimento",
                "goal": "Explorar os tópicos principais",
                "topics": main_topics[2:4] or ["explicação do conteúdo"],
            },
            {
                "section_title": "Síntese",
                "goal": "Consolidar as ideias principais",
                "topics": main_topics[4:] or ["conclusões"],
            },
        ],
        "slide_sequence": slide_sequence,
    }

    return {
        "pedagogical_structure": pedagogical_structure,
        "current_step": "pedagogical_design",
        "status": "structure_completed",
    }