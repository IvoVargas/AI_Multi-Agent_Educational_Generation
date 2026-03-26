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
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def run_analysis_step(state: PrototypeState) -> PrototypeState:
    logger.info("Pipeline step: analysis")
    updated = dict(state)
    updated.update(run_content_analyst(updated))
    return updated


def run_structure_step(state: PrototypeState) -> PrototypeState:
    logger.info("Pipeline step: pedagogical structure")
    updated = dict(state)
    updated.update(run_pedagogical_designer(updated))
    return updated


def run_multimedia_step(state: PrototypeState) -> PrototypeState:
    logger.info("Pipeline step: multimedia generation")
    updated = dict(state)
    updated.update(run_multimedia_generator(updated))
    return updated


def export_pptx_step(state: PrototypeState) -> PrototypeState:
    logger.info("Pipeline step: export pptx")
    updated = dict(state)
    title = updated.get("metadata", {}).get("title", "presentation").strip() or "presentation"
    safe_title = re.sub(r"[^a-zA-Z0-9_-]+", "_", title).strip("_").lower() or "presentation"

    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"

    presentation_path = build_presentation(
        slide_plan=updated.get("slide_plan", []),
        metadata=updated.get("metadata", {}),
        output_path=str(output_path),
    )

    updated["presentation_path"] = presentation_path
    updated["current_step"] = "export"
    updated["status"] = "completed"
    logger.info("Pipeline finished: %s", presentation_path)
    return updated


def build_graph():
    builder = StateGraph(PrototypeState)

    builder.add_node("content_analysis", run_content_analyst)
    builder.add_node("pedagogical_design", run_pedagogical_designer)
    builder.add_node("multimedia_generation", run_multimedia_generator)
    builder.add_node("export_pptx", export_pptx_step)

    builder.add_edge(START, "content_analysis")
    builder.add_edge("content_analysis", "pedagogical_design")
    builder.add_edge("pedagogical_design", "multimedia_generation")
    builder.add_edge("multimedia_generation", "export_pptx")
    builder.add_edge("export_pptx", END)

    return builder.compile()