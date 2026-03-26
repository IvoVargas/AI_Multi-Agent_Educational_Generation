from __future__ import annotations

from typing import Dict

from src.models import ContentAnalysisModel
from src.services.llm_service import LLMService
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)
llm = LLMService()


def _fallback_analysis(state: dict) -> Dict:
    user_input = state.get("user_input", "")
    metadata = state.get("metadata", {})
    title = metadata.get("title", "").strip() or "Tema não especificado"

    summary = user_input[:400].strip()
    if len(user_input) > 400:
        summary += "..."

    return {
        "theme": title,
        "summary": summary or "Resumo conceptual do texto-base.",
        "key_concepts": [
            "conceitos centrais do tema",
            "relações entre tópicos",
            "ideias principais do texto-base",
        ],
        "main_topics": [
            "introdução",
            "conceitos fundamentais",
            "aplicações",
            "vantagens e limitações",
            "síntese",
        ],
        "prerequisites": ["conhecimentos introdutórios relacionados com o tema"],
        "possible_difficulties": [
            "interpretação de conceitos mais abstratos",
            "distinção entre noções próximas",
        ],
    }


def run_content_analyst(state: dict) -> dict:
    logger.info("Content analyst started")
    user_input = state.get("user_input", "")
    metadata = state.get("metadata", {})
    feedback = state.get("analysis_feedback", "").strip()

    system_prompt = """
És um Analista de Conteúdo para um sistema de geração de apresentações educativas.
Responde apenas com JSON válido.

Estrutura obrigatória:
{
  "theme": "string",
  "summary": "string",
  "key_concepts": ["string"],
  "main_topics": ["string"],
  "prerequisites": ["string"],
  "possible_difficulties": ["string"]
}
"""

    user_prompt = f"""
Texto-base:
{user_input}

Metadados:
{metadata}

Feedback anterior:
{feedback if feedback else "Sem feedback anterior."}
"""

    try:
        content_analysis = llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=ContentAnalysisModel,
        )
    except Exception:
        logger.exception("Content analyst failed. Using fallback.")
        content_analysis = _fallback_analysis(state)

    logger.info("Content analyst completed")
    return {
        "content_analysis": content_analysis,
        "analysis_approved": False,
        "pedagogical_structure": {},
        "structure_approved": False,
        "slide_plan": [],
        "presentation_path": "",
        "current_step": "content_analysis",
        "status": "analysis_completed",
        "error_message": "",
    }