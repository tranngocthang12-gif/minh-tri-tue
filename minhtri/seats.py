"""BA GHẾ — ĐỀ XUẤT · PHẢN BIỆN · TRỌNG TÀI.

Không ai được tự đề xuất rồi tự duyệt. Tính độc lập theo PHIÊN, không theo tên:
một AI đóng bốn vai trong cùng một phiên không phải bốn người độc lập.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List

from .epistemics import Claim, EvidenceGrade


class Severity(str, Enum):
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    BLOCKING = "BLOCKING"


class Verdict(str, Enum):
    ACCEPT = "ACCEPT"
    NEEDS_TEST = "NEEDS_TEST"
    REJECT = "REJECT"


class SeatError(ValueError):
    pass


@dataclass
class Proposal:
    provider: str
    session: str
    claim: Claim
    evidence: List[str] = field(default_factory=list)


@dataclass
class Objection:
    text: str
    severity: Severity
    kind: str  # COUNTEREVIDENCE | ASSUMPTION | CAUSAL_ERROR | BLIND_SPOT | LEAKAGE | ALT_EXPLANATION
    answered: bool = False


@dataclass
class Critique:
    provider: str
    session: str
    objections: List[Objection]


@dataclass
class Decision:
    verdict: Verdict
    reasons: List[str]
    independent: bool

    def to_dict(self):
        return {"verdict": self.verdict.value, "reasons": self.reasons,
                "independent": self.independent}


def adjudicate(p: Proposal, c: Critique, adjudicator_session: str,
               required_grade: EvidenceGrade = EvidenceGrade.EXPERIMENTAL) -> Decision:
    sessions = {p.session, c.session, adjudicator_session}
    if len(sessions) < 3:
        raise SeatError("Ba ghế phải là ba phiên khác nhau — không tự đề xuất, tự phản biện, tự duyệt.")
    p.claim.validate()
    if not c.objections:
        raise SeatError("Phản biện rỗng không phải phản biện. Người phản biện phải cố tìm chỗ sai.")

    reasons: List[str] = []
    open_blocking = [o for o in c.objections if o.severity == Severity.BLOCKING and not o.answered]
    open_major = [o for o in c.objections if o.severity == Severity.MAJOR and not o.answered]

    if open_blocking:
        reasons += [f"Chưa giải phản chứng chặn: {o.text}" for o in open_blocking]
        if any(o.kind == "COUNTEREVIDENCE" for o in open_blocking):
            return Decision(Verdict.REJECT, reasons, True)
        return Decision(Verdict.NEEDS_TEST, reasons, True)
    if p.claim.evidence_grade < required_grade:
        reasons.append(f"Bằng chứng {p.claim.evidence_grade.name} < yêu cầu {required_grade.name}.")
        return Decision(Verdict.NEEDS_TEST, reasons, True)
    if open_major:
        reasons += [f"Còn phản biện lớn: {o.text}" for o in open_major]
        return Decision(Verdict.NEEDS_TEST, reasons, True)
    reasons.append("Luận điểm đứng vững trước phản biện với bằng chứng đủ chuẩn.")
    return Decision(Verdict.ACCEPT, reasons, True)
