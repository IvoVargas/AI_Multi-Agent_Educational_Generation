class LLMService:
    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        return {
            "status": "stub",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
        }