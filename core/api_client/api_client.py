from __future__ import annotations

import inspect
import json
import os
import random
import time
from typing import TYPE_CHECKING, Literal, get_args, get_origin
from pydantic import BaseModel
import google.genai.types as types

MAX_TOKENS_PER_GAME_CAP = int(os.environ.get("MAX_TOKENS_PER_GAME", 1500000))

from core.sinks.game_sink import NoopGameSink
from core.api_client.api_record_manager import APIRecordManager

if TYPE_CHECKING:
    from core.sinks.game_sink import GameEventSink

class BudgetExceeded(Exception):
    pass

class APIClient:
    def __init__(self, client, model: str, higher_model_name: str, lower_model_name=None,  sink: GameEventSink = None,
                 token_budget: int = None) -> None:
        if token_budget is None:
            raise ValueError("token_budget is required")
        self._mock_output = False
        self._client = client
        self.default_model = model
        self.higher_model = higher_model_name
        self.lower_model = lower_model_name
        if not sink:
            self.sink = NoopGameSink()
        else:
            self.sink = sink
        self._record_manager = APIRecordManager()
        self.token_budget = min(token_budget, MAX_TOKENS_PER_GAME_CAP)
        
    def _mock_response(self, response_model):
        long_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, \n \n sunt in culpa qui officia deserunt mollit anim id est laborum."
        short_text = "Lorem ipsum dolor sit amet"
        values = {}
        for name, field_info in response_model.model_fields.items():
            annotation = field_info.annotation
            if get_origin(annotation) is Literal:
                values[name] = random.choice(get_args(annotation))
            elif get_origin(annotation) is list:
                inner = get_args(annotation)[0] if get_args(annotation) else str
                if get_origin(inner) is Literal:
                    values[name] = [random.choice(get_args(inner))]
                else:
                    values[name] = [f"test [{name}]"]
            elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
                values[name] = self._mock_response(annotation)
            elif annotation is bool:
                values[name] = random.choice([True, False])
            elif annotation is int:
                values[name] = 2
            elif annotation is float:
                values[name] = 0.0
            else:
                values[name] = f"{short_text}  [{name}]"
        return response_model(**values)

    def _make_call(self, messages, api_model, response_model, thinking=False):
        
        if thinking:
            thinking_config = types.ThinkingConfig(thinking_budget=512, include_thoughts=True)
        else:
            thinking_config = types.ThinkingConfig(thinking_budget=0, include_thoughts=False)
        system_content = next((m["content"] for m in messages if m["role"] == "system"), None)
        user_content = next((m["content"] for m in messages if m["role"] == "user"), None)
        max_429_retries = 8
        backoff = 2
        for attempt in range(max_429_retries):
            try: 
                response = self._client.models.generate_content(
                    model=api_model,
                    contents=user_content,  # just the user message string
                    config=types.GenerateContentConfig(
                        system_instruction=system_content,
                        response_mime_type="application/json",
                        response_schema=response_model,
                        thinking_config=thinking_config,
                        temperature=1.4,
                        #top_p=0.99,
                        #top_k=64
                    ),
                )
                result = response_model(**json.loads(response.text))
                break
            except json.JSONDecodeError:
                if attempt < max_429_retries - 1:
                    print(f"malformed JSON response — retrying ({attempt + 1}/{max_429_retries - 1})")
                    continue
                raise
            except Exception as e:
                if attempt < max_429_retries - 1 and (_is_rate_limit(e) or _is_transient_server_error(e)):
                    wait = backoff * (2 ** attempt)
                    reason = "429 rate limit" if _is_rate_limit(e) else "5xx server error"
                    error_message = (f"server {reason} — waiting {wait}s before retry {attempt + 1}/{max_429_retries - 1}")
                    print(error_message)
                    if attempt > 1:
                        self.sink.system_private(error_message)
                    time.sleep(wait)
                else:
                    raise
        return response, result
    
    def create(self, response_model, messages: list, thinking=False, use_higher_model = False, use_lower_model=False):
        if self._mock_output:
            return self._mock_response(response_model)
        if self._record_manager._total_api_tokens > self.token_budget:
            raise BudgetExceeded(f"Token budget of {self.token_budget} exceeded")
        
        if use_higher_model:
            api_model = self.higher_model
        elif use_lower_model and self.lower_model:
            api_model = self.lower_model
        else:
            api_model = self.default_model
            

        caller = _caller()
        start = time.monotonic()
        response, result = self._make_call(messages, api_model, response_model, thinking=thinking)
        self._record_manager.log_call(
            caller=caller,
            api_model=api_model,
            response_model=response_model,
            response=response,
            start=start,
        )
        return result

    def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/webm", model: str | None = None, hints: list[str] | None = None) -> str:
        hint_text = ""
        if hints:
            hint_text = f"\nThe following names and terms may appear: {', '.join(hints)}."
            
        api_model = model or self.default_model
        response = self._client.models.generate_content(
            model=api_model,
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                f"Transcribe this audio exactly. Return only the spoken words, nothing else. {hint_text}",
            ],
        )
        return response.text.strip()

    def summary(self) -> dict:
        return self._record_manager.summary()

    def print_and_write_summary(self) -> None:
        self._record_manager.print_and_write_summary()

    def usage_totals(self) -> dict:
        return self._record_manager.usage_totals()


# ── helpers ──────────────────────────────────────────────────────────────────

_SKIP = {"core.api_client", "agents.base_agent"}


def _is_rate_limit(exc: Exception) -> bool:
    msg = str(exc)
    return "429" in msg or "RESOURCE_EXHAUSTED" in msg


def _is_transient_server_error(exc: Exception) -> bool:
    msg = str(exc)
    return any(code in msg for code in ("500", "502", "503", "504"))


def _caller() -> str:
    for frame in inspect.stack():
        module = frame.frame.f_globals.get("__name__", "")
        if any(module.startswith(s) for s in _SKIP):
            continue
        cls = frame.frame.f_locals.get("self")
        cls_name = type(cls).__name__ if cls else ""
        return f"{cls_name}.{frame.function}" if cls_name else frame.function
    return "unknown"



