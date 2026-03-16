from __future__ import annotations

from collections.abc import Callable

from langgraph.graph import END, START, StateGraph

from edu_multi_agent.agents import (
    choose_next_node,
    generate_content_analysis,
    generate_multimedia_content,
    generate_orchestrator_note,
    generate_pedagogical_plan,
)
from edu_multi_agent.state import NextNode, ReviewDecision, WorkflowState

ReviewHandler = Callable[[str, str], tuple[ReviewDecision, str, str | None]]


def orchestrator_node(state: WorkflowState) -> WorkflowState:
    next_node = choose_next_node(state)
    return {
        "next_node": next_node,
        "orchestrator_note": generate_orchestrator_note(state, next_node),
    }


def route_from_orchestrator(state: WorkflowState) -> NextNode:
    return state.get("next_node", "end")


def content_analyst_node(state: WorkflowState) -> WorkflowState:
    return {
        "content_analysis": generate_content_analysis(state),
        "pending_review_stage": "content_analysis",
        "attempts_content": state.get("attempts_content", 0) + 1,
    }


def instructional_designer_node(state: WorkflowState) -> WorkflowState:
    return {
        "pedagogical_plan": generate_pedagogical_plan(state),
        "pending_review_stage": "pedagogical_plan",
        "attempts_design": state.get("attempts_design", 0) + 1,
    }


def multimedia_generator_node(state: WorkflowState) -> WorkflowState:
    return {
        "multimedia_content": generate_multimedia_content(state),
        "pending_review_stage": "multimedia_content",
        "attempts_multimedia": state.get("attempts_multimedia", 0) + 1,
    }


def make_review_node(review_handler: ReviewHandler):
    def review_node(state: WorkflowState) -> WorkflowState:
        stage = state["pending_review_stage"]
        stage_output = state[stage]
        decision, feedback, edited_output = review_handler(stage, stage_output)

        history = state.get("review_history", []) + [
            f"{stage}: {decision}" + (f" ({feedback})" if feedback else "")
        ]

        result: WorkflowState = {
            "review_decision": decision,
            "review_feedback": feedback,
            "review_history": history,
        }

        if decision == "edit" and edited_output:
            result[stage] = edited_output

        return result

    return review_node


def build_workflow(review_handler: ReviewHandler):
    graph = StateGraph(WorkflowState)

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("content_analyst", content_analyst_node)
    graph.add_node("review_content", make_review_node(review_handler))
    graph.add_node("instructional_designer", instructional_designer_node)
    graph.add_node("review_design", make_review_node(review_handler))
    graph.add_node("multimedia_generator", multimedia_generator_node)
    graph.add_node("review_multimedia", make_review_node(review_handler))

    graph.add_edge(START, "orchestrator")

    graph.add_conditional_edges(
        "orchestrator",
        route_from_orchestrator,
        {
            "content_analyst": "content_analyst",
            "instructional_designer": "instructional_designer",
            "multimedia_generator": "multimedia_generator",
            "end": END,
        },
    )

    graph.add_edge("content_analyst", "review_content")
    graph.add_edge("review_content", "orchestrator")

    graph.add_edge("instructional_designer", "review_design")
    graph.add_edge("review_design", "orchestrator")

    graph.add_edge("multimedia_generator", "review_multimedia")
    graph.add_edge("review_multimedia", "orchestrator")

    return graph.compile()
