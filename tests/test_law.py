import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minhtri.handover import HandoverError, HandoverLog, check_law, law_sha256, validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def entry(law, **kw):
    e = {"session": "s", "provider": "claude", "role": "Thi công", "started_from": "abc",
         "law_sha256": law, "did": ["x"], "verified": ["y"], "open": [], "next": "z"}
    e.update(kw)
    return e


class TestLawLock(unittest.TestCase):
    def test_repo_law_matches_lock(self):
        self.assertEqual(check_law(ROOT)["sha256"], law_sha256(ROOT))

    def test_edited_law_detected(self):
        d = tempfile.mkdtemp()
        shutil.copy(os.path.join(ROOT, "LUAT_KIEN_TRUC_TOI_CAO.md"), d)
        os.makedirs(os.path.join(d, "brain"))
        shutil.copy(os.path.join(ROOT, "brain", "law.lock"), os.path.join(d, "brain"))
        with open(os.path.join(d, "LUAT_KIEN_TRUC_TOI_CAO.md"), "a", encoding="utf-8") as f:
            f.write("\nĐiều 15 — Bộ não được tự đăng video.\n")
        with self.assertRaises(HandoverError):
            check_law(d)


class TestHandover(unittest.TestCase):
    def test_validate(self):
        law = law_sha256(ROOT)
        validate(entry(law), law)
        for bad in (entry(law, role="Tự do"), entry(law, did=[]), entry(law, verified=[]),
                    entry("0" * 64), {k: v for k, v in entry(law).items() if k != "next"}):
            with self.assertRaises(HandoverError):
                validate(bad, law)

    def test_log_append_and_verify(self):
        law = law_sha256(ROOT)
        log = HandoverLog(os.path.join(tempfile.mkdtemp(), "h.jsonl"))
        log.add(entry(law, session="a"), law)
        log.add(entry(law, session="b"), law)
        self.assertEqual(log.last()["session"], "b")
        self.assertTrue(log.verify())


