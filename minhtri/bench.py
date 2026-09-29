"""BENCHMARK CHO AI — đề công khai, ĐÁP ÁN NIÊM PHONG.

- Đề (suite) nằm trong repo, chỉ chứa băm SHA-256 của đáp án.
- Đáp án (key) do Owner giữ NGOÀI repo; khi chấm, băm phải khớp → không sửa đáp án sau khi thi.
- KHÔNG được thi: tác giả đề (authors), và provider đã ĐỌC đề ngoài phòng thi (exposed_to,
  ví dụ phản biện PR có đề). Phiên thi phải khác mọi phiên soạn đề.
- Chấm tự động: choice (đúng/sai); set (F1 với tập BẮT BUỘC, mã trong tập CHẤP NHẬN không bị
  phạt); number (sai số cho phép).
"""
import json
from typing import Dict

from .canon import canonical_json, sha256
from .providers import ProviderRegistry, canonical

FORBIDDEN_FIELDS = {"answers", "answer", "key", "expected", "solution", "solutions", "required",
                    "optional"}


class BenchError(ValueError):
    pass


def key_hash(key: dict) -> str:
    return sha256(canonical_json(key))


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def leaks(obj, path="") -> list:
    """Tìm trường mang tên đáp án ở bất kỳ tầng nào của đề."""
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in FORBIDDEN_FIELDS:
                found.append(f"{path}/{k}")
            found += leaks(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found += leaks(v, f"{path}[{i}]")
    return found


def check_key(suite: dict, key: dict) -> None:
    if key.get("suite") != suite["id"]:
        raise BenchError("Đáp án không thuộc bài thi này.")
    if key_hash(key) != suite["key_sha256"]:
        raise BenchError("Băm đáp án không khớp — đáp án đã bị sửa hoặc sai tệp.")
    missing = [it["id"] for it in suite["items"] if it["id"] not in key["answers"]]
    if missing:
        raise BenchError(f"Đáp án thiếu câu: {', '.join(missing)}")


def export_prompt(suite: dict) -> str:
    lines = [f"# BÀI THI {suite['id']}", "", suite["instructions"], "",
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
        req = {str(x).upper() for x in expected["required"]}
        ok = req | {str(x).upper() for x in expected.get("optional", [])}
        if not g or not req:
            return 0.0
        recall = len(g & req) / len(req)
        precision = len(g & ok) / len(g)
        return 0.0 if recall == 0 or precision == 0 else 2 * precision * recall / (precision + recall)
    if t == "number":
        try:
            return 1.0 if abs(float(got) - float(expected)) <= item.get("tolerance", 1e-6) else 0.0
        except (TypeError, ValueError):
            return 0.0
    raise BenchError(f"Loại câu lạ: {t}")


def grade(suite: dict, key: dict, answers: Dict, provider: str, session: str) -> Dict[str, float]:
    check_key(suite, key)
    prov = canonical(provider)
    if prov in [canonical(a) for a in suite.get("authors", [])]:
        raise BenchError(f"{prov} là tác giả đề — không được chấm trên đề của chính mình.")
    if prov in [canonical(a) for a in suite.get("exposed_to", [])]:
        raise BenchError(f"{prov} đã đọc đề ngoài phòng thi — điểm sẽ không sạch.")
    if not session or session in suite.get("author_sessions", []):
        raise BenchError("Phiên thi phải có mã và khác mọi phiên soạn đề.")
    per_task: Dict[str, list] = {}
    for it in suite["items"]:
        s = _grade_item(it, key["answers"][it["id"]], answers.get(it["id"]))
        per_task.setdefault(it["task"], []).append(s)
    return {t: round(sum(v) / len(v), 4) for t, v in per_task.items()}


def record(registry: ProviderRegistry, provider: str, suite_id: str, scores: Dict[str, float]) -> None:
    for task, s in scores.items():
        registry.record(provider, task, s, suite_id)
