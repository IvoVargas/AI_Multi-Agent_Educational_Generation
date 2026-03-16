from __future__ import annotations

from edu_multi_agent.state import WorkflowState


def generate_multimedia_content(state: WorkflowState) -> str:
    """Stub do Gerador Multimédia focado em plano de slides PowerPoint."""
    attempt = state.get("attempts_multimedia", 0) + 1
    feedback = state.get("review_feedback", "").strip()
    feedback_line = (
        f"\nAjuste solicitado pelo docente: {feedback}" if feedback and state.get("review_decision") == "retry" else ""
    )

    return (
        "[Gerador de Slides PowerPoint]\n"
        "Plano de apresentação (10 slides):\n"
        "1. Título e objetivos da aula\n"
        "2. Contextualização do tema\n"
        "3. Conceito-chave 1\n"
        "4. Conceito-chave 2\n"
        "5. Exemplo aplicado\n"
        "6. Atividade guiada\n"
        "7. Discussão de erros comuns\n"
        "8. Síntese visual\n"
        "9. Verificação rápida de aprendizagem\n"
        "10. Encerramento e próximos passos\n\n"
        "Notas para o docente:\n"
        "- Usar 1 ideia principal por slide.\n"
        "- Priorizar linguagem simples e exemplos do contexto da turma.\n"
        "- Incluir elementos visuais de apoio em vez de blocos longos de texto.\n\n"
        "Baseado na proposta pedagógica:\n"
        f"{state['pedagogical_plan']}\n"
        f"Versão do plano de slides: {attempt}.{feedback_line}\n"
    )
