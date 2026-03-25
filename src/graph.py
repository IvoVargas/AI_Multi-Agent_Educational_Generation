from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from langgraph.graph import END, START, StateGraph

from src.agents.content_analyst import run_content_analyst
from src.agents.multimedia_generator import run_multimedia_generator
from src.agents.pedagogical_designer import run_pedagogical_designer
from src.config import OUTPUT_DIR
from src.services.pptx_service import build_presentation
from src.state import PrototypeState


def analysis_review_node(state: PrototypeState) -> dict:
    approved = state.get("analysis_approved", True)
    return {
        "analysis_approved": approved,
        "current_step": "analysis_review",
    }


def structure_review_node(state: PrototypeState) -> dict:
    approved = state.get("structure_approved", True)
    return {
        "structure_approved": approved,
        "current_step": "structure_review",
    }


def analysis_router(state: PrototypeState) -> str:
    return "approved" if state.get("analysis_approved", True) else "rework"


def structure_router(state: PrototypeState) -> str:
    return "approved" if state.get("structure_approved", True) else "rework"


def export_pptx_node(state: PrototypeState) -> dict:
    title = state.get("metadata", {}).get("title", "presentation").strip() or "presentation"
    safe_title = re.sub(r"[^a-zA-Z0-9_-]+", "_", title).strip("_").lower() or "presentation"

    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
    output_path = output_dir / filename

    presentation_path = build_presentation(
        slide_plan=state.get("slide_plan", []),
        metadata=state.get("metadata", {}),
        output_path=str(output_path),
    )

    return {
        "presentation_path": presentation_path,
        "current_step": "export",
        "status": "completed",
    }


def build_graph():
    builder = StateGraph(PrototypeState)

    builder.add_node("content_analysis", run_content_analyst)
    builder.add_node("analysis_review", analysis_review_node)
    builder.add_node("pedagogical_design", run_pedagogical_designer)
    builder.add_node("structure_review", structure_review_node)
    builder.add_node("multimedia_generation", run_multimedia_generator)
    builder.add_node("export_pptx", export_pptx_node)

    builder.add_edge(START, "content_analysis")
    builder.add_edge("content_analysis", "analysis_review")

    builder.add_conditional_edges(
        "analysis_review",
        analysis_router,
        {
            "approved": "pedagogical_design",
            "rework": "content_analysis",
        },
    )

    builder.add_edge("pedagogical_design", "structure_review")

    builder.add_conditional_edges(
        "structure_review",
        structure_router,
        {
            "approved": "multimedia_generation",
            "rework": "pedagogical_design",
        },
    )

    builder.add_edge("multimedia_generation", "export_pptx")
    builder.add_edge("export_pptx", END)

    return builder.compile()


def run_pipeline(initial_state: PrototypeState) -> PrototypeState:
    graph = build_graph()
    return graph.invoke(initial_state)