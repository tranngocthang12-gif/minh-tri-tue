"""SỔ BÀI HỌC & KỸ NĂNG — có phiên bản, chỉ ghi thêm, có rollback.

BÀI HỌC  = điều rút ra từ kết quả (luôn trỏ về dự đoán đã chấm).
KỸ NĂNG  = bài học đã qua cổng: đủ dự đoán đúng + ba ghế ACCEPT.
Thành công cũng phải bị phản biện: kỹ năng đã nâng vẫn bị kiểm lại (recheck)
và bị ĐÌNH CHỈ nếu dự đoán mới làm nó rớt cổng.

Trạng thái kỹ năng: CANDIDATE → PROMOTED → SUSPENDED / RETIRED; hoặc REJECTED.
"""
from typing import Dict, List, Optional

from .canon import now_iso
from .chain import HashChain
from .epistemics import Claim
from .gates import GatePolicy, skill_gate
from .ledger import PredictionLedger
from .seats import Decision


class BookError(ValueError):
    pass


class LessonBook:
    def __init__(self, path: str):
        self.chain = HashChain(path)

    # ---------- dựng lại trạng thái từ sổ ----------
    def state(self) -> Dict[str, Dict]:
        lessons, skills = {}, {}
        for e in self.chain.entries():
            t = e["type"]
            if t == "LESSON":
                lessons[e["id"]] = e
            elif t == "SKILL_VERSION":
                sk = skills.setdefault(e["skill"], {"versions": [], "status": "CANDIDATE",
                                                    "active_version": None, "history": []})
                sk["versions"].append(e)
                sk["status"] = "CANDIDATE"
            elif t == "SKILL_STATUS":
                sk = skills[e["skill"]]
                sk["status"] = e["status"]
                sk["active_version"] = e.get("version", sk["active_version"])
                sk["history"].append({"status": e["status"], "version": e.get("version"),
                                      "reasons": e["reasons"], "at": e["at"]})
        return {"lessons": lessons, "skills": skills}

    def verify(self) -> bool:
        return self.chain.verify()

    # ---------- bài học ----------
    def add_lesson(self, lid: str, domain: str, claim: Claim, prediction_ids: List[str],
                   ledger: PredictionLedger, provider: str, session: str) -> dict:
        claim.validate()
        if lid in self.state()["lessons"]:
            raise BookError(f"Bài học {lid} đã có.")
        if not prediction_ids:
            raise BookError("Bài học phải trỏ về ít nhất một dự đoán đã chấm — không học từ cảm giác.")
        resolved = {e["prediction_id"] for e in ledger.entries() if e["type"] == "RESOLUTION"}
        missing = [p for p in prediction_ids if p not in resolved]
        if missing:
            raise BookError(f"Dự đoán chưa chấm: {', '.join(missing)}")
        return self.chain.append({"type": "LESSON", "id": lid, "domain": domain,
                                  "claim": claim.to_dict(), "prediction_ids": prediction_ids,
                                  "provider": provider, "session": session, "at": now_iso()})

    # ---------- kỹ năng ----------
    def propose_skill(self, skill: str, lesson_ids: List[str], procedure: str,
                      prediction_ids: List[str], provider: str, session: str) -> dict:
        st = self.state()
        bad = [l for l in lesson_ids if l not in st["lessons"]]
        if bad or not lesson_ids:
            raise BookError(f"Kỹ năng phải dựa trên bài học có thật: thiếu {bad or 'bài học'}")
        if not procedure.strip():
            raise BookError("Kỹ năng phải có quy trình làm được, không chỉ là nhận xét.")
        sk = st["skills"].get(skill)
        version = 1 + (len(sk["versions"]) if sk else 0)
        return self.chain.append({"type": "SKILL_VERSION", "skill": skill, "version": version,
                                  "lesson_ids": lesson_ids, "procedure": procedure,
                                  "prediction_ids": prediction_ids, "provider": provider,
                                  "session": session, "at": now_iso()})

    def _latest(self, skill: str) -> dict:
        sk = self.state()["skills"].get(skill)
        if not sk:
            raise BookError(f"Không có kỹ năng {skill}.")
        return sk

    def try_promote(self, skill: str, ledger: PredictionLedger, decision: Optional[Decision],
                    policy: GatePolicy = GatePolicy()) -> dict:
        sk = self._latest(skill)
        v = sk["versions"][-1]
        score = ledger.score(ids=v["prediction_ids"])
        gate = skill_gate(score, decision, policy)
        status = "PROMOTED" if gate.passed else "REJECTED"
        return self.chain.append({"type": "SKILL_STATUS", "skill": skill, "status": status,
                                  "version": v["version"] if gate.passed else sk["active_version"],
                                  "reasons": gate.reasons, "score": score.to_dict(),
                                  "at": now_iso()})

    def recheck(self, skill: str, ledger: PredictionLedger,
                policy: GatePolicy = GatePolicy()) -> Optional[dict]:
        """Kiểm lại kỹ năng đang PROMOTED trên dự đoán hiện có; rớt cổng → SUSPENDED."""
        sk = self._latest(skill)
        if sk["status"] != "PROMOTED":
            return None
        v = next(x for x in sk["versions"] if x["version"] == sk["active_version"])
        score = ledger.score(ids=v["prediction_ids"])
        reasons = []
        if score.brier is not None and score.brier > policy.max_brier:
            reasons.append(f"Brier {score.brier:.3f} đã vượt {policy.max_brier}.")
        if score.range_hit_rate is not None and score.range_hit_rate < policy.min_range_hit_rate:
            reasons.append(f"Tỷ lệ trúng {score.range_hit_rate:.2f} đã dưới {policy.min_range_hit_rate}.")
        if not reasons:
            return None
        return self.chain.append({"type": "SKILL_STATUS", "skill": skill, "status": "SUSPENDED",
                                  "version": sk["active_version"], "reasons": reasons,
                                  "score": score.to_dict(), "at": now_iso()})

    def rollback(self, skill: str, to_version: int, reason: str) -> dict:
        sk = self._latest(skill)
        ok = [h for h in sk["history"] if h["status"] == "PROMOTED" and h["version"] == to_version]
        if not ok:
            raise BookError(f"Phiên bản {to_version} chưa từng được PROMOTED — không rollback về đó.")
        return self.chain.append({"type": "SKILL_STATUS", "skill": skill, "status": "PROMOTED",
                                  "version": to_version, "reasons": [f"ROLLBACK: {reason}"],
                                  "at": now_iso()})
