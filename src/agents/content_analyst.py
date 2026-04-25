from __future__ import annotations

from typing import Dict

from src.agents.file_intake import grounding_context_for_state
from src.models import ContentAnalysisModel
from src.services.llm_service import LLMService
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)
llm = LLMService()


def _fallback_analysis(state: dict, source_names: list[str]) -> Dict:
    user_input = state.get("user_input", "")
    metadata = state.get("metadata", {})
    title = metadata.get("title", "").strip() or "Tema não especificado"

    summary = user_input[:400].strip()
    if len(user_input) > 400:
        summary += "..."
    if not summary and source_names:
        summary = f"Resumo conceptual construído com base nas fontes: {', '.join(source_names[:4])}."

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
        "source_documents": source_names,
    }


def run_content_analyst(state: dict) -> dict:
    logger.info("Content analyst started")
    user_input = state.get("user_input", "")
    metadata = state.get("metadata", {})
    feedback = state.get("analysis_feedback", "").strip()
    query = " ".join(
        str(part) for part in [metadata.get("title", ""), user_input[:1000], feedback] if str(part).strip()
    )
    grounding_context, source_names = grounding_context_for_state(state, query=query, top_n=5)

    system_prompt = """
És um Analista de Conteúdo para um sistema de geração de apresentações educativas.
Usa os documentos de apoio apenas como grounding factual e evita inventar detalhes que não estejam no texto-base ou nas fontes.
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
Texto-base principal:
{user_input or 'Sem texto-base explícito. Usa as fontes anexadas como suporte principal.'}

Metadados:
{metadata}

Documentos de apoio e referências:
{grounding_context or 'Sem documentos adicionais.'}

Feedback anterior:
{feedback if feedback else 'Sem feedback anterior.'}
"""

    try:
        content_analysis = llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=ContentAnalysisModel,
        )
        content_analysis["source_documents"] = source_names
    except Exception:
        logger.exception("Content analyst failed. Using fallback.")
        content_analysis = _fallback_analysis(state, source_names)

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
