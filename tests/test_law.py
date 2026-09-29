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

    def test_amend_with_unapproved_adr_fails(self):
        d, run, base = self.repo()
        self.amend(d, run, "# ADR 0002\nChưa duyệt.\n")
        self.assertEqual(self.check(d, base), 1)

    def test_amend_with_owner_approved_adr_passes(self):
        d, run, base = self.repo()
        self.amend(d, run, "# ADR 0002\nOWNER-APPROVED: 2026-10-01\n")
        self.assertEqual(self.check(d, base), 0)


if __name__ == "__main__":
    unittest.main()
