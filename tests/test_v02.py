import json
import os
import subprocess
import sys
import tempfile
import unittest

from minhtri import bench
from minhtri.chain import ChainError, HashChain
from minhtri.epistemics import Claim, ClaimKind, EvidenceGrade
from minhtri.gates import Level, level_from_evidence
from minhtri.ledger import LedgerError, PredictionLedger
from minhtri.lessons import BookError, LessonBook
from minhtri.providers import ProviderError, ProviderRegistry, canonical
from minhtri.seats import Critique, Objection, Proposal, SeatError, Severity

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tmp(name):
    return os.path.join(tempfile.mkdtemp(), name)


def claim():
    return Claim("Mở đầu bằng câu hỏi giữ khán giả tốt hơn", ClaimKind.HYPOTHESIS,
                 EvidenceGrade.REAL_OUTCOME, 0.7)


def seats(prop_session="s1", crit_session="s2"):
    p = Proposal("claude", prop_session, claim())
    c = Critique("gpt", crit_session,
                 [Objection("mùa vụ?", Severity.MAJOR, "ALT_EXPLANATION", answered=True)])
    return p, c


class Base(unittest.TestCase):
    def setUp(self):
        self.led = PredictionLedger(tmp("l.jsonl"))
        self.book = LessonBook(tmp("b.jsonl"))
        self.ids = []
        for i in range(5):
            self.led.register(f"p{i}", "yt", "q", "claude", probability=0.9)
            self.led.resolve(f"p{i}", True, "yt-analytics")
            self.ids.append(f"p{i}")
        self.book.add_lesson("L1", "yt", claim(), self.ids, self.led, "claude", "s1")

    def promote_v1(self, name="hook"):
        self.book.propose_skill(name, ["L1"], "Mở đầu bằng câu hỏi", self.ids, "claude", "s1")
        p, c = seats()
        return self.book.try_promote(name, self.led, p, c, "s3")


class TestSeatsInsidePromotion(Base):
    def test_fake_decision_impossible_same_session(self):          # Grok #1
        self.book.propose_skill("hook", ["L1"], "q", self.ids, "claude", "s1")
        p, c = seats("s1", "s1")
        with self.assertRaises(SeatError):
            self.book.try_promote("hook", self.led, p, c, "s3")

    def test_proposer_must_be_author_session(self):
        self.book.propose_skill("hook", ["L1"], "q", self.ids, "claude", "s1")
        p, c = seats("sX", "s2")
        with self.assertRaises(BookError):
            self.book.try_promote("hook", self.led, p, c, "s3")


class TestVersions(Base):
    def test_failed_v2_does_not_topple_active_v1(self):            # Grok #2
        self.assertEqual(self.promote_v1()["status"], "PROMOTED")
        for i in range(5, 12):
            self.led.register(f"p{i}", "yt", "q", "claude", probability=0.9)
            self.led.resolve(f"p{i}", False, "yt-analytics")
        bad = [f"p{i}" for i in range(5, 12)]
        self.book.add_lesson("L2", "yt", claim(), bad, self.led, "claude", "s4")
        self.book.propose_skill("hook", ["L1", "L2"], "v2", self.ids + bad, "claude", "s4")
        st = self.book.state()["skills"]["hook"]
        self.assertEqual(st["status"], "PROMOTED")                     # đề xuất v2 không reset
        self.assertIsNone(self.book.recheck("hook", self.led))         # v1 không có dự đoán mới gắn tên
        p, c = seats("s4", "s5")
        r = self.book.try_promote("hook", self.led, p, c, "s6")
        self.assertEqual(r["type"], "VERSION_REJECTED")
        st = self.book.state()["skills"]["hook"]
        self.assertEqual((st["status"], st["active_version"]), ("PROMOTED", 1))
        self.assertEqual(st["version_status"]["2"], "REJECTED")
        self.assertTrue(self.book.verify())


