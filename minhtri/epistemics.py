"""CHÁNH KIẾN — phân loại điều mình nói và giới hạn độ tin theo bằng chứng.

Luật: niềm tin không được cao hơn chất lượng bằng chứng.
"""
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import List, Optional


class ClaimKind(str, Enum):
    FACT = "FACT"
    OBSERVATION = "OBSERVATION"
    INFERENCE = "INFERENCE"
    HYPOTHESIS = "HYPOTHESIS"
    PREDICTION = "PREDICTION"
    OPINION = "OPINION"
    UNKNOWN = "UNKNOWN"


class EvidenceGrade(IntEnum):
    NONE = 0            # chưa có gì
    ANECDOTE = 1        # một ca, lời kể
    CORRELATIONAL = 2   # tương quan, chưa loại giải thích khác
    REPLICATED = 3      # lặp lại nhiều nguồn độc lập
    EXPERIMENTAL = 4    # phép thử có đối chứng
    REAL_OUTCOME = 5    # kết quả thật đã đối chiếu với dự đoán đăng ký trước


# Trần độ tin theo cấp bằng chứng.
CONFIDENCE_CAP = {
    EvidenceGrade.NONE: 0.30,
    EvidenceGrade.ANECDOTE: 0.45,
    EvidenceGrade.CORRELATIONAL: 0.60,
    EvidenceGrade.REPLICATED: 0.75,
    EvidenceGrade.EXPERIMENTAL: 0.90,
    EvidenceGrade.REAL_OUTCOME: 0.97,
}


class EpistemicError(ValueError):
    pass


@dataclass
class Claim:
    text: str
    kind: ClaimKind
    evidence_grade: EvidenceGrade = EvidenceGrade.NONE
    confidence: Optional[float] = None
    sources: List[str] = field(default_factory=list)

    def validate(self) -> "Claim":
        if not self.text.strip():
            raise EpistemicError("Claim rỗng.")
        if self.kind == ClaimKind.UNKNOWN:
            if self.confidence is not None:
                raise EpistemicError("UNKNOWN không được mang độ tin — hãy nói 'tôi chưa biết'.")
            return self
        if self.confidence is None:
            raise EpistemicError("Thiếu độ tin cho claim không phải UNKNOWN.")
        if not 0.0 <= self.confidence <= 1.0:
            raise EpistemicError("Độ tin phải trong [0, 1].")
        cap = CONFIDENCE_CAP[self.evidence_grade]
        if self.confidence > cap:
            raise EpistemicError(
                f"Độ tin {self.confidence:.2f} vượt trần {cap:.2f} của bằng chứng {self.evidence_grade.name}."
            )
        if self.kind == ClaimKind.FACT:
            if self.evidence_grade < EvidenceGrade.REPLICATED or not self.sources:
                raise EpistemicError("FACT cần bằng chứng ≥ REPLICATED và có nguồn.")
        if self.kind == ClaimKind.OBSERVATION and not self.sources:
            raise EpistemicError("OBSERVATION phải chỉ ra nguồn quan sát.")
        return self

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "kind": self.kind.value,
            "evidence_grade": self.evidence_grade.name,
            "confidence": self.confidence,
            "sources": list(self.sources),
        }
