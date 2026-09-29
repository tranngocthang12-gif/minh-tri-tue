"""BENCHMARK CHO AI — đề công khai, ĐÁP ÁN NIÊM PHONG.

- Đề (suite) nằm trong repo, chỉ chứa băm SHA-256 của đáp án.
- Đáp án (key) do Owner giữ NGOÀI repo; khi chấm, băm phải khớp → không ai sửa đáp án sau khi thi.
- AI soạn đề KHÔNG được chấm điểm trên đề của chính mình (độc lập).
- Chấm tự động: choice (đúng/sai), set (F1 trên tập mã lỗi), number (sai số cho phép).
"""
import json
from typing import Dict

from .canon import canonical_json, sha256
from .providers import ProviderRegistry


class BenchError(ValueError):
    pass


def key_hash(key: dict) -> str:
    return sha256(canonical_json(key))


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def export_prompt(suite: dict) -> str:
    """Tạo đề bài dạng văn bản để dán cho một AI."""
    lines = [f"# BÀI THI {suite['id']}", "",
             suite["instructions"], "",
             "Trả lời DUY NHẤT một khối JSON dạng {\"<mã câu>\": <đáp án>, ...}.", ""]
    for it in suite["items"]:
        lines.append(f"## {it['id']}  ({it['task']} · {it['type']})")
        lines.append(it["prompt"])
        if it.get("options"):
            lines.append("Lựa chọn: " + ", ".join(it["options"]))
        lines.append("")
    return "\n".join(lines)


def _grade_item(item: dict, expected, got) -> float:
    t = item["type"]
    if got is None:
        return 0.0
    if t == "choice":
        return 1.0 if str(got).strip().upper() == str(expected).upper() else 0.0
    if t == "set":
        g = {str(x).strip().upper() for x in (got if isinstance(got, list) else [got])}
        e = {str(x).upper() for x in expected}
        if not g or not e:
            return 0.0
        tp = len(g & e)
        if tp == 0:
            return 0.0
        prec, rec = tp / len(g), tp / len(e)
        return 2 * prec * rec / (prec + rec)
    if t == "number":
        try:
            return 1.0 if abs(float(got) - float(expected)) <= item.get("tolerance", 1e-6) else 0.0
        except (TypeError, ValueError):
            return 0.0
    raise BenchError(f"Loại câu lạ: {t}")


def grade(suite: dict, key: dict, answers: Dict, provider: str) -> Dict[str, float]:
    if key.get("suite") != suite["id"]:
        raise BenchError("Đáp án không thuộc bài thi này.")
    if key_hash(key) != suite["key_sha256"]:
        raise BenchError("Băm đáp án không khớp — đáp án đã bị sửa hoặc sai tệp.")
    if provider in suite.get("authors", []):
        raise BenchError(f"{provider} là tác giả đề — không được chấm trên đề của chính mình.")
    per_task: Dict[str, list] = {}
    for it in suite["items"]:
        s = _grade_item(it, key["answers"][it["id"]], answers.get(it["id"]))
        per_task.setdefault(it["task"], []).append(s)
    return {t: round(sum(v) / len(v), 4) for t, v in per_task.items()}


def record(registry: ProviderRegistry, provider: str, suite_id: str, scores: Dict[str, float]) -> None:
    for task, s in scores.items():
        registry.record(provider, task, s, suite_id)
