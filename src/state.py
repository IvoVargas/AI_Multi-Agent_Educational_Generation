from __future__ import annotations

from typing import Any, Dict, List, Literal, TypedDict


class ConversationTurn(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class PrototypeState(TypedDict, total=False):
    session_id: str

    user_input: str
    metadata: Dict[str, Any]

    conversation_history: List[ConversationTurn]
    assistant_message: str
    next_action: str
    awaiting_user_input: bool
    missing_fields: List[str]
    last_user_message: str

    uploaded_files: List[Dict[str, Any]]
    knowledge_chunks: List[Dict[str, Any]]
    retrieval_enabled: bool
    source_summary: str

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
        "conversation_history": [],
        "assistant_message": "",
        "next_action": "ask_user",
        "awaiting_user_input": False,
        "missing_fields": [],
        "last_user_message": "",
        "uploaded_files": [],
        "knowledge_chunks": [],
        "retrieval_enabled": False,
        "source_summary": "Sem ficheiros anexados.",
        "content_analysis": {},
        "analysis_approved": False,
        "analysis_feedback": "",
        "pedagogical_structure": {},
        "structure_approved": False,
        "structure_feedback": "",
        "slide_plan": [],
        "generated_images": [],
        "presentation_path": "",
        "current_step": "input",
        "status": "initialized",
        "error_message": "",
    }


def create_chat_initial_state() -> PrototypeState:
    return create_initial_state(
        text_base="",
        title="",
        target_audience="",
        education_level="",
        presentation_goal="",
        num_slides=6,
        language="pt-PT",
        extra_instructions="",
    )