class TestPredictionScope(Base):
    def test_stray_or_empty_predictions_rejected(self):             # Grok #3
        self.led.register("easy", "yt", "q", "claude", probability=0.99)
        self.led.resolve("easy", True, "x")
        with self.assertRaises(BookError):
            self.book.propose_skill("s", ["L1"], "q", self.ids + ["easy"], "claude", "s1")
        with self.assertRaises(BookError):
            self.book.propose_skill("s", ["L1"], "q", [], "claude", "s1")

    def test_lesson_cross_domain_rejected(self):
        self.led.register("f1", "finance", "q", "claude", probability=0.5)
        self.led.resolve("f1", True, "x")
        with self.assertRaises(BookError):
            self.book.add_lesson("L9", "yt", claim(), ["f1"], self.led, "claude", "s1")


class TestRecheckAndRollback(Base):
    def fail_tagged(self, n=8):
        for i in range(n):
            self.led.register(f"t{i}", "yt", "q", "claude", probability=0.9, skill="hook")
            self.led.resolve(f"t{i}", False, "yt-analytics")

    def test_new_tagged_evidence_suspends(self):                     # Grok #7
        self.promote_v1()
        self.fail_tagged()
        self.assertEqual(self.book.recheck("hook", self.led)["status"], "SUSPENDED")

    def test_rollback_needs_gate_and_seats(self):                    # Grok #4
        self.promote_v1()
        self.fail_tagged()
        self.book.recheck("hook", self.led)
        p, c = seats("s7", "s8")
        with self.assertRaises(BookError):                           # rớt cổng → giữ SUSPENDED
            self.book.rollback("hook", 1, self.led, p, c, "s9", "muốn khôi phục")
        self.assertEqual(self.book.state()["skills"]["hook"]["status"], "SUSPENDED")
        p, c = seats("s7", "s7")
        with self.assertRaises(SeatError):
            self.book.rollback("hook", 1, self.led, p, c, "s9", "x")

    def test_cannot_rollback_to_never_promoted(self):
        self.book.propose_skill("s", ["L1"], "q", self.ids, "claude", "s1")
        p, c = seats("s7", "s8")
        with self.assertRaises(BookError):
            self.book.rollback("s", 1, self.led, p, c, "s9", "x")


class TestLedgerHardening(unittest.TestCase):
    def test_huge_range_counts_as_miss(self):                         # Grok #8
        led = PredictionLedger(tmp("l.jsonl"))
        led.register("w", "d", "q", "c", low=-1e18, high=1e18)
        led.resolve("w", 5, "x")
        self.assertEqual(led.score(max_rel_width=1.0).range_hit_rate, 0.0)
        with self.assertRaises(LedgerError):
            led.register("inf", "d", "q", "c", low=0, high=float("inf"))

    def test_late_resolution_flagged(self):
        led = PredictionLedger(tmp("l.jsonl"))
        led.register("a", "d", "q", "c", probability=0.5, resolve_by="2000-01-01")
        self.assertTrue(led.resolve("a", True, "x")["late"])


class TestChain(unittest.TestCase):                                   # Grok #10, #11
    def test_edit_middle_detected(self):
        path = tmp("c.jsonl")
        ch = HashChain(path)
        for i in range(3):
            ch.append({"i": i})
        lines = open(path, encoding="utf-8").read().splitlines()
        rec = json.loads(lines[1]); rec["i"] = 99
        lines[1] = json.dumps(rec)
        open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        with self.assertRaises(ChainError):
            ch.verify()

    def test_full_rewrite_caught_by_append_only_check(self):
        d = tempfile.mkdtemp()
        run = lambda *a: subprocess.run(a, cwd=d, check=True, capture_output=True)
        run("git", "init", "-q")
        os.makedirs(os.path.join(d, "brain/ledger")); os.makedirs(os.path.join(d, "brain/lessons"))
        book = os.path.join(d, "brain/ledger/predictions.jsonl")
        open(os.path.join(d, "brain/lessons/book.jsonl"), "w").close()
        PredictionLedger(book).register("a", "d", "q", "c", probability=0.9)
        run("git", "add", "-A"); run("git", "-c", "user.email=a@b", "-c", "user.name=t", "commit", "-qm", "base")
        os.remove(book)                                    # viết lại từ GENESIS, băm lại hợp lệ
        PredictionLedger(book).register("a", "d", "q", "c", probability=0.1)
        self.assertTrue(PredictionLedger(book).verify())  # tự kiểm vẫn xanh...
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools/check_append_only.py"), "HEAD"],
                           cwd=d, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)                  # ...nhưng CI bắt được


