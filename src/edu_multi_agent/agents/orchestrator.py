from __future__ import annotations

from edu_multi_agent.state import NextNode, WorkflowState


STEP_TO_NODE: dict[str, NextNode] = {
    "content_analysis": "content_analyst",
    "pedagogical_plan": "instructional_designer",
    "multimedia_content": "multimedia_generator",
}


def choose_next_node(state: WorkflowState) -> NextNode:
    """Agente principal que orquestra os próximos passos do workflow."""
    pending_stage = state.get("pending_review_stage")
    review_decision = state.get("review_decision")

    if pending_stage and review_decision == "retry":
        return STEP_TO_NODE[pending_stage]

    if "content_analysis" not in state:
        return "content_analyst"
    if "pedagogical_plan" not in state:
        return "instructional_designer"
    if "multimedia_content" not in state:
        return "multimedia_generator"

    return "end"


def generate_orchestrator_note(state: WorkflowState, next_node: NextNode) -> str:
    if next_node == "end":
        return "[Agente Principal] Workflow concluído. Todos os artefactos foram aprovados."

    return (
        "[Agente Principal] Próxima ação: "
        f"{next_node}. "
        f"Tema={state['topic']} | Público={state['target_audience']}"
    )
