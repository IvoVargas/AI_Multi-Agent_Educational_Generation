from __future__ import annotations

import json
import re
from typing import Any, Dict

from openai import OpenAI

from src.config import MODEL_NAME, OPENAI_API_KEY


class LLMService:
    def __init__(self, api_key: str | None = None, model_name: str | None = None) -> None:
        self.client = OpenAI(api_key=api_key or OPENAI_API_KEY)
        self.model_name = model_name or MODEL_NAME

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )
            content = response.choices[0].message.content or "{}"
            return self._parse_json(content)
        except Exception:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )
            content = response.choices[0].message.content or "{}"
            return self._parse_json(content)

    def _parse_json(self, content: str) -> Dict[str, Any]:
        content = content.strip()

        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?", "", content).strip()
            content = re.sub(r"```$", "", content).strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError("Não foi possível converter a resposta do modelo em JSON válido.")