import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minhtri.tools import ghe2_grok as g


def f(name, patch, status="modified"):
    return {"filename": name, "status": status, "additions": 1, "deletions": 0, "patch": patch}


class FakeResp:
    def __init__(self, status, data=None):
        self.status_code, self._data = status, data

    def json(self):
        if self._data is None:
            raise ValueError("không phải JSON")
        return self._data


class FakeGitHub:
    def __init__(self, pr, files):
        self._pr, self._files, self.comments = pr, files, []
        self.present = {"CONSTITUTION.md"}
        self.history = []

    def pr(self, n):
        return self._pr

    def exists(self, path, ref):
        return path in self.present

    def files(self, n):
        return self._files

    def pr_comments(self, n):
        return self.history

    def comment(self, n, body):
        self.comments.append(body)
        return f"https://github.com/x/y/pull/{n}#issuecomment-{len(self.comments)}"


def pr(**kw):
    base = {"number": 7, "title": "t", "body": "provider: claude", "user": {"login": "owner", "type": "User"},
            "labels": [], "head": {"sha": "abc123", "ref": "feat"}, "base": {"ref": "main"}}
    base.update(kw)
    return base


ENV = {"PR_NUMBER": "7", "GITHUB_RUN_ID": "42", "XAI_API_KEY": "xai-bi-mat", "GROK_MODEL": ""}


class TestTruncate(unittest.TestCase):
    def test_small_diff_untouched(self):
        text, cut = g.truncate_diff([f("a.py", "+x")], limit=1000)
        self.assertFalse(cut)
        self.assertIn("+x", text)
        self.assertNotIn(g.TRUNCATED_NOTE, text)

    def test_cut_respects_limit_and_marks(self):
        files = [f(f"docs/f{i}.md", "+" + "y" * 5000) for i in range(30)]
        text, cut = g.truncate_diff(files, limit=60000)
        self.assertTrue(cut)
        self.assertLessEqual(len(text), 60000)
        self.assertIn(g.TRUNCATED_NOTE, text)
        self.assertIn("Bỏ hẳn:", text)

    def test_priority_law_adr_core_brain_first(self):
        files = [f("docs/other.md", "+" + "o" * 3000), f("brain/state.json", "+b"),
                 f("minhtri/x.py", "+m"), f("docs/adr/ADR-001.md", "+a"), f("CONSTITUTION.md", "+c")]
        text, cut = g.truncate_diff(files, limit=2000)
        self.assertTrue(cut)
        order = [text.index(n) for n in ("CONSTITUTION.md", "ADR-001.md", "minhtri/x.py", "brain/state.json")]
        self.assertEqual(order, sorted(order))
        self.assertIn("docs/other.md", text.split(g.TRUNCATED_NOTE)[1])  # tệp thường bị cắt

    def test_missing_patch_noted(self):
        text, _ = g.truncate_diff([{"filename": "img.png", "status": "added"}])
        self.assertIn("không có patch", text)


class TestComment(unittest.TestCase):
    def test_header_and_verbatim_reply(self):
        reply = "KẾT QUẢ PHẢN BIỆN — PR #7 — provider: grok\n1. …\nPHÁN QUYẾT: NEEDS_TEST — x"
        body = g.build_comment(7, "42", "abc123", "grok-4", reply, {"total_tokens": 10})
        first = body.splitlines()[0]
        self.assertEqual(first, "KẾT QUẢ PHẢN BIỆN — PR #7 — provider: grok · session: gh-action-42 · "
                                "head: abc123 · model: grok-4")
        self.assertIn(reply, body)
        self.assertIn("ghe2-usage", body)

    def test_long_reply_capped(self):
        body = g.build_comment(7, "42", "abc", "grok-4", "x" * 100000)
        self.assertLessEqual(len(body), g.COMMENT_LIMIT)
        self.assertIn("bị cắt", body)

    def test_error_comment(self):
        self.assertEqual(g.build_error_comment("HTTP 401"), "Ghế 2 tự động lỗi: HTTP 401, không có phán quyết")


class TestHistory(unittest.TestCase):
    def test_history_capped_keeps_newest(self):
        cs = [{"user": {"login": "u"}, "created_at": str(i), "body": f"c{i} " + "z" * 1000} for i in range(50)]
        text = g.format_history(cs, limit=5000)
        self.assertLessEqual(len(text), 5000 + 200)
        self.assertIn(g.HISTORY_CUT_NOTE, text)
        self.assertIn("c49 ", text)
        self.assertNotIn("c0 ", text)

    def test_strip_usage(self):
        self.assertEqual(g.strip_usage("a\n\n<!-- ghe2-usage: {} -->\n"), "a")
        self.assertEqual(g.strip_usage("không có"), "không có")


