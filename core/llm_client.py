from pathlib import Path


class LLMUnavailable(Exception):
    pass


class LLM:
    def __init__(self, api_key: str | None = None):
        pass

    def chat_json(self, system: str, user: str, max_retries: int = 2) -> dict:
        raise NotImplementedError

    def chat_vision(
        self,
        system: str,
        user_text: str,
        image: bytes | str | Path,
        max_retries: int = 2,
    ) -> str:
        raise NotImplementedError
