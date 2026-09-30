"""Ghế 2 tự động — gửi mô tả PR + diff cho Grok, đăng "KẾT QUẢ PHẢN BIỆN" lên PR.

Chạy trong GitHub Action (.github/workflows/ghe2-grok.yml), bằng bản trên `main`:
    python -m minhtri.tools.ghe2_grok

Biến môi trường:
    XAI_API_KEY        khóa xAI (chỉ đọc từ Secret, không bao giờ in ra)
    GITHUB_TOKEN       token của Action (pull-requests: write)
    GITHUB_REPOSITORY  owner/repo
    PR_NUMBER          số PR
    GITHUB_RUN_ID      mã lần chạy → session: gh-action-<run_id>
    GROK_MODEL         model Grok (mặc định grok-4)

Chỉ đăng comment. Không merge, không đổi mã, không gửi gì ngoài nội dung PR
(Điều 1, Điều 2). Lỗi API → comment ngắn và thoát mã 0 (không chặn CI).
Chỉ dùng thư viện chuẩn + `requests`; `requests` nạp muộn để test chạy không cần nó.
"""
import json
import os
import sys

XAI_URL = "https://api.x.ai/v1/chat/completions"
GITHUB_API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
DEFAULT_MODEL = "grok-4"
TEMPERATURE = 0.2
DIFF_LIMIT = 60000
SKIP_LABEL = "skip-ghe2"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROMPT_PATH = os.path.join(ROOT, "docs", "reviews", "LOI_NHAC_GHE2.md")
TRUNCATED_NOTE = "⚠ diff đã cắt"

LAW_FILES = ("CONSTITUTION.md", "CONTRIBUTING.md", "ARCHITECTURE.md")
# tệp luật báo cho Grok có/không trên head PR (Grok không đọc được repo)
SUPREME_LAWS = ("LUAT_KIEN_TRUC_TOI_CAO.md", "CONSTITUTION.md")
COMMENT_LIMIT = 65000  # GitHub giới hạn comment 65.536 ký tự


def priority(path):
    """Hạng ưu tiên khi cắt diff: nhỏ hơn = giữ trước."""
    name = path.rsplit("/", 1)[-1]
    if name in LAW_FILES or name.upper().startswith("LUAT"):
        return 0
    if "adr" in path.lower().split("/") or name.upper().startswith("ADR"):
        return 1
    if path.startswith("minhtri/"):
        return 2
    if path.startswith("brain/"):
        return 3
    return 4


def file_block(f):
    patch = f.get("patch")
    head = f"diff -- {f['filename']} ({f.get('status', '?')}, +{f.get('additions', 0)} -{f.get('deletions', 0)})\n"
    if patch is None:
        return head + "(không có patch: tệp nhị phân hoặc quá lớn)\n"
    return head + patch + "\n"


def truncate_diff(files, limit=DIFF_LIMIT):
    """Ghép diff theo thứ tự ưu tiên, tổng ≤ limit ký tự.

    Trả (text, truncated). Nếu phải cắt, text kết thúc bằng dòng
    "⚠ diff đã cắt" kèm danh sách tệp bị cắt/bỏ; dòng này nằm trong limit.
    """
    ordered = sorted(enumerate(files), key=lambda p: (priority(p[1]["filename"]), p[0]))
    blocks = [(f["filename"], file_block(f)) for _, f in ordered]
    full = "".join(b for _, b in blocks)
    if len(full) <= limit:
        return full, False

    def note(cut, dropped):
        parts = [f"\n{TRUNCATED_NOTE} (giới hạn {limit} ký tự)."]
        if cut:
            parts.append(f" Cắt dở: {cut}.")
        if dropped:
            parts.append(" Bỏ hẳn: " + ", ".join(dropped) + ".")
        return "".join(parts) + "\n"

    names = [n for n, _ in blocks]
    reserve = len(note(max(names, key=len), names))  # chỗ cho dòng ghi chú xấu nhất
    budget = max(limit - reserve, 0)
    out, used, cut, dropped = [], 0, None, []
    for name, block in blocks:
        if cut is not None or used >= budget:
            dropped.append(name)
            continue
        if used + len(block) <= budget:
            out.append(block)
            used += len(block)
        else:
            out.append(block[: budget - used] + "\n")
            used = budget
            cut = name
    text = "".join(out) + note(cut, dropped)
    return text[:limit], True


def comment_header(pr_number, run_id, sha, model):
    return (f"KẾT QUẢ PHẢN BIỆN — PR #{pr_number} — provider: grok · "
            f"session: gh-action-{run_id} · head: {sha} · model: {model}")


def build_comment(pr_number, run_id, sha, model, reply, usage=None):
    """Dòng đầu cố định + nguyên văn trả lời của Grok (+ ghi chú token ẩn)."""
    header = comment_header(pr_number, run_id, sha, model) + "\n\n"
    reply = reply.strip()
    room = COMMENT_LIMIT - len(header) - 200
    if len(reply) > room:
        reply = reply[:room] + "\n\n⚠ trả lời Grok bị cắt do giới hạn độ dài comment GitHub"
    body = header + reply + "\n"
    if usage:
        body += "\n<!-- ghe2-usage: " + json.dumps(usage, ensure_ascii=False) + " -->\n"
    return body


def build_error_comment(code):
    return f"Ghế 2 tự động lỗi: {code}, không có phán quyết"


def law_status_lines(present):
    """present: {tên tệp: True/False} → dòng báo tệp luật có/thiếu trên head."""
    return [f"- {name}: {'có' if ok else 'chưa có tệp luật trên nhánh này'}" for name, ok in present.items()]


