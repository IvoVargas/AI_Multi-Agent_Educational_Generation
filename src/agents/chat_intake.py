from __future__ import annotations

import re
from typing import Dict

from src.models import ChatRequirementExtractionModel
from src.services.llm_service import LLMService
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)
llm = LLMService()


def _detect_language(message: str) -> str | None:
    lower = message.lower()
    if "pt-pt" in lower or "português de portugal" in lower or "portugues de portugal" in lower:
        return "pt-PT"
    if "português" in lower or "portugues" in lower:
        return "pt-PT"
    if "english" in lower or "inglês" in lower or "ingles" in lower:
        return "en-US"
    if "espanhol" in lower or "español" in lower:
        return "es-ES"
    return None


def _detect_num_slides(message: str) -> int | None:
    match = re.search(r"(\d{1,2})\s*slides?", message, flags=re.IGNORECASE)
    if match:
        value = int(match.group(1))
        if 1 <= value <= 100:
            return value
    return None


def _fallback_extract(message: str, state: dict) -> Dict:
    lower = message.lower().strip()
    next_action = state.get("next_action", "")

    if any(term in lower for term in ["reinicia", "recomeça", "recomeca", "novo tema", "reset"]):
        return {"user_intent": "restart"}

    approve_tokens = ["aprovo", "aprovado", "pode avançar", "podes avançar", "continua", "segue", "ok avança", "ok avanca", "aprovo os resultados", "aprovo a solo", "aprovo solo"]
    if next_action == "wait_analysis_approval" and any(term in lower for term in approve_tokens):
        return {"user_intent": "approve_analysis"}
    if next_action == "wait_structure_approval" and any(term in lower for term in approve_tokens):
        return {"user_intent": "approve_structure"}

    regenerate_tokens = ["reformula", "rever", "altera", "melhora", "mais técnico", "mais tecnico", "mais simples", "encurta", "expande", "solo", "resultados de aprendizagem"]
    if next_action == "wait_analysis_approval" and any(term in lower for term in regenerate_tokens):
        return {"user_intent": "regenerate_analysis", "feedback": message.strip()}
    if next_action == "wait_structure_approval" and any(term in lower for term in regenerate_tokens):
        return {"user_intent": "regenerate_structure", "feedback": message.strip()}

    result: Dict[str, object] = {
        "user_intent": "provide_requirements",
        "num_slides": _detect_num_slides(message),
        "language": _detect_language(message),
    }

    if not state.get("user_input", "").strip():
        result["text_base"] = message.strip()
    else:
        result["extra_instructions"] = message.strip()

    lower_about = re.search(r"sobre\s+(.+?)(?:\s+para\s+|\s+com\s+|\.|$)", message, flags=re.IGNORECASE)
    if lower_about:
        topic = lower_about.group(1).strip(" .,")
        if topic:
            result["title"] = topic[:200]

    audience_match = re.search(r"para\s+(.+?)(?:\s+com\s+|\s+em\s+|\.|$)", message, flags=re.IGNORECASE)
    if audience_match:
        result["target_audience"] = audience_match.group(1).strip(" .,")[:200]

    return {k: v for k, v in result.items() if v not in (None, "")}


def extract_chat_update(message: str, state: dict) -> Dict:
    metadata = state.get("metadata", {})
    system_prompt = """
És um extrator de requisitos para um sistema multiagente que gera apresentações educativas.
Recebes uma mensagem livre do utilizador e devolves apenas JSON válido.

Classifica a intenção do utilizador numa destas categorias:
- provide_requirements: está a dar ou alterar requisitos
- approve_analysis: aprova a análise conceptual
- approve_structure: aprova a estrutura pedagógica e/ou os resultados de aprendizagem SOLO
- regenerate_analysis: quer reformular a análise conceptual
- regenerate_structure: quer reformular a estrutura pedagógica e/ou os resultados de aprendizagem SOLO
- continue: quer apenas que avances para o próximo passo
- restart: quer reiniciar o processo
- unknown: não foi possível determinar

Extrai apenas o que estiver explicitamente ou fortemente implícito na mensagem.
Não inventes valores.

Estrutura obrigatória:
{
  "user_intent": "provide_requirements | approve_analysis | approve_structure | regenerate_analysis | regenerate_structure | continue | restart | unknown",
  "title": "string ou null",
  "target_audience": "string ou null",
  "education_level": "string ou null",
  "presentation_goal": "string ou null",
  "num_slides": 6,
  "language": "pt-PT | en-US | es-ES | null",
  "extra_instructions": "string ou null",
  "text_base": "string ou null",
  "feedback": "string ou null"
}
"""

    user_prompt = f"""
Mensagem do utilizador:
{message}

Estado atual:
- next_action: {state.get('next_action', '')}
- current_step: {state.get('current_step', '')}
- analysis_exists: {bool(state.get('content_analysis'))}
- structure_exists: {bool(state.get('pedagogical_structure'))}
- analysis_approved: {bool(state.get('analysis_approved'))}
- structure_approved: {bool(state.get('structure_approved'))}

Metadados já existentes:
- title: {metadata.get('title', '')}
- target_audience: {metadata.get('target_audience', '')}
- education_level: {metadata.get('education_level', '')}
- presentation_goal: {metadata.get('presentation_goal', '')}
- num_slides: {metadata.get('num_slides', '')}
- language: {metadata.get('language', '')}
"""

    try:
        extracted = llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=ChatRequirementExtractionModel,
        )
        logger.info("Chat intake extraction completed with intent=%s", extracted.get("user_intent"))
        return extracted
    except Exception:
        logger.exception("Chat intake extraction failed. Using fallback heuristics.")
        return _fallback_extract(message, state)
