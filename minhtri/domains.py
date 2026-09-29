"""TẦNG 2 — mở một MIỀN tri thức mới.

Tầng 1 không sở hữu chuyên môn; nó chỉ tạo bộ câu hỏi bắt buộc để học một miền.
Mọi câu trả lời ban đầu là UNKNOWN — không bịa kiến thức miền.
"""
import json
import os
import re

from .canon import now_iso

DOMAIN_QUESTIONS = [
    "capabilities_needed",      # Muốn đạt mục tiêu phải có những năng lực nào?
    "capabilities_missing",     # Ta đang thiếu năng lực nào?
    "sources_of_truth",         # Nguồn chân lý ở đâu?
    "reality_metrics",          # Chỉ số nào phản ánh thực tế?
    "experts_needed",           # Cần chuyên gia/vai nào?
    "benchmarks",               # Đo năng lực bằng benchmark gì?
    "cheapest_experiment",      # Thí nghiệm rẻ nhất là gì?
    "money_mechanism",          # CHÁNH MẠNG: đồng tiền sinh ra từ cơ chế nào?
    "harms_and_limits",         # Hại tiềm ẩn, luật, quyền sử dụng
]


def slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not s:
        raise ValueError("Tên miền không hợp lệ (dùng chữ không dấu).")
    return s


def create_domain(root: str, name: str, owner_purpose: str) -> str:
    d = os.path.join(root, slug(name))
    if os.path.exists(d):
        raise FileExistsError(f"Miền {name} đã tồn tại.")
    os.makedirs(d)
    doc = {
        "domain": slug(name),
        "owner_purpose": owner_purpose,
        "created_at": now_iso(),
        "level": "L0_MEMORY",
        "questions": {q: {"status": "UNKNOWN", "answer": None, "evidence": []}
                      for q in DOMAIN_QUESTIONS},
        "open_hypotheses": [],
        "skills": [],
    }
    with open(os.path.join(d, "domain.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return d
