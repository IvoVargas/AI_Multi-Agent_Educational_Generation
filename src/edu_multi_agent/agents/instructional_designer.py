from __future__ import annotations

from edu_multi_agent.state import WorkflowState


def generate_pedagogical_plan(state: WorkflowState) -> str:
    """Stub do Designer Pedagógico para o MVP."""
    attempt = state.get("attempts_design", 0) + 1
    feedback = state.get("review_feedback", "").strip()
    feedback_line = (
        f"\nAjuste solicitado pelo docente: {feedback}" if feedback and state.get("review_decision") == "retry" else ""
    )

    return (
        "[Designer Pedagógico]\n"
        "Plano de aula proposto:\n"
        "1. Abertura (5 min): ativação de conhecimentos prévios.\n"
        "2. Desenvolvimento (20 min): explicação guiada + exemplo resolvido.\n"
        "3. Prática (15 min): atividade aplicada em pares.\n"
        "4. Fecho (10 min): síntese e avaliação formativa rápida.\n\n"
        "Estratégias didáticas:\n"
        "- Perguntas orientadoras em cada etapa.\n"
        "- Diferenciação por nível de dificuldade.\n"
        "- Rubrica simples para feedback imediato.\n\n"
        "Baseado na análise:\n"
        f"{state['content_analysis']}\n"
        f"Versão de design: {attempt}.{feedback_line}\n"
    )
