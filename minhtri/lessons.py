"""SỔ BÀI HỌC & KỸ NĂNG — có phiên bản, chỉ ghi thêm, có rollback.

BÀI HỌC  = điều rút ra từ kết quả; luôn trỏ về dự đoán ĐÃ CHẤM.
KỸ NĂNG  = bài học đã qua cổng: TOÀN BỘ dự đoán của các bài học đó (không chọn lọc)
           đủ đúng + ba ghế (ba phiên khác nhau) ACCEPT — trọng tài gọi TRONG hàm.
           Dự đoán gắn tên kỹ năng (ledger skill=...) KHÔNG BAO GIỜ giúp nâng cấp;
           chúng chỉ dùng để GIÁM SÁT.
Thành công cũng phải bị phản biện:
  - recheck: dự đoán gốc + dự đoán cùng miền gắn tên kỹ năng rớt ngưỡng → SUSPENDED;
  - im lặng không phải còn đúng: sau `stale_after` kết quả mới cùng miền mà kỹ năng
    không có kết quả mới nào gắn tên → STALE.
Kết quả chấm trễ hạn (late) tính là trượt tối đa ở mọi phép chấm của sổ này.
Rollback phải qua cổng, ba ghế lại, không rớt giám sát; thoát STALE cần kết quả mới gắn tên.

Trạng thái KỸ NĂNG: CANDIDATE → PROMOTED ⇄ SUSPENDED/STALE; REJECTED nếu chưa từng có bản đạt.
Trạng thái PHIÊN BẢN: CANDIDATE → PROMOTED | REJECTED (bản rớt không kéo đổ bản đang active).
"""
from typing import Dict, List, Optional

