"""SỔ DỰ ĐOÁN — đăng ký trước khi thấy kết quả, chuỗi băm chống sửa lén.

Mỗi dòng JSONL có prev_hash và hash. Sửa một dòng cũ làm gãy chuỗi.
"""
import json
import math
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from .canon import canonical_json, now_iso, sha256

GENESIS = "0" * 64


class LedgerError(ValueError):
    pass


@dataclass
class Score:
    resolved: int
    binary_n: int
    brier: Optional[float]
    range_n: int
    range_hit_rate: Optional[float]

    def to_dict(self):
        return self.__dict__.copy()


class PredictionLedger:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        if not os.path.exists(path):
            open(path, "w", encoding="utf-8").close()

    def entries(self) -> List[dict]:
        with open(self.path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def _append(self, body: dict) -> dict:
        entries = self.entries()
        prev = entries[-1]["hash"] if entries else GENESIS
        record = dict(body, seq=len(entries), prev_hash=prev)
        record["hash"] = sha256(canonical_json(record))
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(canonical_json(record) + "\n")
        return record

    def verify(self) -> bool:
        prev = GENESIS
        for i, e in enumerate(self.entries()):
            body = {k: v for k, v in e.items() if k != "hash"}
            if e.get("seq") != i or e.get("prev_hash") != prev:
                raise LedgerError(f"Gãy chuỗi tại seq {i}.")
            if sha256(canonical_json(body)) != e["hash"]:
                raise LedgerError(f"Băm sai tại seq {i} — dòng đã bị sửa.")
            prev = e["hash"]
        return True

    def _index(self) -> Dict[str, dict]:
        preds, resolved = {}, set()
        for e in self.entries():
            if e["type"] == "PREDICTION":
                preds[e["id"]] = e
            elif e["type"] == "RESOLUTION":
                resolved.add(e["prediction_id"])
        for pid in resolved:
            preds[pid]["_resolved"] = True
        return preds

    def register(self, pid: str, domain: str, question: str, provider: str,
                 probability: Optional[float] = None,
                 low: Optional[float] = None, high: Optional[float] = None,
                 resolve_by: Optional[str] = None, rationale: str = "",
                 skill: Optional[str] = None) -> dict:
        if pid in self._index():
            raise LedgerError(f"Dự đoán {pid} đã tồn tại.")
        binary = probability is not None
        ranged = low is not None and high is not None
        if binary == ranged:
            raise LedgerError("Chọn đúng một dạng: probability (có/không) HOẶC khoảng [low, high].")
        if binary and not 0.0 <= probability <= 1.0:
            raise LedgerError("probability phải trong [0, 1].")
        if ranged:
            if low > high:
                raise LedgerError("low > high.")
            if not (math.isfinite(low) and math.isfinite(high)):
                raise LedgerError("Khoảng dự đoán phải hữu hạn.")
        return self._append({
            "type": "PREDICTION", "id": pid, "domain": domain, "question": question,
            "provider": provider, "probability": probability, "low": low, "high": high,
            "resolve_by": resolve_by, "rationale": rationale, "skill": skill,
            "registered_at": now_iso(),
        })

    def resolve(self, pid: str, outcome, source: str) -> dict:
        idx = self._index()
        if pid not in idx:
            raise LedgerError(f"Không có dự đoán {pid} — không được chấm cái chưa đăng ký.")
        if idx[pid].get("_resolved"):
            raise LedgerError(f"{pid} đã chấm rồi — không chấm lại.")
        if not source:
            raise LedgerError("Kết quả phải có nguồn đo thật.")
        p = idx[pid]
        if p["probability"] is not None and outcome not in (True, False, 0, 1):
            raise LedgerError("Dự đoán có/không cần outcome True/False.")
        now = now_iso()
        late = bool(p.get("resolve_by")) and now[:10] > str(p["resolve_by"])[:10]
        return self._append({"type": "RESOLUTION", "prediction_id": pid, "outcome": outcome,
                             "source": source, "resolved_at": now, "late": late})

    def score(self, domain: Optional[str] = None, provider: Optional[str] = None,
              ids: Optional[List[str]] = None,
              max_rel_width: Optional[float] = None, late_is_miss: bool = False,
              after_seq: Optional[int] = None) -> Score:
        """max_rel_width: khoảng rộng hơn (high-low)/max(|giữa|,1) bị tính là TRƯỢT —
        chặn việc đoán khoảng vô tận để 'trúng' 100%.
        late_is_miss: kết quả chấm sau resolve_by tính là trượt tối đa.
        after_seq: chỉ tính các RESOLUTION ghi sau số thứ tự này."""
        entries = self.entries()
        preds = {e["id"]: e for e in entries if e["type"] == "PREDICTION"}
        bs, hits = [], []
        for e in entries:
            if e["type"] != "RESOLUTION":
                continue
            p = preds[e["prediction_id"]]
            if after_seq is not None and e["seq"] <= after_seq:
                continue
            if ids is not None and p["id"] not in ids:
                continue
            if domain and p["domain"] != domain:
                continue
            if provider and p["provider"] != provider:
                continue
            if late_is_miss and e.get("late"):
                # chấm trễ hạn = TRƯỢT tối đa, không được dùng để né thất bại
                if p["probability"] is not None:
                    bs.append(1.0)
                else:
                    hits.append(0.0)
                continue
            if p["probability"] is not None:
                bs.append((p["probability"] - (1.0 if e["outcome"] else 0.0)) ** 2)
            else:
                width = (p["high"] - p["low"]) / max(abs((p["high"] + p["low"]) / 2), 1.0)
                sharp = max_rel_width is None or width <= max_rel_width
                hits.append(1.0 if sharp and p["low"] <= float(e["outcome"]) <= p["high"] else 0.0)
        return Score(
            resolved=len(bs) + len(hits),
            binary_n=len(bs), brier=(sum(bs) / len(bs)) if bs else None,
            range_n=len(hits), range_hit_rate=(sum(hits) / len(hits)) if hits else None,
        )
