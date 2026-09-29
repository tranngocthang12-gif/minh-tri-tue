"""SỔ BÀI HỌC & KỸ NĂNG — có phiên bản, chỉ ghi thêm, có rollback.

BÀI HỌC  = điều rút ra từ kết quả; luôn trỏ về dự đoán ĐÃ CHẤM.
KỸ NĂNG  = bài học đã qua cổng: dự đoán của chính các bài học đó đủ đúng
           + ba ghế (ba phiên khác nhau) ACCEPT — trọng tài được gọi TRONG hàm,
           không nhận Decision dựng sẵn.
Thành công cũng phải bị phản biện: recheck chấm lại kỹ năng đang PROMOTED trên
dự đoán của phiên bản active + mọi dự đoán mới GẮN tên kỹ năng (ledger skill=...).
Rớt cổng → SUSPENDED. Rollback cũng phải qua cổng và ba ghế lại.

Trạng thái KỸ NĂNG: CANDIDATE → PROMOTED ⇄ SUSPENDED; REJECTED nếu chưa từng có bản đạt.
Trạng thái PHIÊN BẢN: CANDIDATE → PROMOTED | REJECTED (bản rớt không kéo đổ bản đang active).
"""
from typing import Dict, List, Optional

from .canon import now_iso
from .chain import HashChain
from .epistemics import Claim
from .gates import GatePolicy, skill_gate
from .ledger import PredictionLedger, Score
from .seats import Critique, Proposal, adjudicate


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
                sk = skills.setdefault(e["skill"], {
                    "versions": [], "version_status": {}, "status": "CANDIDATE",
                    "active_version": None, "promoted_at": None, "history": []})
                sk["versions"].append(e)
                sk["version_status"][str(e["version"])] = "CANDIDATE"
            elif t == "SKILL_STATUS":          # PROMOTED | SUSPENDED — đổi trạng thái kỹ năng
                sk = skills[e["skill"]]
                sk["status"] = e["status"]
                sk["active_version"] = e["version"]
                sk["version_status"][str(e["version"])] = e["status"]
                if e["status"] == "PROMOTED":
                    sk["promoted_at"] = e["seq"]
                sk["history"].append({k: e[k] for k in ("status", "version", "reasons", "at")})
            elif t == "VERSION_REJECTED":      # chỉ gắn lên phiên bản mới
                sk = skills[e["skill"]]
                sk["version_status"][str(e["version"])] = "REJECTED"
                if sk["active_version"] is None:
                    sk["status"] = "REJECTED"
                sk["history"].append({"status": "VERSION_REJECTED", "version": e["version"],
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
        preds = {e["id"]: e for e in ledger.entries() if e["type"] == "PREDICTION"}
        resolved = {e["prediction_id"] for e in ledger.entries() if e["type"] == "RESOLUTION"}
        missing = [p for p in prediction_ids if p not in resolved]
        if missing:
            raise BookError(f"Dự đoán chưa chấm: {', '.join(missing)}")
        other = [p for p in prediction_ids if preds[p]["domain"] != domain]
        if other:
            raise BookError(f"Dự đoán khác miền {domain}: {', '.join(other)}")
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
        domains = {st["lessons"][l]["domain"] for l in lesson_ids}
        if len(domains) != 1:
            raise BookError("Các bài học của một kỹ năng phải cùng miền.")
        if not procedure.strip():
            raise BookError("Kỹ năng phải có quy trình làm được, không chỉ là nhận xét.")
        allowed = {p for l in lesson_ids for p in st["lessons"][l]["prediction_ids"]}
        if not prediction_ids:
            raise BookError("Kỹ năng phải có dự đoán làm bằng chứng.")
        stray = [p for p in prediction_ids if p not in allowed]
        if stray:
            raise BookError("Dự đoán không thuộc bài học của kỹ năng (không được chọn "
                            f"dự đoán dễ ngoài lề): {', '.join(stray)}")
        sk = st["skills"].get(skill)
        version = 1 + (len(sk["versions"]) if sk else 0)
        return self.chain.append({"type": "SKILL_VERSION", "skill": skill, "version": version,
                                  "domain": domains.pop(), "lesson_ids": lesson_ids,
                                  "procedure": procedure, "prediction_ids": prediction_ids,
                                  "provider": provider, "session": session, "at": now_iso()})

    def _skill(self, skill: str) -> dict:
        sk = self.state()["skills"].get(skill)
        if not sk:
            raise BookError(f"Không có kỹ năng {skill}.")
        return sk

    @staticmethod
    def _version(sk: dict, version: int) -> dict:
        return next(v for v in sk["versions"] if v["version"] == version)

    @staticmethod
    def _tagged(skill: str, ledger: PredictionLedger) -> List[str]:
        return [e["id"] for e in ledger.entries()
                if e["type"] == "PREDICTION" and e.get("skill") == skill]

    def _score(self, skill: str, v: dict, ledger: PredictionLedger, policy: GatePolicy) -> Score:
        ids = sorted(set(v["prediction_ids"]) | set(self._tagged(skill, ledger)))
        return ledger.score(ids=ids, max_rel_width=policy.max_rel_width)

    def _three_seats(self, v: dict, proposal: Proposal, critique: Critique, adj_session: str):
        if proposal.session != v["session"]:
            raise BookError("Ghế đề xuất phải là đúng phiên đã soạn phiên bản kỹ năng.")
        return adjudicate(proposal, critique, adj_session)

    def try_promote(self, skill: str, ledger: PredictionLedger, proposal: Proposal,
                    critique: Critique, adjudicator_session: str,
                    policy: GatePolicy = GatePolicy()) -> dict:
        sk = self._skill(skill)
        v = sk["versions"][-1]
        if sk["version_status"][str(v["version"])] != "CANDIDATE":
            raise BookError(f"Phiên bản {v['version']} đã được xét.")
        decision = self._three_seats(v, proposal, critique, adjudicator_session)
        score = self._score(skill, v, ledger, policy)
        gate = skill_gate(score, decision, policy)
        base = {"skill": skill, "version": v["version"], "reasons": gate.reasons,
                "score": score.to_dict(), "decision": decision.to_dict(),
                "sessions": [proposal.session, critique.session, adjudicator_session],
                "at": now_iso()}
        if gate.passed:
            return self.chain.append(dict(base, type="SKILL_STATUS", status="PROMOTED"))
        return self.chain.append(dict(base, type="VERSION_REJECTED"))

    def recheck(self, skill: str, ledger: PredictionLedger,
                policy: GatePolicy = GatePolicy()) -> Optional[dict]:
        """Kiểm lại kỹ năng đang PROMOTED; rớt ngưỡng → SUSPENDED."""
        sk = self._skill(skill)
        if sk["status"] != "PROMOTED":
            return None
        v = self._version(sk, sk["active_version"])
        score = self._score(skill, v, ledger, policy)
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

    def rollback(self, skill: str, to_version: int, ledger: PredictionLedger,
                 proposal: Proposal, critique: Critique, adjudicator_session: str,
                 reason: str, policy: GatePolicy = GatePolicy()) -> dict:
        sk = self._skill(skill)
        if not any(h["status"] == "PROMOTED" and h["version"] == to_version for h in sk["history"]):
            raise BookError(f"Phiên bản {to_version} chưa từng được PROMOTED — không rollback về đó.")
        v = self._version(sk, to_version)
        decision = adjudicate(proposal, critique, adjudicator_session)  # ba phiên mới, độc lập
        score = self._score(skill, v, ledger, policy)
        gate = skill_gate(score, decision, policy)
        if not gate.passed:
            raise BookError("Rollback bị từ chối — bản cũ rớt cổng trên dữ liệu hiện có: "
                            + "; ".join(gate.reasons))
        return self.chain.append({"type": "SKILL_STATUS", "skill": skill, "status": "PROMOTED",
                                  "version": to_version, "reasons": [f"ROLLBACK: {reason}"],
                                  "score": score.to_dict(), "decision": decision.to_dict(),
                                  "sessions": [proposal.session, critique.session,
                                               adjudicator_session], "at": now_iso()})
