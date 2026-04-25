from __future__ import annotations

from typing import Dict

from src.agents.file_intake import grounding_context_for_state
from src.models import PedagogicalStructureModel
from src.services.llm_service import LLMService
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)
llm = LLMService()


def _fallback_structure(state: dict, source_names: list[str]) -> Dict:
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
        "source_documents": source_names,
    }


def run_pedagogical_designer(state: dict) -> dict:
    logger.info("Pedagogical designer started")
    metadata = state.get("metadata", {})
    content_analysis = state.get("content_analysis", {})
    feedback = state.get("structure_feedback", "").strip()
    query = " ".join(
        str(part)
        for part in [content_analysis.get("theme", ""), " ".join(content_analysis.get("main_topics", [])), feedback]
        if str(part).strip()
    )
    grounding_context, source_names = grounding_context_for_state(state, query=query, top_n=5)

    system_prompt = """
És um Designer Pedagógico para um sistema de geração de apresentações educativas.
Usa a análise conceptual como guia principal e os documentos anexados apenas como suporte factual e de estrutura.
Responde apenas com JSON válido.

Estrutura obrigatória:
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
"""

    user_prompt = f"""
Análise conceptual:
{content_analysis}

Metadados:
{metadata}

Fontes de apoio:
{grounding_context or 'Sem fontes adicionais.'}

Feedback anterior:
{feedback if feedback else 'Sem feedback anterior.'}
"""

    try:
        pedagogical_structure = llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=PedagogicalStructureModel,
        )
        pedagogical_structure["source_documents"] = source_names
    except Exception:
        logger.exception("Pedagogical designer failed. Using fallback.")
        pedagogical_structure = _fallback_structure(state, source_names)

    logger.info("Pedagogical designer completed")
    return {
        "pedagogical_structure": pedagogical_structure,
        "structure_approved": False,
        "slide_plan": [],
        "presentation_path": "",
        "current_step": "pedagogical_design",
        "status": "structure_completed",
        "error_message": "",
    }
