from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


SoloLevel = Literal["SOLO_2", "SOLO_3", "SOLO_4", "SOLO_5"]
OutcomeType = Literal[
    "conhecimento_teorico",
    "competencia_pratica_tecnica",
    "competencia_social",
]
OutcomeImportance = Literal["principal", "secundario"]


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
        return [v.strip() for v in values if isinstance(v, str) and v.strip()]


class SoloLearningOutcomeModel(BaseModel):
    """Resultado de aprendizagem classificado segundo a Taxonomia SOLO.

    O nível SOLO_1/pre-structural não é aceite porque não representa um resultado de
    aprendizagem observável para desenho pedagógico.
    """

    model_config = ConfigDict(extra="forbid")

    id: int = Field(ge=1, le=50)
    outcome_type: OutcomeType
    solo_level: SoloLevel
    action_verb: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=10, max_length=450)
    importance: OutcomeImportance = "principal"
    related_topics: List[str] = Field(default_factory=list, max_length=8)
    suggested_learning_activity: str = Field(default="", max_length=350)
    suggested_assessment: str = Field(default="", max_length=350)

    @field_validator("action_verb", "description", "suggested_learning_activity", "suggested_assessment", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> str:
        if value is None:
            return ""
        return " ".join(str(value).split()).strip()

    @field_validator("related_topics")
    @classmethod
    def normalize_related_topics(cls, values: List[str]) -> List[str]:
        return [v.strip() for v in values if isinstance(v, str) and v.strip()][:8]


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
    learning_outcome_ids: List[int] = Field(default_factory=list, max_length=5)
    solo_level: Optional[SoloLevel] = None

    @field_validator("content_points")
    @classmethod
    def normalize_points(cls, values: List[str]) -> List[str]:
        cleaned = [v.strip() for v in values if isinstance(v, str) and v.strip()]
        return cleaned[:6]

    @field_validator("learning_outcome_ids")
    @classmethod
    def normalize_outcome_ids(cls, values: List[int]) -> List[int]:
        cleaned: List[int] = []
        for value in values:
            try:
                ivalue = int(value)
            except Exception:
                continue
            if ivalue > 0 and ivalue not in cleaned:
                cleaned.append(ivalue)
        return cleaned[:5]


class PedagogicalStructureModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    presentation_title: str = Field(min_length=2, max_length=200)
    solo_learning_outcomes: List[SoloLearningOutcomeModel] = Field(min_length=3, max_length=8)
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
    speaker_notes: str = Field(min_length=5, max_length=1200)
    visual_description: str = Field(min_length=5, max_length=500)
    image_prompt: str = Field(min_length=5, max_length=700)
    image_path: Optional[str] = None
    kind: str = Field(pattern="^(title|content|closing)$")
    learning_outcome_ids: List[int] = Field(default_factory=list, max_length=5)
    solo_level: Optional[SoloLevel] = None
    learning_outcome_summary: str = Field(default="", max_length=1000)

    @field_validator("bullets")
    @classmethod
    def normalize_bullets(cls, values: List[str]) -> List[str]:
        cleaned = [v.strip() for v in values if isinstance(v, str) and v.strip()]
        return cleaned[:6]

    @field_validator("learning_outcome_ids")
    @classmethod
    def normalize_slide_outcome_ids(cls, values: List[int]) -> List[int]:
        cleaned: List[int] = []
        for value in values:
            try:
                ivalue = int(value)
            except Exception:
                continue
            if ivalue > 0 and ivalue not in cleaned:
                cleaned.append(ivalue)
        return cleaned[:5]


class OrchestratorMessageModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assistant_message: str = Field(min_length=5, max_length=600)
    tone: Literal["request_info", "inform", "approval", "completion"] = "inform"


class ChatRequirementExtractionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_intent: Literal[
        "provide_requirements",
        "approve_analysis",
        "approve_structure",
        "regenerate_analysis",
        "regenerate_structure",
        "continue",
        "restart",
        "unknown",
    ] = "unknown"
    title: Optional[str] = None
    target_audience: Optional[str] = None
    education_level: Optional[str] = None
    presentation_goal: Optional[str] = None
    num_slides: Optional[int] = Field(default=None, ge=1, le=100)
    language: Optional[str] = None
    extra_instructions: Optional[str] = None
    text_base: Optional[str] = None
    feedback: Optional[str] = None

    @field_validator(
        "title",
        "target_audience",
        "education_level",
        "presentation_goal",
        "language",
        "extra_instructions",
        "text_base",
        "feedback",
        mode="before",
    )
    @classmethod
    def normalize_optional_string(cls, value: object) -> Optional[str]:
        if value is None or not isinstance(value, str):
            return None
        cleaned = value.strip()
        return cleaned or None


class FileRoleClassificationModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["brief", "support", "visual", "template", "other"]
    rationale: str = Field(min_length=5)

    @field_validator("rationale", mode="before")
    @classmethod
    def normalize_rationale(cls, value: object) -> str:
        if value is None:
            return "Classificação automática."
        if not isinstance(value, str):
            value = str(value)
        return " ".join(value.split()).strip()


class BriefExtractionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    target_audience: Optional[str] = None
    education_level: Optional[str] = None
    presentation_goal: Optional[str] = None
    num_slides: Optional[int] = Field(default=None, ge=1, le=100)
    language: Optional[str] = None
    extra_instructions: Optional[str] = None
    text_base: Optional[str] = None

    @field_validator(
        "title",
        "target_audience",
        "education_level",
        "presentation_goal",
        "language",
        "extra_instructions",
        "text_base",
        mode="before",
    )
    @classmethod
    def normalize_brief_fields(cls, value: object) -> Optional[str]:
        if value is None or not isinstance(value, str):
            return None
        cleaned = value.strip()
        return cleaned or None


class SupportDocumentSummaryModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=5, max_length=600)
    key_points: List[str] = Field(default_factory=list)
    preferred_usage: Literal["grounding", "style_reference", "visual_reference", "reference"] = "grounding"

    @field_validator("key_points")
    @classmethod
    def normalize_points(cls, values: List[str]) -> List[str]:
        return [v.strip() for v in values if isinstance(v, str) and v.strip()]
