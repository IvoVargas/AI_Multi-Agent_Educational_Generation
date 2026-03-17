from __future__ import annotations

from typing import Literal, TypedDict


ReviewDecision = Literal["approve", "retry", "edit"]
ReviewStage = Literal["content_analysis", "pedagogical_plan", "multimedia_content"]
NextNode = Literal["content_analyst", "instructional_designer", "multimedia_generator", "end"]


class WorkflowState(TypedDict, total=False):
    topic: str
    target_audience: str
    learning_objectives: list[str]

    content_analysis: str
    pedagogical_plan: str
    multimedia_content: str

    orchestrator_note: str
    next_node: NextNode

    pending_review_stage: ReviewStage
    review_decision: ReviewDecision
    review_feedback: str
    review_history: list[str]

    attempts_content: int
    attempts_design: int
    attempts_multimedia: int
