# Spec 02 — LLM Client

**Step:** 4 of 15  
**Time budget:** ~25 min  
**Checkpoint:** `LLM().chat_json(system, user)` returns a dict when the API key is valid; raises `LLMUnavailable` when the key is missing.

---

## Goal

Implement `core/llm_client.py` — a thin wrapper around the OpenAI Python SDK pointed at the DeepSeek API. Provides `chat_json` (JSON-mode responses) and `chat_vision` (multimodal image input). Both methods retry on transient failures and raise `LLMUnavailable` after `max_retries`.

---

## Dependencies

- `openai` Python SDK (OpenAI-compatible, pointed at DeepSeek base URL)
- `core.config` for `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `MODEL_NAME`, `MODEL_VERSION`
- `core.prompts` for prompt constants (used by callers, not by this module directly)

---

## Class: `LLMUnavailable`

```python
class LLMUnavailable(Exception):
    pass
```

Raised whenever the LLM call cannot be completed after all retries. Callers should catch this and route to `fallback.py`.

---

## Class: `LLM`

### `__init__(self, api_key: str | None = None)`

- If `api_key` is `None`, use `config.DEEPSEEK_API_KEY`.
- If the resolved key is `None` or empty: do NOT raise immediately — defer to call time so the app can start without a key (precomputed mode).
- Create an `openai.OpenAI(api_key=key, base_url=DEEPSEEK_BASE_URL)` client and store as `self._client`.

### `chat_json(self, system: str, user: str, max_retries: int = 2) -> dict`

Calls the chat completions API with `response_format={"type": "json_object"}`, `temperature=0`.

Messages: `[{"role": "system", "content": system}, {"role": "user", "content": user}]`

Retry logic:
1. Try the API call.
2. On success: parse `response.choices[0].message.content` as JSON. If `json.loads` fails, retry once with a stricter system postscript `" Respond ONLY with valid JSON, no prose."`. If it fails again, raise `LLMUnavailable("Malformed JSON after retries")`.
3. On `openai.APIStatusError` (5xx) or `openai.APIConnectionError`: exponential backoff (`2 ** attempt` seconds, max 2 attempts), then raise `LLMUnavailable`.
4. On `openai.AuthenticationError` (401): raise `LLMUnavailable("Invalid API key")` immediately (no retry).
5. If `api_key` is None/empty at call time: raise `LLMUnavailable("No API key configured")`.

Returns `dict`.

### `chat_vision(self, system: str, user_text: str, image: bytes | str | Path, max_retries: int = 2) -> str`

Sends a multimodal message using the OpenAI vision format.

Image encoding:
- If `image` is `bytes`: base64-encode directly.
- If `image` is `Path` or `str`: read the file as bytes, then base64-encode.
- Build data URI: `f"data:image/png;base64,{b64_str}"`.

Message format:
```python
[
  {"role": "system", "content": system},
  {"role": "user", "content": [
    {"type": "text", "text": user_text},
    {"type": "image_url", "image_url": {"url": data_uri}},
  ]},
]
```

Call at `temperature=0`, no `response_format` (vision endpoint returns plain text).

Retry logic: same as `chat_json` but on content errors: just retry with same prompt. Returns `response.choices[0].message.content` as string.

On any failure after retries: raise `LLMUnavailable`.

---

## Error handling summary

| Condition | Behaviour |
|---|---|
| Missing/empty API key | `LLMUnavailable("No API key configured")` |
| 401 AuthenticationError | `LLMUnavailable("Invalid API key")` |
| 5xx / ConnectionError | Retry with backoff, then `LLMUnavailable` |
| Malformed JSON (chat_json) | Retry once with stricter prompt, then `LLMUnavailable` |

---

## Acceptance Criteria

1. `from core.llm_client import LLM, LLMUnavailable` imports cleanly.
2. `LLM(api_key=None)` with no `.env` → calling `chat_json(...)` raises `LLMUnavailable` (not an unhandled exception).
3. With a valid key: `LLM().chat_json("respond with valid json", '{"ok": true}')` returns `{"ok": True}` (or similar).
4. `LLMUnavailable` is a subclass of `Exception`.
