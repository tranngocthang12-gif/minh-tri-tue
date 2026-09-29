import json
import os
import tempfile
import unittest

from minhtri.domains import create_domain
from minhtri.epistemics import Claim, ClaimKind, EpistemicError, EvidenceGrade
from minhtri.focus import Candidate, choose
from minhtri.gates import GatePolicy, skill_gate
from minhtri.inquiry import Inquiry, InquiryError, Stage
from minhtri.ledger import LedgerError, PredictionLedger
from minhtri.providers import ProviderRegistry
from minhtri.seats import (Critique, Objection, Proposal, SeatError, Severity,
                           Verdict, adjudicate)


def tmp(name):
    return os.path.join(tempfile.mkdtemp(), name)


class TestEpistemics(unittest.TestCase):
    def test_confidence_capped_by_evidence(self):
        with self.assertRaises(EpistemicError):
            Claim("A gây ra B", ClaimKind.HYPOTHESIS, EvidenceGrade.ANECDOTE, 0.9).validate()
        Claim("A có thể gây ra B", ClaimKind.HYPOTHESIS, EvidenceGrade.ANECDOTE, 0.4).validate()

    def test_unknown_has_no_confidence(self):
        Claim("Chưa biết", ClaimKind.UNKNOWN).validate()
        with self.assertRaises(EpistemicError):
            Claim("Chưa biết", ClaimKind.UNKNOWN, confidence=0.5).validate()

    def test_fact_needs_sources(self):
        with self.assertRaises(EpistemicError):
            Claim("X", ClaimKind.FACT, EvidenceGrade.REPLICATED, 0.7).validate()


class TestLedger(unittest.TestCase):
    def test_register_resolve_score_verify(self):
        led = PredictionLedger(tmp("l.jsonl"))
        led.register("p1", "youtube", "CTR > 5%?", "claude", probability=0.8)
        led.register("p2", "youtube", "Views 48h", "gpt", low=100, high=500)
        led.resolve("p1", True, "yt-analytics")
        led.resolve("p2", 300, "yt-analytics")
        s = led.score()
        self.assertEqual(s.resolved, 2)
        self.assertAlmostEqual(s.brier, 0.04)
        self.assertEqual(s.range_hit_rate, 1.0)
        self.assertTrue(led.verify())

    def test_cannot_resolve_unregistered_or_twice(self):
        led = PredictionLedger(tmp("l.jsonl"))
        with self.assertRaises(LedgerError):
            led.resolve("ghost", True, "x")
        led.register("p1", "d", "q", "claude", probability=0.5)
        led.resolve("p1", False, "x")
        with self.assertRaises(LedgerError):
            led.resolve("p1", True, "x")

    def test_tamper_detected(self):
        path = tmp("l.jsonl")
        led = PredictionLedger(path)
        led.register("p1", "d", "q", "claude", probability=0.9)
        led.register("p2", "d", "q", "claude", probability=0.1)
        lines = open(path, encoding="utf-8").read().splitlines()
        rec = json.loads(lines[0]); rec["probability"] = 0.1
        lines[0] = json.dumps(rec, ensure_ascii=False)
        open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        with self.assertRaises(LedgerError):
            led.verify()


class TestInquiry(unittest.TestCase):
    def test_order_enforced(self):
        q = Inquiry("kiếm tiền YouTube", "youtube")
        with self.assertRaises(InquiryError):
            q.fill(Stage.PATH, {"steps": [], "first_cheap_test": "", "kill_criteria": ["x"]})

    def test_correlation_is_not_cause(self):
        q = Inquiry("x", "d")
        q.fill(Stage.REALITY, {"current_state": "a", "undesired_state": "b", "known": [],
                               "unknown": ["c"], "limits": [], "risks": [], "cost_of_no_change": "d"})
        with self.assertRaises(InquiryError):
            q.fill(Stage.CONDITIONS, {"factors": [{"role": "CAUSE", "basis": "CORRELATION_ONLY"}]})


class TestSeats(unittest.TestCase):
    def claim(self, grade=EvidenceGrade.EXPERIMENTAL, conf=0.8):
        return Claim("Thumbnail B tăng CTR", ClaimKind.HYPOTHESIS, grade, conf)

    def test_same_session_forbidden(self):
        p = Proposal("claude", "s1", self.claim())
        c = Critique("claude", "s1", [Objection("x", Severity.MINOR, "ASSUMPTION")])
        with self.assertRaises(SeatError):
            adjudicate(p, c, "s3")

    def test_counterevidence_rejects(self):
        p = Proposal("claude", "s1", self.claim())
        c = Critique("gpt", "s2", [Objection("A/B cho kết quả ngược", Severity.BLOCKING, "COUNTEREVIDENCE")])
        self.assertEqual(adjudicate(p, c, "s3").verdict, Verdict.REJECT)

    def test_weak_evidence_needs_test(self):
        p = Proposal("claude", "s1", self.claim(EvidenceGrade.ANECDOTE, 0.4))
        c = Critique("gpt", "s2", [Objection("mẫu nhỏ", Severity.MINOR, "ASSUMPTION")])
        self.assertEqual(adjudicate(p, c, "s3").verdict, Verdict.NEEDS_TEST)

    def test_accept(self):
        p = Proposal("claude", "s1", self.claim())
        c = Critique("gpt", "s2", [Objection("mùa vụ?", Severity.MAJOR, "ALT_EXPLANATION", answered=True)])
        self.assertEqual(adjudicate(p, c, "s3").verdict, Verdict.ACCEPT)


class TestGate(unittest.TestCase):
    def test_gate_blocks_without_outcomes(self):
        led = PredictionLedger(tmp("l.jsonl"))
        r = skill_gate(led.score(), None, GatePolicy())
        self.assertFalse(r.passed)


class TestProviders(unittest.TestCase):
    def test_champion_needs_margin(self):
        reg = ProviderRegistry(tmp("p.json"), min_samples=2, margin=0.05)
        for n in ("claude", "gpt"):
            reg.add(n, "m")
        for i, s in enumerate((0.70, 0.72)):
            reg.record("claude", "critique", s, f"a{i}")
        self.assertEqual(reg.elect("critique")["champion"], "claude")
        for i, s in enumerate((0.73, 0.74)):
            reg.record("gpt", "critique", s, f"b{i}")
        self.assertEqual(reg.elect("critique")["champion"], "claude")  # hơn chưa đủ margin
        for i, s in enumerate((0.95, 0.95)):
            reg.record("gpt", "critique", s, f"c{i}")
        self.assertEqual(reg.elect("critique")["champion"], "chatgpt")


class TestFocusAndDomain(unittest.TestCase):
    def test_wait_when_nothing_worth_doing(self):
        r = choose([Candidate("x", "DEVELOP", 1, 0.1, 10, True)])
        self.assertEqual(r["decision"], "WAIT")

    def test_domain_starts_unknown(self):
        root = tempfile.mkdtemp()
        d = create_domain(root, "YouTube", "kiếm tiền")
        doc = json.load(open(os.path.join(d, "domain.json"), encoding="utf-8"))
        self.assertTrue(all(v["status"] == "UNKNOWN" for v in doc["questions"].values()))


if __name__ == "__main__":
    unittest.main()
