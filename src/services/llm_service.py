from __future__ import annotations

from typing import Any, Type

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from src.config import MODEL_NAME, OPENAI_API_KEY
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class LLMService:
    def __init__(self, api_key: str | None = None, model_name: str | None = None) -> None:
        self.client = OpenAI(api_key=api_key or OPENAI_API_KEY)
        self.model_name = model_name or MODEL_NAME

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Type[BaseModel],
    ) -> dict[str, Any]:
        logger.info("LLM request started for schema=%s", schema.__name__)

        response = self.client.chat.completions.create(
            model=self.model_name,
            response_format={"type": "json_object"},
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content or "{}"
        logger.info("LLM response received for schema=%s", schema.__name__)

        try:
            validated = schema.model_validate_json(content)
            logger.info("LLM JSON validated successfully for schema=%s", schema.__name__)
            return validated.model_dump()
        except ValidationError as exc:
            logger.exception("JSON validation failed for schema=%s", schema.__name__)
            raise ValueError(f"Resposta do LLM inválida para {schema.__name__}: {exc}") from exc