def build_user_message(pr, files, diff_text, truncated, laws=None):
    lines = [
        f"PHẢN BIỆN PR #{pr['number']}",
        f"Tiêu đề: {pr.get('title', '')}",
        f"Nhánh: {pr.get('head', {}).get('ref', '?')} → {pr.get('base', {}).get('ref', '?')}",
        f"Head: {pr.get('head', {}).get('sha', '?')}",
        "",
        "## Mô tả PR",
        (pr.get("body") or "(trống)").strip(),
        "",
        "## Tệp đổi",
    ]
    lines += [f"- {f['filename']} ({f.get('status', '?')}, +{f.get('additions', 0)} -{f.get('deletions', 0)})"
              for f in files]
    if laws is not None:
        lines += ["", "## Tệp luật trên nhánh này"] + law_status_lines(laws)
    lines += ["", "## Diff" + (f" ({TRUNCATED_NOTE})" if truncated else ""), diff_text]
    return "\n".join(lines)


def should_skip(pr):
    """Bỏ qua PR do bot/Action tạo hoặc có nhãn skip-ghe2. Trả lý do hoặc None."""
    user = pr.get("user") or {}
    if user.get("type") == "Bot" or user.get("login", "").endswith("[bot]"):
        return f"PR do bot tạo ({user.get('login')})"
    if any(l.get("name") == SKIP_LABEL for l in pr.get("labels") or []):
        return f"PR có nhãn {SKIP_LABEL}"
    return None


class GrokError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def call_grok(api_key, model, system_prompt, user_message, post=None, timeout=600):
    """Gọi xAI chat completions. Trả (nội dung, usage). Lỗi → GrokError(mã)."""
    if post is None:
        import requests
        post = requests.post
    try:
        r = post(XAI_URL,
                 headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                 json={"model": model, "temperature": TEMPERATURE,
                       "messages": [{"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_message}]},
                 timeout=timeout)
    except Exception as e:  # mạng, hết giờ — không in chi tiết có thể chứa header
        raise GrokError(type(e).__name__) from None
    if r.status_code != 200:
        raise GrokError(f"HTTP {r.status_code}")
    try:
        data = r.json()
        content = data["choices"][0]["message"]["content"]
    except Exception:
        raise GrokError("phản hồi không đọc được") from None
    if not content or not content.strip():
        raise GrokError("trả lời rỗng")
    return content, data.get("usage")


class GitHub:
    def __init__(self, token, repo, session=None):
        if session is None:
            import requests
            session = requests.Session()
        self.s = session
        self.s.headers.update({"Authorization": f"Bearer {token}",
                               "Accept": "application/vnd.github+json",
                               "X-GitHub-Api-Version": "2022-11-28"})
        self.base = f"{GITHUB_API}/repos/{repo}"

    def _get(self, path, **params):
        r = self.s.get(self.base + path, params=params, timeout=60)
        r.raise_for_status()
        return r.json()

    def pr(self, n):
        return self._get(f"/pulls/{n}")

    def files(self, n):
        out, page = [], 1
        while True:
            batch = self._get(f"/pulls/{n}/files", per_page=100, page=page)
            out += batch
            if len(batch) < 100 or page >= 30:  # GitHub trả tối đa 3000 tệp
                return out
            page += 1

    def exists(self, path, ref):
        r = self.s.get(f"{self.base}/contents/{path}", params={"ref": ref}, timeout=60)
        if r.status_code == 404:
            return False
        r.raise_for_status()
        return True

    def comment(self, n, body):
        r = self.s.post(f"{self.base}/issues/{n}/comments", json={"body": body}, timeout=60)
        r.raise_for_status()
        return r.json().get("html_url")


def main(env=None, gh=None, post=None):
    env = os.environ if env is None else env
    n = int(env["PR_NUMBER"])
    run_id = env.get("GITHUB_RUN_ID", "local")
    model = env.get("GROK_MODEL") or DEFAULT_MODEL
    gh = gh or GitHub(env["GITHUB_TOKEN"], env["GITHUB_REPOSITORY"])

    pr = gh.pr(n)
    reason = should_skip(pr)
    if reason:
        print(f"Bỏ qua: {reason}")
        return 0
    sha = pr["head"]["sha"]
    api_key = env.get("XAI_API_KEY")
    if not api_key:
        url = gh.comment(n, build_error_comment("thiếu XAI_API_KEY"))
        print(f"Thiếu XAI_API_KEY. Comment: {url}")
        return 0

    files = gh.files(n)
    diff_text, truncated = truncate_diff(files)
    with open(PROMPT_PATH, encoding="utf-8") as fh:
        system_prompt = fh.read()
    laws = {name: gh.exists(name, sha) for name in SUPREME_LAWS}
    user_message = build_user_message(pr, files, diff_text, truncated, laws)
    print(f"PR #{n} head {sha} · {len(files)} tệp · diff {len(diff_text)} ký tự"
          f"{' (đã cắt)' if truncated else ''} · model {model}")

    try:
        reply, usage = call_grok(api_key, model, system_prompt, user_message, post=post)
    except GrokError as e:
        url = gh.comment(n, build_error_comment(e.code))
        print(f"Grok lỗi: {e.code}. Comment: {url}")
        return 0

    print("usage: " + json.dumps(usage or {}, ensure_ascii=False))
    url = gh.comment(n, build_comment(n, run_id, sha, model, reply, usage))
    print(f"Đã đăng: {url}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # không chặn CI; không in chi tiết có thể lộ header
        print(f"Ghế 2 tự động lỗi: {type(e).__name__}")
        sys.exit(0)
