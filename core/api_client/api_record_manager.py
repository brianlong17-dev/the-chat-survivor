import json
import os
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class CallRecord:
    index: int
    timestamp: str
    caller: str
    model: str
    response_model: str
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    duration_ms: int


class APIRecordManager:

    def __init__(self):
        self._records: list[CallRecord] = []
        self._log_path = _make_log_path()

        self._total_input_tokens: int = 0
        self._total_output_tokens: int = 0
        self._call_index = 0

        self._lock = threading.Lock()

    def log_call(self, caller, api_model, response_model, response, start):
        prompt, completion, total = self._extract_usage(response)

        with self._lock:
            record = CallRecord(
                index=self._call_index,
                timestamp=datetime.now(timezone.utc).isoformat(),
                caller=caller,
                model=api_model,
                response_model=getattr(response_model, "__name__", str(response_model)),
                prompt_tokens=prompt,
                completion_tokens=completion,
                total_tokens=total,
                duration_ms=int((time.monotonic() - start) * 1000),
            )
            self._call_index += 1
            self._records.append(record)
            self._total_input_tokens += prompt or 0
            self._total_output_tokens += completion or 0

        _write(self._log_path, record)

    def usage_totals(self) -> dict:
        with self._lock:
            return {
                "input": self._total_input_tokens,
                "output": self._total_output_tokens,
                "total": self._total_input_tokens + self._total_output_tokens,
            }

    @staticmethod
    def _extract_usage(response) -> tuple[int | None, int | None, int | None]:
        usage = getattr(response, "usage_metadata", None) or getattr(response, "usage", None)
        if usage is None:
            return None, None, None

        prompt = getattr(usage, "prompt_token_count", None) or getattr(usage, "prompt_tokens", None)
        completion = getattr(usage, "candidates_token_count", None) or getattr(usage, "completion_tokens", None)
        #can be slightly different with metadata
        total = getattr(usage, "total_token_count", None) or getattr(usage, "total_tokens", None)
        if total is None and prompt is not None and completion is not None:
            total = prompt + completion
        return prompt, completion, total



#----------------------------------------#
    def summary(self) -> dict:
        with self._lock:
            records = list(self._records)
            total_input = self._total_input_tokens
            total_output = self._total_output_tokens
        by_caller: dict[str, dict] = {}
        for r in records:
            s = by_caller.setdefault(r.caller, {"calls": 0, "input": 0, "output": 0, "ms": 0})
            s["calls"] += 1
            s["input"] += r.prompt_tokens or 0
            s["output"] += r.completion_tokens or 0
            s["ms"] += r.duration_ms
        return {
            "total_calls": len(records),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "by_caller": by_caller,
        }

    def print_and_write_summary(self) -> None:
        s = self.summary()
        w = 72
        print(f"\n{'─' * w}")
        print(f"  API — {s['total_calls']} calls · "
              f"{s['total_input_tokens']:,} in · "
              f"{s['total_output_tokens']:,} out · "
              f"{s['total_tokens']:,} total")
        print(f"{'─' * w}")
        for caller, stats in s["by_caller"].items():
            print(f"  {caller:<36}  {stats['calls']:3d} calls  "
                  f"{stats['input']:>7,} in  {stats['output']:>7,} out  "
                  f"{stats['ms']:>5}ms")
        print(f"{'─' * w}\n")
        if self._log_path:
            summary_path = self._log_path.replace(".jsonl", "_summary.json")
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(s, f, indent=2)


#------------------------------


def _write(path: str | None, record: CallRecord) -> None:
    if path is None:
        return
    line = json.dumps(asdict(record)) + "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def _make_log_path() -> str:
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs", "api_logs")
    os.makedirs(log_dir, exist_ok=True)
    _prune_logs(log_dir, keep=50)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    suffix = uuid.uuid4().hex[:6]
    return os.path.join(log_dir, f"api_calls_{ts}_{suffix}.jsonl")


def _prune_logs(log_dir: str, keep: int) -> None:
    logs = sorted(os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith(".jsonl"))
    for old in logs[:-keep]:
        os.remove(old)
