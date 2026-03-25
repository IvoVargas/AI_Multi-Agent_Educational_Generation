from __future__ import annotations

from typing import Any, Dict


def _extract_theme(user_input: str, metadata: Dict[str, Any]) -> str:
    title = metadata.get("title", "").strip()
    if title:
        return title

    first_line = next((line.strip() for line in user_input.splitlines() if line.strip()), "")
    if first_line:
        return first_line[:80]

    return "Tema não especificado"


def run_content_analyst(state: dict) -> dict:
    user_input = state.get("user_input", "")
    metadata = state.get("metadata", {})
    theme = _extract_theme(user_input, metadata)

    summary = user_input[:400].strip()
    if len(user_input) > 400:
        summary += "..."

    content_analysis = {
        "theme": theme,
        "summary": summary or "Resumo conceptual do texto-base.",
        "key_concepts": [
            "conceitos centrais do tema",
            "relações entre tópicos",
            "ideias principais do texto-base",
        ],
        "main_topics": [
            "introdução ao tema",
            "conceitos fundamentais",
            "aplicações ou exemplos",
            "vantagens e limitações",
            "síntese final",
        ],
        "prerequisites": [
            "conhecimentos introdutórios relacionados com o tema"
        ],
        "possible_difficulties": [
            "interpretação de conceitos mais abstratos",
            "distinção entre noções próximas",
        ],
    }

    return {
        "content_analysis": content_analysis,
        "current_step": "content_analysis",
        "status": "analysis_completed",
    }