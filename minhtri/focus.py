"""CHÁNH TINH TẤN + CHÁNH ĐỊNH — chọn nút thắt đòn bẩy cao nhất, hoặc CHỜ.

Không nghiên cứu vô hạn. Nếu thêm thông tin không đáng giá bằng một phép thử → THỬ.
Nếu không có việc đáng làm → CHỜ.
"""
from dataclasses import dataclass
from typing import List

PRIORITY = {"PREVENT": 1.3, "REMOVE": 1.2, "DEVELOP": 1.0, "MAINTAIN": 0.8}


@dataclass
class Candidate:
    name: str
    kind: str            # PREVENT | REMOVE | DEVELOP | MAINTAIN
    value: float         # giá trị kỳ vọng nếu thành công (đơn vị tùy miền, cùng thang)
    probability: float   # xác suất thành công ước lượng
    cost: float          # chi phí (cùng thang)
    reversible: bool
    research_value: float = 0.0  # giá trị kỳ vọng của việc nghiên cứu thêm


def leverage(c: Candidate) -> float:
    ev = c.value * c.probability * PRIORITY.get(c.kind, 1.0)
    if not c.reversible:
        ev *= 0.5   # CHƯA CHẮC → THỬ NHỎ; việc không đảo ngược bị phạt
    return ev / max(c.cost, 1e-9)


def choose(cands: List[Candidate], min_leverage: float = 1.0, max_focus: int = 3) -> dict:
    ranked = sorted(cands, key=leverage, reverse=True)
    picked = [c for c in ranked if leverage(c) >= min_leverage][:max_focus]
    if not picked:
        return {"decision": "WAIT", "reason": "Không có việc nào đủ đòn bẩy. CHỜ.", "focus": []}
    out = []
    for c in picked:
        action = "RESEARCH" if c.research_value > c.cost else "TEST"
        out.append({"name": c.name, "leverage": round(leverage(c), 3), "action": action})
    return {"decision": "FOCUS", "reason": "Hội tụ vào tối đa ba nút thắt.", "focus": out}