class TestLawAmendmentGate(unittest.TestCase):
    """Chương V: sửa luật mà không có ADR OWNER-APPROVED → CI đỏ."""

    def repo(self):
        d = tempfile.mkdtemp()
        for f in ("LUAT_KIEN_TRUC_TOI_CAO.md",):
            shutil.copy(os.path.join(ROOT, f), d)
        os.makedirs(os.path.join(d, "brain")); os.makedirs(os.path.join(d, "docs", "adr"))
        shutil.copy(os.path.join(ROOT, "brain", "law.lock"), os.path.join(d, "brain"))
        run = lambda *a: subprocess.run(a, cwd=d, check=True, capture_output=True)
        run("git", "init", "-q", "-b", "main")
        run("git", "add", "-A")
        run("git", "-c", "user.email=a@b", "-c", "user.name=t", "commit", "-qm", "base")
        base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()
        return d, run, base

    def amend(self, d, run, adr_text):
        with open(os.path.join(d, "LUAT_KIEN_TRUC_TOI_CAO.md"), "a", encoding="utf-8") as f:
            f.write("\nLàm rõ.\n")
        lock = json.load(open(os.path.join(d, "brain", "law.lock"), encoding="utf-8"))
        lock["sha256"] = law_sha256(d); lock["adr"] = "docs/adr/0002-x.md"
        json.dump(lock, open(os.path.join(d, "brain", "law.lock"), "w", encoding="utf-8"))
        if adr_text is not None:
            open(os.path.join(d, "docs", "adr", "0002-x.md"), "w", encoding="utf-8").write(adr_text)
        run("git", "add", "-A")
        run("git", "-c", "user.email=a@b", "-c", "user.name=t", "commit", "-qm", "amend")

    def check(self, d, base):
        return subprocess.run([sys.executable, os.path.join(ROOT, "tools", "check_law.py"), base],
                              cwd=d, capture_output=True, text=True).returncode

    def test_amend_without_adr_fails(self):
        d, run, base = self.repo()
        self.amend(d, run, None)
        self.assertEqual(self.check(d, base), 1)

    def test_amend_approval_without_source_fails(self):
        d, run, base = self.repo()
        self.amend(d, run, "# ADR 0002\nOWNER-APPROVED: 2026-10-01\n")
        self.assertEqual(self.check(d, base), 1)

    def test_constitution_edit_needs_adr(self):
        d, run, base = self.repo()
        open(os.path.join(d, "CONSTITUTION.md"), "w", encoding="utf-8").write("sửa lén\n")
        run("git", "add", "-A")
        run("git", "-c", "user.email=a@b", "-c", "user.name=t", "commit", "-qm", "c")
        self.assertEqual(self.check(d, base), 1)

    def edit_ch1(self, d, run, adr_text):
        p = os.path.join(d, "LUAT_KIEN_TRUC_TOI_CAO.md")
        t = open(p, encoding="utf-8").read().replace("Cơ hội thay đổi; **bộ não ở lại**.",
                                                     "Cơ hội thay đổi; bộ não thuộc về một AI.")
        open(p, "w", encoding="utf-8").write(t)
        self.amend(d, run, adr_text)

    def test_chapter_one_change_needs_clarify_line(self):
        d, run, base = self.repo()
        self.edit_ch1(d, run, "OWNER-APPROVED: 2026-10-01 — nguồn: chat\n")
        self.assertEqual(self.check(d, base), 1)

    def test_chapter_one_reversal_blocked(self):
        d, run, base = self.repo()
        self.edit_ch1(d, run, "OWNER-APPROVED: 2026-10-01 — nguồn: chat\nCHƯƠNG-I: ĐẢO NGƯỢC\n")
        self.assertEqual(self.check(d, base), 1)

    def test_chapter_one_clarify_passes(self):
        d, run, base = self.repo()
        self.edit_ch1(d, run, "OWNER-APPROVED: 2026-10-01 — nguồn: chat\nCHƯƠNG-I: LÀM RÕ — thử\n")
        self.assertEqual(self.check(d, base), 0)

    def test_amend_with_unapproved_adr_fails(self):
        d, run, base = self.repo()
        self.amend(d, run, "# ADR 0002\nChưa duyệt.\n")
        self.assertEqual(self.check(d, base), 1)

    def test_amend_with_owner_approved_adr_passes(self):
        d, run, base = self.repo()
        self.amend(d, run, "# ADR 0002\nOWNER-APPROVED: 2026-10-01 — nguồn: chat Owner\n")
        self.assertEqual(self.check(d, base), 0)


