from __future__ import annotations

from typing import Any, Dict

from src.services.llm_service import LLMService

llm = LLMService()


def _fallback_structure(state: dict) -> Dict[str, Any]:
    metadata = state.get("metadata", {})
    content_analysis = state.get("content_analysis", {})
    title = metadata.get("title", "").strip() or content_analysis.get("theme", "Apresentação")
    topics = content_analysis.get("main_topics", []) or ["introdução", "desenvolvimento", "síntese"]
    num_slides = int(metadata.get("num_slides", 6))

    slide_sequence = []
    for idx, topic in enumerate(topics[: max(1, num_slides - 2)], start=1):
        slide_sequence.append(
            {
                "slide_number": idx,
                "title": topic.capitalize(),
                "objective": f"Apresentar {topic}",
                "content_points": [
                    f"Definir {topic}",
                    f"Explicar a relevância de {topic}",
                    f"Dar um exemplo relacionado com {topic}",
                ],
            }
        )

    return {
        "presentation_title": title,
        "learning_objectives": [
            f"Compreender os aspetos principais de {title}",
            f"Relacionar conceitos e aplicações do tema",
        ],
        "sections": [
            {
                "section_title": "Introdução",
                "goal": "Apresentar o tema",
                "topics": topics[:2],
            },
            {
                "section_title": "Desenvolvimento",
                "goal": "Explorar os tópicos principais",
                "topics": topics[2:4],
            },
            {
                "section_title": "Síntese",
                "goal": "Consolidar as ideias principais",
                "topics": topics[4:],
            },
        ],
        "slide_sequence": slide_sequence,
    }


def run_pedagogical_designer(state: dict) -> dict:
    metadata = state.get("metadata", {})
    content_analysis = state.get("content_analysis", {})
    feedback = state.get("structure_feedback", "").strip()

    system_prompt = """
És um Designer Pedagógico para um sistema de geração de apresentações educativas.
Recebes uma análise conceptual e deves devolver apenas um objeto JSON válido.

Devolve exatamente esta estrutura:
{
  "presentation_title": "string",
  "learning_objectives": ["string"],
  "sections": [
    {
      "section_title": "string",
      "goal": "string",
      "topics": ["string"]
    }
  ],
  "slide_sequence": [
    {
      "slide_number": 1,
      "title": "string",
      "objective": "string",
      "content_points": ["string"]
    }
  ]
}

Regras:
- Escreve em português de Portugal.
- Não cries markdown.
- Não incluas texto fora do JSON.
- A estrutura deve ser adequada a uma apresentação educativa.
"""

    user_prompt = f"""
Análise conceptual:
{content_analysis}

Metadados:
{metadata}

Feedback de reformulação anterior:
{feedback if feedback else "Sem feedback anterior."}
"""

    try:
        pedagogical_structure = llm.generate_json(system_prompt, user_prompt)
    except Exception:
        pedagogical_structure = _fallback_structure(state)

    return {
        "pedagogical_structure": pedagogical_structure,
        "structure_approved": False,
        "slide_plan": [],
        "presentation_path": "",
        "current_step": "pedagogical_design",
        "status": "structure_completed",
        "error_message": "",
    }