class TestMain(unittest.TestCase):
    def run_main(self, post, pr_obj=None, env=None):
        gh = FakeGitHub(pr_obj or pr(), [f("minhtri/x.py", "+m")])
        rc = g.main(env=dict(ENV, **(env or {})), gh=gh, post=post)
        return rc, gh.comments

    def test_success_posts_review_with_default_model(self):
        sent = {}

        def post(url, headers, json, timeout):
            sent.update(url=url, headers=headers, json=json)
            return FakeResp(200, {"choices": [{"message": {"content": "PHÁN QUYẾT: ACCEPT — ok"}}],
                                  "usage": {"prompt_tokens": 5, "completion_tokens": 3}})

        rc, comments = self.run_main(post)
        self.assertEqual(rc, 0)
        self.assertEqual(sent["url"], g.XAI_URL)
        self.assertEqual(sent["json"]["model"], "grok-4")
        self.assertEqual(sent["json"]["temperature"], 0.2)
        self.assertIn("không có quyền đọc thêm", sent["json"]["messages"][0]["content"])
        user = sent["json"]["messages"][1]["content"]
        self.assertIn("+m", user)
        self.assertIn("- LUAT_KIEN_TRUC_TOI_CAO.md: chưa có tệp luật trên nhánh này", user)
        self.assertIn("- CONSTITUTION.md: có", user)
        self.assertIn("chưa có tệp luật trên nhánh này", sent["json"]["messages"][0]["content"])
        self.assertTrue(comments[0].startswith("KẾT QUẢ PHẢN BIỆN — PR #7 — provider: grok"))
        self.assertIn("PHÁN QUYẾT: ACCEPT", comments[0])

    def test_model_from_env(self):
        seen = []
        post = lambda url, headers, json, timeout: seen.append(json["model"]) or FakeResp(
            200, {"choices": [{"message": {"content": "x"}}]})
        self.run_main(post, env={"GROK_MODEL": "grok-3-mini"})
        self.assertEqual(seen, ["grok-3-mini"])

    def test_api_error_short_comment_exit0_no_key_leak(self):
        rc, comments = self.run_main(lambda *a, **k: FakeResp(401))
        self.assertEqual(rc, 0)
        self.assertEqual(comments, ["Ghế 2 tự động lỗi: HTTP 401, không có phán quyết"])
        self.assertNotIn("xai-bi-mat", comments[0])

    def test_http_400_temperature_rejected(self):
        # Grok phản biện lần 2: server xAI từ chối temperature → HTTP 400
        sent = {}

        def post(url, headers, json, timeout):
            sent.update(json=json)
            return FakeResp(400, {"error": "temperature is not supported (Bearer xai-bi-mat)"})

        rc, comments = self.run_main(post)
        self.assertEqual(rc, 0)
        self.assertEqual(sent["json"]["temperature"], g.TEMPERATURE)
        self.assertEqual(comments, ["Ghế 2 tự động lỗi: HTTP 400, không có phán quyết"])
        self.assertNotIn("xai-bi-mat", comments[0])
        self.assertNotIn("PHÁN QUYẾT:", comments[0])

    def test_previous_comments_sent_to_grok(self):
        sent = {}

        def post(url, headers, json, timeout):
            sent.update(json=json)
            return FakeResp(200, {"choices": [{"message": {"content": "PHÁN QUYẾT: ACCEPT — ok"}}]})

        gh = FakeGitHub(pr(), [f("minhtri/x.py", "+m")])
        gh.history = [
            {"user": {"login": "github-actions[bot]"}, "created_at": "t1",
             "body": "KẾT QUẢ PHẢN BIỆN — PR #7 — provider: grok\n6. temperature\n<!-- ghe2-usage: {\"x\": 1} -->"},
            {"user": {"login": "owner"}, "created_at": "t2",
             "body": "GHẾ 1 TRẢ LỜI PHẢN BIỆN — 6a BÁC BẰNG DỮ LIỆU: HTTP 200"},
        ]
        g.main(env=dict(ENV), gh=gh, post=post)
        user = sent["json"]["messages"][1]["content"]
        self.assertIn("## Comment trước đó trên PR", user)
        self.assertLess(user.index("provider: grok\n6. temperature"), user.index("GHẾ 1 TRẢ LỜI PHẢN BIỆN"))
        self.assertNotIn("ghe2-usage", user)
        self.assertLess(user.index("## Comment trước đó"), user.index("## Diff"))
        self.assertIn("Điểm đã được trả lời có bằng chứng thì không nhắc lại.",
                      sent["json"]["messages"][0]["content"])

    def test_no_previous_comments(self):
        sent = {}
        post = lambda url, headers, json, timeout: sent.update(json=json) or FakeResp(
            200, {"choices": [{"message": {"content": "x"}}]})
        self.run_main(post)
        self.assertIn("## Comment trước đó trên PR (cũ → mới)\n(chưa có)", sent["json"]["messages"][1]["content"])

    def test_network_error(self):
        def post(*a, **k):
            raise TimeoutError("Bearer xai-bi-mat")
        rc, comments = self.run_main(post)
        self.assertEqual(rc, 0)
        self.assertEqual(comments, ["Ghế 2 tự động lỗi: TimeoutError, không có phán quyết"])

    def test_skip_label_and_bot(self):
        boom = lambda *a, **k: self.fail("không được gọi Grok")
        for p in (pr(labels=[{"name": "skip-ghe2"}]), pr(user={"login": "github-actions[bot]", "type": "Bot"})):
            rc, comments = self.run_main(boom, pr_obj=p)
            self.assertEqual((rc, comments), (0, []))

    def test_dispatch_skip_label_and_bot_before_any_call(self):
        # workflow_dispatch không qua điều kiện `if` của job → script phải tự chặn
        class NoCall(FakeGitHub):
            def files(self, n):
                raise AssertionError("không được đọc diff")
        for p in (pr(labels=[{"name": "skip-ghe2"}]), pr(user={"login": "x[bot]", "type": "Bot"})):
            gh = NoCall(p, [])
            self.assertEqual(g.main(env=dict(ENV), gh=gh, post=lambda *a, **k: self.fail("gọi Grok")), 0)
            self.assertEqual(gh.comments, [])

    def test_missing_key(self):
        rc, comments = self.run_main(lambda *a, **k: self.fail("không gọi"), env={"XAI_API_KEY": ""})
        self.assertEqual(rc, 0)
        self.assertIn("thiếu XAI_API_KEY", comments[0])


if __name__ == "__main__":
    unittest.main()
