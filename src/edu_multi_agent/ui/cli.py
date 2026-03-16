from __future__ import annotations

from edu_multi_agent.state import ReviewDecision, WorkflowState
from edu_multi_agent.workflow.graph import build_workflow


def collect_user_input() -> WorkflowState:
    print("=== MVP Multi-Agente Educacional ===")
    topic = input("Tema: ").strip()
    target_audience = input("Público-alvo: ").strip()
    objectives_raw = input("Objetivos de aprendizagem (separados por ';'): ").strip()

    objectives = [obj.strip() for obj in objectives_raw.split(";") if obj.strip()]
    if not objectives:
        objectives = ["Compreender os conceitos fundamentais do tema."]

    return {
        "topic": topic,
        "target_audience": target_audience,
        "learning_objectives": objectives,
        "review_history": [],
    }


def cli_review_handler(stage: str, output: str) -> tuple[ReviewDecision, str, str | None]:
    print("\n" + "=" * 70)
    print(f"Revisão humana da etapa: {stage}")
    print("-" * 70)
    print(output)
    print("-" * 70)
    print("[A]provar | [R]efazer com feedback | [E]ditar e continuar")

    while True:
        decision_raw = input("Escolha (A/R/E): ").strip().lower()
        if decision_raw in {"a", "aprovar"}:
            return "approve", "", None
        if decision_raw in {"r", "refazer"}:
            feedback = input("Feedback para refazer: ").strip()
            return "retry", feedback, None
        if decision_raw in {"e", "editar"}:
            edited_output = input("Cole a versão editada para esta etapa: ").strip()
            return "edit", "edição manual do docente", edited_output
        print("Opção inválida. Escreva 'A', 'R' ou 'E'.")


def run_cli() -> None:
    initial_state = collect_user_input()
    app = build_workflow(cli_review_handler)
    final_state = app.invoke(initial_state)

    print("\n" + "=" * 70)
    print("Workflow concluído.")
    print("=" * 70)
    print(final_state.get("orchestrator_note", ""))

    print("\n### Análise de conteúdo")
    print(final_state.get("content_analysis", "(sem conteúdo)"))

    print("\n### Proposta pedagógica")
    print(final_state.get("pedagogical_plan", "(sem conteúdo)"))

    print("\n### Saída final multimédia")
    print(final_state.get("multimedia_content", "(sem conteúdo)"))

    print("\n### Histórico de revisões")
    for event in final_state.get("review_history", []):
        print(f"- {event}")
