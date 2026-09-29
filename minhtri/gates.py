"""THANG HỌC L0–L9 và CỔNG NÂNG BÀI HỌC → KỸ NĂNG.

Không được nói 'đã hiểu' vì đã đọc nhiều. Muốn lên cấp phải qua cổng bằng chứng.
"""
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional

from .ledger import Score
from .seats import Decision, Verdict


class Level(IntEnum):
    L0_MEMORY = 0
    L1_KNOWLEDGE = 1
    L2_UNDERSTANDING = 2
    L3_PREDICTION = 3
    L4_ACTION = 4
    L5_VALIDATION = 5
    L6_SELF_CRITICISM = 6
    L7_META_LEARNING = 7
    L8_SELF_REPAIR = 8
    L9_TRANSFER = 9


@dataclass
class GatePolicy:
    min_resolved: int = 5
    max_brier: float = 0.20          # 0.25 = đoán mò 50/50
    min_range_hit_rate: float = 0.60


@dataclass
class GateResult:
    passed: bool
    reasons: List[str]


def skill_gate(score: Score, decision: Optional[Decision],
               policy: GatePolicy = GatePolicy()) -> GateResult:
    """Cổng nâng một bài học thành KỸ NĂNG (L5 trở lên)."""
    reasons: List[str] = []
    if score.resolved < policy.min_resolved:
        reasons.append(f"Mới {score.resolved} dự đoán đã chấm, cần ≥ {policy.min_resolved}.")
    if score.brier is not None and score.brier > policy.max_brier:
        reasons.append(f"Brier {score.brier:.3f} > {policy.max_brier} — chưa hơn đoán mò đủ xa.")
    if score.range_hit_rate is not None and score.range_hit_rate < policy.min_range_hit_rate:
        reasons.append(f"Tỷ lệ trúng khoảng {score.range_hit_rate:.2f} < {policy.min_range_hit_rate}.")
    if decision is None:
        reasons.append("Chưa qua ba ghế.")
    elif not decision.independent:
        reasons.append("Trọng tài không độc lập.")
    elif decision.verdict != Verdict.ACCEPT:
        reasons.append(f"Trọng tài: {decision.verdict.value}.")
    return GateResult(passed=not reasons, reasons=reasons or ["Đạt cổng: nâng thành kỹ năng."])


def level_from_evidence(read_sources: int, predictions_registered: int, score: Score,
                        acted: bool, survived_critique: bool) -> Level:
    """Xếp cấp học thực tế — cấp chỉ tăng khi có bằng chứng của cấp đó."""
    lvl = Level.L0_MEMORY
    if read_sources > 0:
        lvl = Level.L1_KNOWLEDGE
    if read_sources > 0 and predictions_registered > 0:
        lvl = Level.L3_PREDICTION
    if lvl >= Level.L3_PREDICTION and acted:
        lvl = Level.L4_ACTION
    if lvl >= Level.L4_ACTION and score.resolved > 0:
        lvl = Level.L5_VALIDATION
    if lvl >= Level.L5_VALIDATION and survived_critique:
        lvl = Level.L6_SELF_CRITICISM
    return lvl