class TestBenchHardening(unittest.TestCase):
    def mini(self):
        s = {"id": "t", "authors": ["claude"], "author_sessions": ["sa"], "exposed_to": ["grok"],
             "items": [{"id": "a", "task": "research", "type": "choice"},
                       {"id": "b", "task": "critique", "type": "set"},
                       {"id": "c", "task": "quant", "type": "number", "tolerance": 0.01}]}
        key = {"suite": "t", "answers": {"a": "FACT", "b": {"required": ["X", "Y"], "optional": ["Z"]},
                                         "c": 3}}
        s["key_sha256"] = bench.key_hash(key)
        return s, key

    def test_optional_codes_not_penalized(self):                      # Grok #6
        s, key = self.mini()
        sc = bench.grade(s, key, {"a": "fact", "b": ["X", "Y", "Z"], "c": 3.001}, "gemini", "g1")
        self.assertEqual(sc, {"research": 1.0, "critique": 1.0, "quant": 1.0})
        sc = bench.grade(s, key, {"b": ["X", "W"]}, "gemini", "g1")
        self.assertAlmostEqual(sc["critique"], 0.5)

    def test_author_alias_exposed_and_session_blocked(self):         # Grok #9, exposure
        s, key = self.mini()
        for prov, sess in (("Claude-Opus", "x"), ("anthropic", "x"), ("grok-4", "x"), ("gemini", "sa"),
                           ("gemini", "")):
            with self.assertRaises((bench.BenchError, ProviderError)):
                bench.grade(s, key, {}, prov, sess)

    def test_key_missing_item_and_tamper(self):
        s, key = self.mini()
        partial = {"suite": "t", "answers": {"a": "FACT"}}
        s2 = dict(s, key_sha256=bench.key_hash(partial))
        with self.assertRaises(bench.BenchError):
            bench.grade(s2, partial, {}, "gemini", "g1")
        bad = {"suite": "t", "answers": dict(key["answers"], a="OPINION")}
        with self.assertRaises(bench.BenchError):
            bench.grade(s, bad, {}, "gemini", "g1")

    def test_leak_scan_nested(self):                                  # Grok #15
        self.assertTrue(bench.leaks({"items": [{"id": "a", "expected": 1}]}))
        real = bench.load(os.path.join(ROOT, "benchmarks", "tang1-core-v1.json"))
        self.assertEqual(bench.leaks(real), [])
        self.assertIn("grok", real["exposed_to"])

    def test_same_suite_not_counted_twice(self):                      # Grok #5
        reg = ProviderRegistry(tmp("p.json"), min_samples=2)
        reg.add("gpt", "m")
        bench.record(reg, "gpt", "t1", {"quant": 1.0})
        with self.assertRaises(ProviderError):
            bench.record(reg, "gpt", "t1", {"quant": 1.0})
        self.assertIsNone(reg.elect("quant")["champion"])            # 1 đề < 2 đề
        bench.record(reg, "chatgpt", "t2", {"quant": 1.0})
        self.assertEqual(reg.elect("quant")["champion"], "chatgpt")

    def test_canonical(self):
        self.assertEqual(canonical("GPT-5"), "chatgpt")
        with self.assertRaises(ProviderError):
            canonical("llama")


class TestLevels(unittest.TestCase):                                  # Grok #13
    def test_no_skipping_l2(self):
        led = PredictionLedger(tmp("l.jsonl"))
        s = led.score()
        self.assertEqual(level_from_evidence(3, 5, s, False, False), Level.L1_KNOWLEDGE)
        self.assertEqual(level_from_evidence(3, 5, s, False, False, explained_conditions=True),
                         Level.L3_PREDICTION)


if __name__ == "__main__":
    unittest.main()


