"""CI: PR sửa repo phải ghi thêm ít nhất một dòng sổ bàn giao hợp lệ (Điều 14).

Mỗi dòng mới: đủ trường, law_sha256 khớp luật hiện hành, started_from là tổ tiên của HEAD.
Dùng: python tools/check_handover.py <base-ref>
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from minhtri.handover import HandoverError, law_sha256, validate  # noqa: E402
from tools.check_append_only import resolve_base  # noqa: E402

LOG = "brain/handover/log.jsonl"


def lines_at(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return [] if r.returncode != 0 else [l for l in r.stdout.splitlines() if l.strip()]


def main(base) -> int:
    if not base:
        print("Không có commit gốc — bỏ qua."); return 0
    diff = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"],
                          capture_output=True, text=True, check=True).stdout.split()
    if not diff:
        print("Không có thay đổi."); return 0
    old = lines_at(base, LOG)
    with open(LOG, encoding="utf-8") as f:
        new = [l for l in f.read().splitlines() if l.strip()][len(old):]
    if not new:
        print("PR sửa repo nhưng KHÔNG ghi sổ bàn giao (BAN_GIAO.md phần C)."); return 1
    law = law_sha256(".")
    for line in new:
        e = json.loads(line)
        try:
            validate(e, law)
        except HandoverError as err:
            print(f"Dòng bàn giao {e.get('session')}: {err}"); return 1
        anc = subprocess.run(["git", "merge-base", "--is-ancestor", e["started_from"], "HEAD"])
        if anc.returncode != 0:
            print(f"started_from {e['started_from'][:12]} không phải tổ tiên của HEAD — phiên không mở từ main thật.")
            return 1
    print(f"Sổ bàn giao: {len(new)} dòng mới hợp lệ."); return 0


if __name__ == "__main__":
    sys.exit(main(resolve_base(sys.argv[1] if len(sys.argv) > 1 else "")))
