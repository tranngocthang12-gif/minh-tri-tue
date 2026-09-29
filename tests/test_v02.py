import json
import os
import tempfile
import unittest

from minhtri import bench
from minhtri.epistemics import Claim, ClaimKind, EvidenceGrade
from minhtri.gates import GatePolicy
from minhtri.ledger import PredictionLedger
from minhtri.lessons import BookError, LessonBook
from minhtri.providers import ProviderRegistry
from minhtri.seats import Decision, Verdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tmpdir():
    return tempfile.mkdtemp()


def claim():
    return Claim("Mở đầu bằng câu hỏi giữ khán giả tốt hơn", ClaimKind.HYPOTHESIS,
                 EvidenceGrade.REAL_OUTCOME, 0.7)


def accept():
    return Decision(Verdict.ACCEPT, ["ok"], True)


class TestLessons(unittest.TestCase):
    def setUp(self):
        d = tmpdir()
        self.led = PredictionLedger(os.path.join(d, "l.jsonl"))
        self.book = LessonBook(os.path.join(d, "b.jsonl"))
        for i in range(5):
            self.led.register(f"p{i}", "yt", "q", "claude", probability=0.9)
            self.led.resolve(f"p{i}", True, "yt-analytics")
        self.ids = [f"p{i}" for i in range(5)]

    def test_lesson_needs_resolved_predictions(self):
        self.led.register("open", "yt", "q", "claude", probability=0.5)
        with self.assertRaises(BookError):
            self.book.add_lesson("L1", "yt", claim(), ["open"], self.led, "claude", "s1")
        with self.assertRaises(BookError):
            self.book.add_lesson("L1", "yt", claim(), [], self.led, "claude", "s1")

    def test_promote_then_suspend_then_rollback(self):
        self.book.add_lesson("L1", "yt", claim(), self.ids, self.led, "claude", "s1")
        self.book.propose_skill("hook-cau-hoi", ["L1"], "Mở đầu bằng một câu hỏi trong 5 giây đầu",
                                self.ids, "claude", "s1")
        r = self.book.try_promote("hook-cau-hoi", self.led, accept())
        self.assertEqual(r["status"], "PROMOTED")
        # thực tế mới phản bác → kiểm lại → đình chỉ
        for i in range(5, 12):
            self.led.register(f"p{i}", "yt", "q", "claude", probability=0.9)
            self.led.resolve(f"p{i}", False, "yt-analytics")
        self.book.propose_skill("hook-cau-hoi", ["L1"], "v2", self.ids + [f"p{i}" for i in range(5, 12)],
                                "claude", "s2")
        # v1 vẫn đang active; recheck trên v1 không có dự đoán mới → không đình chỉ
        self.assertIsNone(self.book.recheck("hook-cau-hoi", self.led))
        r2 = self.book.try_promote("hook-cau-hoi", self.led, accept())
        self.assertEqual(r2["status"], "REJECTED")
        st = self.book.state()["skills"]["hook-cau-hoi"]
        self.assertEqual(st["active_version"], 1)
        self.book.rollback("hook-cau-hoi", 1, "v2 rớt cổng")
        self.assertEqual(self.book.state()["skills"]["hook-cau-hoi"]["status"], "PROMOTED")
        self.assertTrue(self.book.verify())

    def test_recheck_suspends_failing_skill(self):
        self.book.add_lesson("L1", "yt", claim(), self.ids, self.led, "claude", "s1")
        ids = self.ids + ["x1", "x2", "x3", "x4", "x5", "x6"]
        for x in ids[5:]:
            self.led.register(x, "yt", "q", "claude", probability=0.9)
        self.book.propose_skill("s", ["L1"], "quy trình", ids, "claude", "s1")
        self.assertEqual(self.book.try_promote("s", self.led, accept())["status"], "PROMOTED")
        for x in ids[5:]:
            self.led.resolve(x, False, "yt-analytics")
        self.assertEqual(self.book.recheck("s", self.led)["status"], "SUSPENDED")

    def test_cannot_rollback_to_never_promoted(self):
        self.book.add_lesson("L1", "yt", claim(), self.ids, self.led, "claude", "s1")
        self.book.propose_skill("s", ["L1"], "q", self.ids, "claude", "s1")
        with self.assertRaises(BookError):
            self.book.rollback("s", 1, "x")


class TestBench(unittest.TestCase):
    def setUp(self):
        self.suite = bench.load(os.path.join(ROOT, "benchmarks", "tang1-core-v1.json"))
        self.key = {"suite": "x", "answers": {}}

    def test_suite_does_not_leak_answers(self):
        self.assertNotIn("answers", self.suite)
        self.assertEqual(len(self.suite["key_sha256"]), 64)

    def test_grading_and_seal(self):
        s = {"id": "t", "authors": ["claude"], "items": [
            {"id": "a", "task": "research", "type": "choice"},
            {"id": "b", "task": "critique", "type": "set"},
            {"id": "c", "task": "quant", "type": "number", "tolerance": 0.01}]}
        key = {"suite": "t", "answers": {"a": "FACT", "b": ["X", "Y"], "c": 3}}
        s["key_sha256"] = bench.key_hash(key)
        sc = bench.grade(s, key, {"a": "fact", "b": ["X"], "c": 3.001}, "gpt")
        self.assertEqual(sc["research"], 1.0)
        self.assertAlmostEqual(sc["critique"], 0.6667, places=3)
        self.assertEqual(sc["quant"], 1.0)
        with self.assertRaises(bench.BenchError):
            bench.grade(s, key, {}, "claude")          # tác giả đề không được thi
        bad = dict(key, answers=dict(key["answers"], a="OPINION"))
        with self.assertRaises(bench.BenchError):
            bench.grade(s, bad, {}, "gpt")             # sửa đáp án → băm lệch

    def test_record_into_registry(self):
        reg = ProviderRegistry(os.path.join(tmpdir(), "p.json"))
        reg.add("gpt", "m")
        bench.record(reg, "gpt", "t", {"quant": 1.0, "critique": 0.5})
        self.assertEqual(len(reg.data["providers"]["gpt"]["scores"]["quant"]), 1)


if __name__ == "__main__":
    unittest.main()
