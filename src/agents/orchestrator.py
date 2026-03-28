from __future__ import annotations

from typing import Dict, List

from src.models import OrchestratorMessageModel
from src.services.llm_service import LLMService
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)
llm = LLMService()

FIELD_LABELS = {
    "text_base": "texto-base",
    "title": "título",
    "target_audience": "público-alvo",
    "education_level": "nível de ensino",
    "presentation_goal": "objetivo da apresentação",
    "num_slides": "número aproximado de slides",
    "language": "idioma",
}


def _compute_missing_fields(state: dict) -> List[str]:
    metadata = state.get("metadata", {})
    missing: List[str] = []

    if not state.get("user_input", "").strip():
        missing.append("text_base")

    for key in ["title", "target_audience", "education_level", "presentation_goal"]:
        if not str(metadata.get(key, "")).strip():
            missing.append(key)

    num_slides = metadata.get("num_slides", 0)
    try:
        if int(num_slides) <= 0:
            missing.append("num_slides")
    except Exception:
        missing.append("num_slides")

    if not str(metadata.get("language", "")).strip():
        missing.append("language")

    return missing


def _fallback_message(next_action: str, missing_fields: List[str]) -> str:
    if next_action == "ask_user" and missing_fields:
        readable = ", ".join(FIELD_LABELS.get(field, field) for field in missing_fields)
        return f"Antes de avançar, preciso que preenchas: {readable}."

    if next_action == "run_content_analysis":
        return "Os dados essenciais já estão preenchidos. Vou gerar a análise conceptual."

    if next_action == "wait_analysis_approval":
        return "A análise conceptual está pronta. Revê o resultado e aprova ou pede reformulação."

    if next_action == "run_pedagogical_design":
        return "A análise foi aprovada. Vou gerar a estrutura pedagógica."

    if next_action == "wait_structure_approval":
        return "A estrutura pedagógica está pronta. Revê o resultado e aprova ou pede reformulação."

    if next_action == "run_multimedia_generation":
        return "A estrutura foi aprovada. Vou preparar o plano de slides e os elementos visuais."

    if next_action == "export_pptx":
        return "O plano multimédia está concluído. Vou exportar o PowerPoint final."

    if next_action == "completed":
        return "O processo está concluído e a apresentação já foi gerada."

    return "Estado atualizado."


def _generate_assistant_message(state: dict, next_action: str, missing_fields: List[str]) -> str:
    metadata = state.get("metadata", {})

    system_prompt = """
És um agente orquestrador de um sistema multiagente para geração de apresentações educativas.
A tua função é comunicar com o utilizador de forma curta, clara e objetiva.
Responde apenas com JSON válido.

Estrutura obrigatória:
{
  "assistant_message": "string",
  "tone": "request_info" | "inform" | "approval" | "completion"
}
"""

    user_prompt = f"""
Estado atual:
- current_step: {state.get('current_step', '')}
- status: {state.get('status', '')}
- next_action: {next_action}
- missing_fields: {missing_fields}
- title: {metadata.get('title', '')}
- target_audience: {metadata.get('target_audience', '')}
- education_level: {metadata.get('education_level', '')}
- presentation_goal: {metadata.get('presentation_goal', '')}

Gera uma mensagem curta ao utilizador em português de Portugal.
"""

    try:
        response = llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=OrchestratorMessageModel,
        )
        return response["assistant_message"]
    except Exception:
        logger.exception("Orchestrator message generation failed. Using fallback.")
        return _fallback_message(next_action, missing_fields)


def run_orchestrator(state: dict) -> Dict:
    logger.info("Orchestrator started")
    updated = dict(state)

    missing_fields = _compute_missing_fields(updated)
    updated["missing_fields"] = missing_fields
    updated["awaiting_user_input"] = False

    if missing_fields:
        next_action = "ask_user"
    elif not updated.get("content_analysis"):
        next_action = "run_content_analysis"
    elif updated.get("content_analysis") and not updated.get("analysis_approved"):
        next_action = "wait_analysis_approval"
    elif updated.get("analysis_approved") and not updated.get("pedagogical_structure"):
        next_action = "run_pedagogical_design"
    elif updated.get("pedagogical_structure") and not updated.get("structure_approved"):
        next_action = "wait_structure_approval"
    elif updated.get("structure_approved") and not updated.get("slide_plan"):
        next_action = "run_multimedia_generation"
    elif updated.get("slide_plan") and not updated.get("presentation_path"):
        next_action = "export_pptx"
    else:
        next_action = "completed"

    updated["next_action"] = next_action
    updated["assistant_message"] = _generate_assistant_message(
        updated,
        next_action=next_action,
        missing_fields=missing_fields,
    )

    if next_action in {"ask_user", "wait_analysis_approval", "wait_structure_approval"}:
        updated["awaiting_user_input"] = True
        updated["status"] = "awaiting_input"
    elif next_action == "completed":
        updated["status"] = "completed"
    else:
        updated["status"] = "ready_to_continue"

    updated["current_step"] = "orchestration"
    logger.info("Orchestrator decided next_action=%s", next_action)
    return updated