from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class PrototypeState(TypedDict, total=False):
    session_id: str

    user_input: str
    metadata: Dict[str, Any]

    content_analysis: Dict[str, Any]
    analysis_approved: bool
    analysis_feedback: str

    pedagogical_structure: Dict[str, Any]
    structure_approved: bool
    structure_feedback: str

    slide_plan: List[Dict[str, Any]]
    generated_images: List[Dict[str, Any]]

    presentation_path: str

    current_step: str
    status: str
    error_message: str


def create_initial_state(
    text_base: str,
    title: str,
    target_audience: str,
    education_level: str,
    presentation_goal: str,
    num_slides: int,
    language: str,
    extra_instructions: str,
) -> PrototypeState:
    return {
        "user_input": text_base.strip(),
        "metadata": {
            "title": title.strip(),
            "target_audience": target_audience.strip(),
            "education_level": education_level.strip(),
            "presentation_goal": presentation_goal.strip(),
            "num_slides": int(num_slides),
            "language": language.strip() or "pt-PT",
            "extra_instructions": extra_instructions.strip(),
        },
        "content_analysis": {},
        "analysis_approved": True,
        "analysis_feedback": "",
        "pedagogical_structure": {},
        "structure_approved": True,
        "structure_feedback": "",
        "slide_plan": [],
        "generated_images": [],
        "presentation_path": "",
        "current_step": "input",
        "status": "initialized",
        "error_message": "",
    }