class TestHandoverGate(unittest.TestCase):
    """Điều 14: dòng bàn giao giả / cổ / trùng session / thiếu MỞ PHIÊN bị chặn."""

    def repo(self):
        d = tempfile.mkdtemp()
        shutil.copy(os.path.join(ROOT, "LUAT_KIEN_TRUC_TOI_CAO.md"), d)
        os.makedirs(os.path.join(d, "brain", "handover"))
        shutil.copy(os.path.join(ROOT, "brain", "law.lock"), os.path.join(d, "brain"))
        open(os.path.join(d, "brain", "handover", "log.jsonl"), "w").close()
        self.run_ = lambda *a: subprocess.run(a, cwd=d, check=True, capture_output=True)
        self.run_("git", "init", "-q", "-b", "main")
        self.commit(d, "c0")
        self.commit(d, "c1", touch="a.txt")
        base = self.head(d)
        self.run_("git", "checkout", "-qb", "f")
        return d, base

    def head(self, d):
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()

    def commit(self, d, msg, touch=None):
        if touch:
            open(os.path.join(d, touch), "a").write(msg)
        self.run_("git", "add", "-A")
        self.run_("git", "-c", "user.email=a@b", "-c", "user.name=t", "commit", "-qm", msg, "--allow-empty")

    def add_entry(self, d, started_from, session="s1"):
        log = HandoverLog(os.path.join(d, "brain", "handover", "log.jsonl"))
        law = law_sha256(ROOT)
        log.add(entry(law, session=session, started_from=started_from), law)

    def check(self, d, base, body="MỞ PHIÊN · provider: x"):
        env = dict(os.environ, PR_BODY=body)
        return subprocess.run([sys.executable, os.path.join(ROOT, "tools", "check_handover.py"), base],
                              cwd=d, capture_output=True, text=True, env=env).returncode

    def test_valid_entry_passes(self):
        d, base = self.repo()
        self.add_entry(d, base); self.commit(d, "w", touch="b.txt")
        self.assertEqual(self.check(d, base), 0)

    def test_old_started_from_rejected(self):
        d, base = self.repo()
        old = subprocess.run(["git", "rev-parse", "HEAD~1"], cwd=d, capture_output=True, text=True).stdout.strip()
        self.add_entry(d, old); self.commit(d, "w", touch="b.txt")
        self.assertEqual(self.check(d, base), 1)

    def test_missing_open_line_rejected(self):
        d, base = self.repo()
        self.add_entry(d, base); self.commit(d, "w", touch="b.txt")
        self.assertEqual(self.check(d, base, body="không có dòng mở phiên"), 1)

    def test_duplicate_session_rejected(self):
        d, base = self.repo()
        self.add_entry(d, base, session="dup"); self.add_entry(d, base, session="dup")
        self.commit(d, "w", touch="b.txt")
        self.assertEqual(self.check(d, base), 1)

    def test_law_amended_between_sessions_passes(self):
        # Chương V: luật sửa giữa hai phiên của cùng PR → dòng cũ giữ băm bản đã đọc, dòng cuối khớp bản mới
        d, base = self.repo()
        self.add_entry(d, base, session="s1"); self.commit(d, "w1")
        open(os.path.join(d, "LUAT_KIEN_TRUC_TOI_CAO.md"), "a", encoding="utf-8").write("\nsửa\n")
        law2 = law_sha256(d)
        HandoverLog(os.path.join(d, "brain", "handover", "log.jsonl")).add(
            entry(law2, session="s2", started_from=base), law2)
        self.commit(d, "w2")
        self.assertEqual(self.check(d, base), 0)

    def test_last_entry_must_match_current_law(self):
        d, base = self.repo()
        self.add_entry(d, base, session="s1"); self.commit(d, "w1")
        open(os.path.join(d, "LUAT_KIEN_TRUC_TOI_CAO.md"), "a", encoding="utf-8").write("\nsửa\n")
        self.commit(d, "w2")
        self.assertEqual(self.check(d, base), 1)

    def test_fake_law_hash_rejected(self):
        d, base = self.repo()
        log = HandoverLog(os.path.join(d, "brain", "handover", "log.jsonl"))
        log.add(entry("f" * 64, session="s1", started_from=base), "f" * 64)
        self.add_entry(d, base, session="s2"); self.commit(d, "w")
        self.assertEqual(self.check(d, base), 1)

    def test_branch_merged_main_keeps_old_fork_points(self):
        # nhánh PR gộp main (git merge main): dòng cũ mang điểm tách cũ, dòng cuối mang điểm tách mới
        d, base = self.repo()
        self.add_entry(d, base, session="s1"); self.commit(d, "w1")
        self.run_("git", "checkout", "-q", "main"); self.commit(d, "m1", touch="m.txt")
        base2 = self.head(d)
        self.run_("git", "checkout", "-q", "f")
        self.run_("git", "-c", "user.email=a@b", "-c", "user.name=t", "merge", "-q", "--no-edit", "main")
        self.add_entry(d, base2, session="s2"); self.commit(d, "w2")
        self.assertEqual(self.check(d, base2), 0)

    def test_merged_main_last_entry_needs_current_fork(self):
        d, base = self.repo()
        self.add_entry(d, base, session="s1"); self.commit(d, "w1")
        self.run_("git", "checkout", "-q", "main"); self.commit(d, "m1", touch="m.txt")
        base2 = self.head(d)
        self.run_("git", "checkout", "-q", "f")
        self.run_("git", "-c", "user.email=a@b", "-c", "user.name=t", "merge", "-q", "--no-edit", "main")
        self.add_entry(d, base, session="s2"); self.commit(d, "w2")  # phiên mới khai điểm tách cũ
        self.assertEqual(self.check(d, base2), 1)

    def test_no_entry_rejected(self):
        d, base = self.repo()
        self.commit(d, "w", touch="b.txt")
        self.assertEqual(self.check(d, base), 1)


if __name__ == "__main__":
    unittest.main()
