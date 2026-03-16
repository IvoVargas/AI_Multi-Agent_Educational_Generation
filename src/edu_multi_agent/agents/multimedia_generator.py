from __future__ import annotations

from edu_multi_agent.state import WorkflowState


def generate_multimedia_content(state: WorkflowState) -> str:
    """Stub do Gerador Multimédia para o MVP."""
    attempt = state.get("attempts_multimedia", 0) + 1
    feedback = state.get("review_feedback", "").strip()
    feedback_line = (
        f"\nAjuste solicitado pelo docente: {feedback}" if feedback and state.get("review_decision") == "retry" else ""
    )

    return (
        "[Gerador Multimédia]\n"
        "Pacote multimédia (protótipo):\n"
        "- Roteiro de 6 slides com pontos-chave da aula.\n"
        "- Guião curto de vídeo (2-3 min) para introdução do tema.\n"
        "- Quiz de 5 perguntas de escolha múltipla para reforço.\n\n"
        "Conteúdo base usado:\n"
        f"{state['pedagogical_plan']}\n"
        f"Versão multimédia: {attempt}.{feedback_line}\n"
    )
