from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ContentAnalysisModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    theme: str = Field(min_length=3, max_length=200)
    summary: str = Field(min_length=10, max_length=1500)
    key_concepts: List[str] = Field(min_length=3, max_length=12)
    main_topics: List[str] = Field(min_length=3, max_length=12)
    prerequisites: List[str] = Field(default_factory=list, max_length=10)
    possible_difficulties: List[str] = Field(default_factory=list, max_length=10)

    @field_validator("key_concepts", "main_topics", "prerequisites", "possible_difficulties")
    @classmethod
    def clean_list(cls, values: List[str]) -> List[str]:
        cleaned = [v.strip() for v in values if isinstance(v, str) and v.strip()]
        return cleaned


class SectionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    section_title: str = Field(min_length=2, max_length=120)
    goal: str = Field(min_length=5, max_length=300)
    topics: List[str] = Field(min_length=1, max_length=8)

    @field_validator("topics")
    @classmethod
    def clean_topics(cls, values: List[str]) -> List[str]:
        return [v.strip() for v in values if isinstance(v, str) and v.strip()]


class SlideSequenceItemModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slide_number: int = Field(ge=1, le=100)
    title: str = Field(min_length=2, max_length=120)
    objective: str = Field(min_length=5, max_length=300)
    content_points: List[str] = Field(min_length=1, max_length=6)

    @field_validator("content_points")
    @classmethod
    def normalize_points(cls, values: List[str]) -> List[str]:
        cleaned = [v.strip() for v in values if isinstance(v, str) and v.strip()]
        return cleaned[:6]


class PedagogicalStructureModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    presentation_title: str = Field(min_length=2, max_length=200)
    learning_objectives: List[str] = Field(min_length=1, max_length=6)
    sections: List[SectionModel] = Field(min_length=1, max_length=8)
    slide_sequence: List[SlideSequenceItemModel] = Field(min_length=1, max_length=30)

    @field_validator("learning_objectives")
    @classmethod
    def normalize_objectives(cls, values: List[str]) -> List[str]:
        return [v.strip() for v in values if isinstance(v, str) and v.strip()][:6]


class SlidePlanItemModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slide_number: int = Field(ge=0, le=100)
    title: str = Field(min_length=2, max_length=120)
    bullets: List[str] = Field(min_length=1, max_length=6)
    speaker_notes: str = Field(min_length=5, max_length=800)
    visual_description: str = Field(min_length=5, max_length=400)
    image_prompt: str = Field(min_length=5, max_length=500)
    image_path: Optional[str] = None
    kind: str = Field(pattern="^(title|content|closing)$")

    @field_validator("bullets")
    @classmethod
    def normalize_bullets(cls, values: List[str]) -> List[str]:
        cleaned = [v.strip() for v in values if isinstance(v, str) and v.strip()]
        return cleaned[:6]


class OrchestratorMessageModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assistant_message: str = Field(min_length=5, max_length=600)
    tone: Literal["request_info", "inform", "approval", "completion"] = "inform"