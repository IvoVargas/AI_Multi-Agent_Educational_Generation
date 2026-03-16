from __future__ import annotations

from edu_multi_agent.state import WorkflowState


def generate_content_analysis(state: WorkflowState) -> str:
    """Stub do Analista de Conteúdo para o MVP."""
    objectives = "\n".join(f"- {obj}" for obj in state["learning_objectives"])
    attempt = state.get("attempts_content", 0) + 1
    feedback = state.get("review_feedback", "").strip()
    feedback_line = (
        f"\nAjuste solicitado pelo docente: {feedback}" if feedback and state.get("review_decision") == "retry" else ""
    )

    return (
        "[Analista de Conteúdo]\n"
        f"Tema: {state['topic']}\n"
        f"Público-alvo: {state['target_audience']}\n"
        f"Objetivos de aprendizagem:\n{objectives}\n\n"
        "Diagnóstico inicial:\n"
        "1. Conceitos centrais e pré-requisitos identificados.\n"
        "2. Dificuldades comuns do público-alvo mapeadas.\n"
        "3. Sugestão de exemplos práticos ligados ao contexto do docente.\n"
        f"Versão de análise: {attempt}.{feedback_line}\n"
    )
