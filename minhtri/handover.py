"""SỔ BÀN GIAO — liên tục giữa các phiên (Điều 13, 14 Luật Kiến trúc Tối cao).

Chỉ ghi thêm, chuỗi băm. Mỗi phiên sửa repo ghi đúng một dòng khi đóng phiên.
"""
import json
import os
from typing import List, Optional

from .canon import now_iso, sha256
from .chain import HashChain

REQUIRED = {"session": str, "provider": str, "role": str, "started_from": str,
            "law_sha256": str, "did": list, "verified": list, "open": list, "next": str}
ROLES = {"Ghế 1", "Ghế 2", "Trọng tài", "Thi công"}


class HandoverError(ValueError):
    pass


def law_sha256(root: str) -> str:
    """Băm nội dung luật, chuẩn hoá xuống dòng (Windows CRLF = Linux LF)."""
    with open(os.path.join(root, "LUAT_KIEN_TRUC_TOI_CAO.md"), encoding="utf-8", newline="") as f:
        return sha256(f.read().replace("\r\n", "\n"))


def check_law(root: str) -> dict:
    """Băm luật hiện tại phải khớp khoá brain/law.lock."""
    with open(os.path.join(root, "brain", "law.lock"), encoding="utf-8") as f:
        lock = json.load(f)
    actual = law_sha256(root)
    if actual != lock["sha256"]:
        raise HandoverError(f"Băm luật {actual[:8]} lệch khoá {lock['sha256'][:8]} — luật bị sửa ngoài Chương V.")
    return lock


def validate(entry: dict, law_hash: str) -> None:
    for k, t in REQUIRED.items():
        if k not in entry or not isinstance(entry[k], t):
            raise HandoverError(f"Dòng bàn giao thiếu/sai trường '{k}' ({t.__name__}).")
        if t is str and not entry[k].strip():
            raise HandoverError(f"Trường '{k}' rỗng.")
    if entry["role"] not in ROLES:
        raise HandoverError(f"Vai lạ '{entry['role']}'. Chỉ nhận: {', '.join(sorted(ROLES))}.")
    if not entry["did"] or not entry["verified"]:
        raise HandoverError("'did' và 'verified' không được rỗng — đã làm gì, đã xác minh gì.")
    if entry["law_sha256"] != law_hash:
        raise HandoverError("law_sha256 không khớp luật hiện hành — phiên chưa đọc đúng bản luật.")


class HandoverLog:
    def __init__(self, path: str):
        self.chain = HashChain(path)

    def last(self) -> Optional[dict]:
        e = self.chain.entries()
        return e[-1] if e else None

    def add(self, entry: dict, law_hash: str) -> dict:
        validate(entry, law_hash)
        body = {k: entry[k] for k in REQUIRED}
        body["at"] = now_iso()
        return self.chain.append(body)

    def verify(self) -> bool:
        return self.chain.verify()
