import base64
import json
import time
from pathlib import Path

import openai

from core.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME


class LLMUnavailable(Exception):
    pass


class LLM:
    def __init__(self, api_key: str | None = None):
        resolved = api_key if api_key is not None else DEEPSEEK_API_KEY
        self._api_key = resolved
        self._client = openai.OpenAI(
            api_key=resolved or "no-key",
            base_url=DEEPSEEK_BASE_URL,
        )

    def _check_key(self) -> None:
        if not self._api_key:
            raise LLMUnavailable("No API key configured")

    def chat_json(self, system: str, user: str, max_retries: int = 2) -> dict:
        self._check_key()
        last_exc: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                resp = self._client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0,
                    response_format={"type": "json_object"},
                )
                content = resp.choices[0].message.content or ""
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    if attempt < max_retries:
                        system = system + " Respond ONLY with valid JSON, no prose."
                        continue
                    raise LLMUnavailable("Malformed JSON after retries")
            except openai.AuthenticationError as e:
                raise LLMUnavailable("Invalid API key") from e
            except (openai.APIStatusError, openai.APIConnectionError) as e:
                last_exc = e
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
        raise LLMUnavailable(f"API error after retries: {last_exc}") from last_exc

    def chat_vision(
        self,
        system: str,
        user_text: str,
        image: bytes | str | Path,
        max_retries: int = 2,
    ) -> str:
        self._check_key()
        if isinstance(image, (str, Path)):
            raw = Path(image).read_bytes()
        else:
            raw = image
        b64 = base64.b64encode(raw).decode()
        data_uri = f"data:image/png;base64,{b64}"

        last_exc: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                resp = self._client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": [
                            {"type": "text", "text": user_text},
                            {"type": "image_url", "image_url": {"url": data_uri}},
                        ]},
                    ],
                    temperature=0,
                )
                return resp.choices[0].message.content or ""
            except openai.AuthenticationError as e:
                raise LLMUnavailable("Invalid API key") from e
            except (openai.APIStatusError, openai.APIConnectionError) as e:
                last_exc = e
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
        raise LLMUnavailable(f"API error after retries: {last_exc}") from last_exc
