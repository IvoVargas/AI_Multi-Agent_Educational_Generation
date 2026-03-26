from __future__ import annotations

from typing import Any, Dict

from src.services.llm_service import LLMService

llm = LLMService()


def _fallback_analysis(state: dict) -> Dict[str, Any]:
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
        "prerequisites": [
            "conhecimentos introdutórios relacionados com o tema"
        ],
        "possible_difficulties": [
            "interpretação de conceitos mais abstratos",
            "distinção entre noções próximas",
        ],
    }


def run_content_analyst(state: dict) -> dict:
    user_input = state.get("user_input", "")
    metadata = state.get("metadata", {})
    feedback = state.get("analysis_feedback", "").strip()

    system_prompt = """
És um Analista de Conteúdo para um sistema de geração de apresentações educativas.
A tua função é analisar um texto-base e devolver apenas um objeto JSON válido.

Devolve exatamente esta estrutura:
{
  "theme": "string",
  "summary": "string",
  "key_concepts": ["string"],
  "main_topics": ["string"],
  "prerequisites": ["string"],
  "possible_difficulties": ["string"]
}

Regras:
- Escreve em português de Portugal.
- Não cries markdown.
- Não incluas texto fora do JSON.
- Sê objetivo, pedagógico e estruturado.
"""

    user_prompt = f"""
Texto-base:
{user_input}

Metadados:
{metadata}

Feedback de reformulação anterior:
{feedback if feedback else "Sem feedback anterior."}
"""

    try:
        content_analysis = llm.generate_json(system_prompt, user_prompt)
    except Exception:
        content_analysis = _fallback_analysis(state)

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