from .canon import now_iso
from .chain import HashChain
from .epistemics import Claim
from .gates import GatePolicy, skill_gate
from .ledger import PredictionLedger, Score, merge_scores
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
            elif t == "SKILL_STATUS":          # PROMOTED | SUSPENDED | STALE
                sk = skills[e["skill"]]
                sk["status"] = e["status"]
                sk["active_version"] = e["version"]
                sk["version_status"][str(e["version"])] = e["status"]
                sk["status_ledger_seq"] = e.get("ledger_seq", -1)
                if e["status"] == "PROMOTED":
                    sk["promoted_at"] = e["seq"]
                    sk["promoted_ledger_seq"] = e.get("ledger_seq", -1)
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
        dropped = sorted(allowed - set(prediction_ids))
        if dropped:
            raise BookError("Phải dùng TOÀN BỘ dự đoán của các bài học — không chọn lọc "
                            f"để né dự đoán sai: thiếu {', '.join(dropped)}")
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
    def _tagged(skill: str, domain: str, ledger: PredictionLedger) -> List[str]:
        return [e["id"] for e in ledger.entries()
                if e["type"] == "PREDICTION" and e.get("skill") == skill and e["domain"] == domain]

    @staticmethod
    def _ledger_seq(ledger: PredictionLedger) -> int:
        entries = ledger.entries()
        return entries[-1]["seq"] if entries else -1

    def _base_score(self, v: dict, ledger: PredictionLedger, policy: GatePolicy) -> Score:
        """Chấm để NÂNG: chỉ dự đoán gốc của bài học."""
        return ledger.score(ids=v["prediction_ids"], max_rel_width=policy.max_rel_width,
                            late_is_miss=True)

    def _watch_score(self, skill: str, v: dict, ledger: PredictionLedger,
                     policy: GatePolicy, since_seq: int = -1) -> Score:
        """Chấm để GIÁM SÁT: dự đoán gốc (mọi thời điểm)
        + dự đoán cùng miền gắn tên có kết quả SAU mốc nâng gần nhất (since_seq)
        + dự đoán gắn tên QUÁ HẠN mà chưa chấm (tính trượt).
        Dự đoán gắn tên cũ trước mốc nâng không được dùng để pha loãng thất bại mới."""
        tagged = self._tagged(skill, v["domain"], ledger)
        base = self._base_score(v, ledger, policy)
        fresh = ledger.score(ids=tagged, max_rel_width=policy.max_rel_width,
                             late_is_miss=True, after_seq=since_seq)
        return merge_scores(base, fresh, ledger.overdue(tagged))

    @staticmethod
    def _watch_failures(score: Score, policy: GatePolicy) -> List[str]:
        reasons = []
        if score.brier is not None and score.brier > policy.max_brier:
            reasons.append(f"Brier {score.brier:.3f} đã vượt {policy.max_brier}.")
        if score.range_hit_rate is not None and score.range_hit_rate < policy.min_range_hit_rate:
            reasons.append(f"Tỷ lệ trúng {score.range_hit_rate:.2f} đã dưới {policy.min_range_hit_rate}.")
        return reasons

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
        score = self._base_score(v, ledger, policy)
        gate = skill_gate(score, decision, policy)
        watch = self._watch_failures(
            self._watch_score(skill, v, ledger, policy, sk.get("promoted_ledger_seq", -1)), policy)
        if watch:
            gate = type(gate)(passed=False, reasons=gate.reasons * (not gate.passed) + watch)
        base = {"skill": skill, "version": v["version"], "reasons": gate.reasons,
                "score": score.to_dict(), "decision": decision.to_dict(),
                "sessions": [proposal.session, critique.session, adjudicator_session],
                "ledger_seq": self._ledger_seq(ledger), "at": now_iso()}
        if gate.passed:
            return self.chain.append(dict(base, type="SKILL_STATUS", status="PROMOTED"))
        return self.chain.append(dict(base, type="VERSION_REJECTED"))

    def recheck(self, skill: str, ledger: PredictionLedger,
                policy: GatePolicy = GatePolicy()) -> Optional[dict]:
        """Giám sát kỹ năng đang PROMOTED: rớt ngưỡng → SUSPENDED; im lặng quá lâu → STALE."""
        sk = self._skill(skill)
        if sk["status"] != "PROMOTED":
            return None
        v = self._version(sk, sk["active_version"])
        score = self._watch_score(skill, v, ledger, policy, sk.get("promoted_ledger_seq", -1))
        reasons = self._watch_failures(score, policy)
        status = "SUSPENDED" if reasons else None
        if not reasons:
            since = sk["status_ledger_seq"]
            tagged = set(self._tagged(skill, v["domain"], ledger))
            preds = {e["id"]: e for e in ledger.entries() if e["type"] == "PREDICTION"}
            new_domain = [e for e in ledger.entries() if e["type"] == "RESOLUTION"
                          and e["seq"] > since and preds[e["prediction_id"]]["domain"] == v["domain"]]
            window = new_domain[-policy.stale_after:]          # cửa sổ TRƯỢT: N kết quả gần nhất
            if len(window) >= policy.stale_after and not any(e["prediction_id"] in tagged for e in window):
                status = "STALE"
                reasons = [f"{policy.stale_after} kết quả gần nhất trong miền {v['domain']} không có "
                           "kết quả nào gắn tên kỹ năng — im lặng không phải bằng chứng còn đúng."]
        if not status:
            return None
        return self.chain.append({"type": "SKILL_STATUS", "skill": skill, "status": status,
                                  "version": sk["active_version"], "reasons": reasons,
                                  "score": score.to_dict(), "ledger_seq": self._ledger_seq(ledger),
                                  "at": now_iso()})

    def rollback(self, skill: str, to_version: int, ledger: PredictionLedger,
                 proposal: Proposal, critique: Critique, adjudicator_session: str,
                 reason: str, policy: GatePolicy = GatePolicy()) -> dict:
        sk = self._skill(skill)
        if not any(h["status"] == "PROMOTED" and h["version"] == to_version for h in sk["history"]):
            raise BookError(f"Phiên bản {to_version} chưa từng được PROMOTED — không rollback về đó.")
        v = self._version(sk, to_version)
        if sk["status"] == "STALE":
            tagged = set(self._tagged(skill, v["domain"], ledger))
            fresh = [e for e in ledger.entries() if e["type"] == "RESOLUTION"
                     and e["seq"] > sk["status_ledger_seq"] and e["prediction_id"] in tagged]
            if not fresh:
                raise BookError("Kỹ năng STALE: cần kết quả mới gắn tên kỹ năng trước khi khôi phục.")
        decision = adjudicate(proposal, critique, adjudicator_session)  # ba phiên mới, độc lập
        score = self._base_score(v, ledger, policy)
        gate = skill_gate(score, decision, policy)
        watch = self._watch_failures(
            self._watch_score(skill, v, ledger, policy, sk.get("promoted_ledger_seq", -1)), policy)
        if not gate.passed or watch:
            raise BookError("Rollback bị từ chối — bản cũ rớt cổng/giám sát trên dữ liệu hiện có: "
                            + "; ".join((gate.reasons if not gate.passed else []) + watch))
        return self.chain.append({"type": "SKILL_STATUS", "skill": skill, "status": "PROMOTED",
                                  "version": to_version, "reasons": [f"ROLLBACK: {reason}"],
                                  "score": score.to_dict(), "decision": decision.to_dict(),
                                  "sessions": [proposal.session, critique.session,
                                               adjudicator_session],
                                  "ledger_seq": self._ledger_seq(ledger), "at": now_iso()})
