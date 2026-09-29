"""Chuỗi băm chỉ-ghi-thêm dùng chung cho các sổ (bài học, kỹ năng…)."""
import json
import os
from typing import List

from .canon import canonical_json, sha256

GENESIS = "0" * 64


class ChainError(ValueError):
    pass


class HashChain:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        if not os.path.exists(path):
            open(path, "w", encoding="utf-8").close()

    def entries(self) -> List[dict]:
        with open(self.path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def append(self, body: dict) -> dict:
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
                raise ChainError(f"{os.path.basename(self.path)}: gãy chuỗi tại seq {i}.")
            if sha256(canonical_json(body)) != e["hash"]:
                raise ChainError(f"{os.path.basename(self.path)}: băm sai tại seq {i}.")
            prev = e["hash"]
        return True