class TestRound2(Base):
    """Phản biện Grok vòng 2: N1–N5 và ý 3, 8."""

    def test_tagged_predictions_never_help_promotion(self):           # N1 / ý 3
        led, book = self.led, self.book
        led.register("m0", "yt", "q", "claude", probability=0.9)
        led.resolve("m0", False, "x")                                  # bài học yếu: 1 dự đoán sai
        book.add_lesson("Lw", "yt", claim(), ["m0"], led, "claude", "s1")
        for i in range(6):                                             # dự đoán dễ, gắn tên
            led.register(f"e{i}", "yt", "q", "claude", probability=0.99, skill="weak")
            led.resolve(f"e{i}", True, "x")
        book.propose_skill("weak", ["Lw"], "q", ["m0"], "claude", "s1")
        p, c = seats()
        self.assertEqual(book.try_promote("weak", led, p, c, "s3")["type"], "VERSION_REJECTED")

    def test_no_cherry_picking_lesson_predictions(self):              # ý 3 (tập con)
        with self.assertRaises(BookError):
            self.book.propose_skill("s", ["L1"], "q", self.ids[:3], "claude", "s1")

    def test_silence_makes_skill_stale(self):                          # N2
        self.promote_v1()
        for i in range(20):                                            # miền vẫn chạy, kỹ năng im
            self.led.register(f"o{i}", "yt", "q", "claude", probability=0.6)
            self.led.resolve(f"o{i}", True, "x")
        self.assertEqual(self.book.recheck("hook", self.led)["status"], "STALE")
        p, c = seats("s7", "s8")
        with self.assertRaises(BookError):                             # thoát STALE cần bằng chứng mới
            self.book.rollback("hook", 1, self.led, p, c, "s9", "vẫn tốt")
        self.led.register("f1", "yt", "q", "claude", probability=0.9, skill="hook")
        self.led.resolve("f1", True, "x")
        self.assertEqual(self.book.rollback("hook", 1, self.led, p, c, "s9", "có kết quả mới")["status"],
                         "PROMOTED")

    def test_other_domain_does_not_make_stale(self):
        self.promote_v1()
        for i in range(25):
            self.led.register(f"x{i}", "finance", "q", "claude", probability=0.6)
            self.led.resolve(f"x{i}", True, "x")
        self.assertIsNone(self.book.recheck("hook", self.led))

    def test_late_counts_as_miss(self):                                # N3 / ý 8
        led = PredictionLedger(tmp("l.jsonl"))
        led.register("a", "d", "q", "c", probability=0.9, resolve_by="2000-01-01")
        led.resolve("a", True, "x")
        self.assertAlmostEqual(led.score().brier, 0.01)
        self.assertEqual(led.score(late_is_miss=True).brier, 1.0)

    def test_alias_needs_boundary(self):                               # N5
        with self.assertRaises(ProviderError):
            canonical("grokking")
        self.assertEqual(canonical("grok-4"), "grok")


class TestAppendOnlyBase(unittest.TestCase):                           # N4
    def test_zero_before_uses_merge_base(self):
        d = tempfile.mkdtemp()
        run = lambda *a: subprocess.run(a, cwd=d, check=True, capture_output=True)
        git = ["git", "-c", "user.email=a@b", "-c", "user.name=t"]
        run("git", "init", "-q", "-b", "main")
        os.makedirs(os.path.join(d, "brain/ledger")); os.makedirs(os.path.join(d, "brain/lessons"))
        book = os.path.join(d, "brain/ledger/predictions.jsonl")
        open(os.path.join(d, "brain/lessons/book.jsonl"), "w").close()
        PredictionLedger(book).register("a", "d", "q", "c", probability=0.9)
        run("git", "add", "-A"); run(*git, "commit", "-qm", "base")
        run("git", "checkout", "-qb", "feature")
        os.remove(book)
        PredictionLedger(book).register("a", "d", "q", "c", probability=0.1)
        run("git", "add", "-A"); run(*git, "commit", "-qm", "rewrite")
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools/check_append_only.py"), "0" * 40],
                           cwd=d, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout)
