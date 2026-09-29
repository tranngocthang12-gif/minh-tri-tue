"""CI: Luật Kiến trúc Tối cao (Chương IV, V).

- Băm luật phải khớp brain/law.lock.
- Nếu luật hoặc khoá đổi so với commit gốc → cùng PR phải THÊM một ADR mới trong docs/adr/
  có dòng 'OWNER-APPROVED: <yyyy-mm-dd>', và khoá phải trỏ tới ADR đó.
Dùng: python tools/check_law.py <base-ref>
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from minhtri.handover import HandoverError, check_law  # noqa: E402
from tools.check_append_only import resolve_base  # noqa: E402

LAW, LOCK = "LUAT_KIEN_TRUC_TOI_CAO.md", "brain/law.lock"
APPROVED = re.compile(r"^OWNER-APPROVED:\s*\d{4}-\d{2}-\d{2}", re.M)


def changed(base: str, status: str = "ACMRD") -> list:
    r = subprocess.run(["git", "diff", "--name-status", f"--diff-filter={status}", f"{base}...HEAD"],
                       capture_output=True, text=True, check=True)
    return [l.split("\t") for l in r.stdout.splitlines() if l.strip()]


def main(base) -> int:
    try:
        lock = check_law(".")
    except (HandoverError, FileNotFoundError) as e:
        print("LUẬT:", e); return 1
    print(f"Luật khớp khoá ({lock['sha256'][:8]}).")
    if not base:
        print("Không có commit gốc — chỉ kiểm khoá."); return 0
    files = changed(base)
    touched = {p[-1] for p in files}
    if not ({LAW, LOCK} & touched):
        print("PR không sửa luật."); return 0
    added_adr = [p[-1] for p in files if p[0] == "A" and p[-1].startswith("docs/adr/") and p[-1].endswith(".md")]
    ok = [f for f in added_adr if APPROVED.search(open(f, encoding="utf-8").read())]
    if not ok:
        print("LUẬT BỊ SỬA mà không có ADR mới mang dòng OWNER-APPROVED (Chương V)."); return 1
    if os.path.basename(lock.get("adr", "")) not in {os.path.basename(f) for f in ok}:
        print(f"brain/law.lock phải trỏ tới ADR mới: {', '.join(ok)}"); return 1
    print(f"Sửa luật hợp lệ theo Chương V: {', '.join(ok)}"); return 0


if __name__ == "__main__":
    sys.exit(main(resolve_base(sys.argv[1] if len(sys.argv) > 1 else "")))
