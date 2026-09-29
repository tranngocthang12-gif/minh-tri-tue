"""KHUNG NHÌN VẤN ĐỀ (lấy cảm hứng cấu trúc Tứ Diệu Đế).

Thứ tự bắt buộc: THỰC TRẠNG → ĐIỀU KIỆN → ĐÍCH → CON ĐƯỜNG.
Không được nhảy thẳng vào giải pháp. Đây là mô hình ứng dụng lấy cảm hứng,
KHÔNG phải định nghĩa lại giáo pháp.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class Stage(str, Enum):
    REALITY = "REALITY"
    CONDITIONS = "CONDITIONS"
    TARGET = "TARGET"
    PATH = "PATH"


ORDER = [Stage.REALITY, Stage.CONDITIONS, Stage.TARGET, Stage.PATH]

REQUIRED = {
    Stage.REALITY: ["current_state", "undesired_state", "known", "unknown", "limits", "risks",
                    "cost_of_no_change"],
    Stage.CONDITIONS: ["factors"],
    Stage.TARGET: ["true_goal", "means_not_goal", "stop", "reduce", "increase", "build",
                   "protect", "out_of_control"],
    Stage.PATH: ["steps", "first_cheap_test", "kill_criteria"],
}

FACTOR_ROLES = {"CAUSE", "CONDITION", "TRIGGER", "MAINTAINER", "AMPLIFIER", "FEEDBACK_LOOP"}


class InquiryError(ValueError):
    pass


@dataclass
class Inquiry:
    purpose: str
    domain: str
    stages: Dict[str, dict] = field(default_factory=dict)

    def next_stage(self) -> Stage:
        for s in ORDER:
            if s.value not in self.stages:
                return s
        raise InquiryError("Khung đã hoàn tất.")

    def fill(self, stage: Stage, data: dict) -> None:
        expected = self.next_stage()
        if stage != expected:
            raise InquiryError(f"Chưa được làm {stage.value}. Bước kế tiếp phải là {expected.value}.")
        missing = [k for k in REQUIRED[stage] if k not in data]
        if missing:
            raise InquiryError(f"{stage.value} thiếu: {', '.join(missing)}")
        if stage == Stage.REALITY and not data["unknown"]:
            raise InquiryError("REALITY phải liệt kê điều CHƯA biết — không ai biết hết.")
        if stage == Stage.CONDITIONS:
            self._check_factors(data["factors"])
        if stage == Stage.PATH and not data["kill_criteria"]:
            raise InquiryError("PATH phải có điều kiện dừng (kill criteria).")
        self.stages[stage.value] = data

    @staticmethod
    def _check_factors(factors: List[dict]) -> None:
        if not factors:
            raise InquiryError("CONDITIONS cần ít nhất một yếu tố.")
        for f in factors:
            if f.get("role") not in FACTOR_ROLES:
                raise InquiryError(f"Vai trò yếu tố không hợp lệ: {f.get('role')}")
            if f.get("role") == "CAUSE" and f.get("basis") == "CORRELATION_ONLY":
                raise InquiryError("Không được gọi là CAUSE khi chỉ có tương quan.")

    @property
    def complete(self) -> bool:
        return all(s.value in self.stages for s in ORDER)

    def to_dict(self) -> dict:
        return {"purpose": self.purpose, "domain": self.domain, "stages": self.stages}
