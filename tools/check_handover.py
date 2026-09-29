"""CI: sổ bàn giao (Điều 12, 14).

- Thay đổi (PR hoặc push vào main) phải ghi thêm ≥ 1 dòng sổ bàn giao.
- Sổ phải nguyên chuỗi băm.
- Mỗi dòng mới: đủ trường, law_sha256 khớp luật hiện hành, `session` chưa từng dùng,
  `started_from` = đúng điểm tách nhánh khỏi main (merge-base) — không được lấy commit cổ bất kỳ.
- Với PR: mô tả PR (biến môi trường PR_BODY) phải có dòng bắt đầu bằng "MỞ PHIÊN ·".
Dùng: python tools/check_handover.py <base-ref>
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from minhtri.chain import ChainError  # noqa: E402
from minhtri.handover import HandoverError, HandoverLog, law_sha256, validate  # noqa: E402
from tools.check_append_only import resolve_base  # noqa: E402

LOG = "brain/handover/log.jsonl"


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True)


def lines_at(ref, path):
    r = git("show", f"{ref}:{path}")
    return [] if r.returncode != 0 else [l for l in r.stdout.splitlines() if l.strip()]


def main(base) -> int:
    if not base:
        print("Không có commit gốc — bỏ qua."); return 0
    if not git("diff", "--name-only", f"{base}...HEAD").stdout.split():
        print("Không có thay đổi."); return 0
    body = os.environ.get("PR_BODY")
    if body is not None and not any(l.strip().startswith("MỞ PHIÊN ·") for l in body.splitlines()):
        print("Mô tả PR thiếu dòng 'MỞ PHIÊN · …' (BAN_GIAO.md phần A.4)."); return 1
    try:
        HandoverLog(LOG).verify()
    except ChainError as e:
        print("Sổ bàn giao gãy chuỗi:", e); return 1
    old = lines_at(base, LOG)
    with open(LOG, encoding="utf-8") as f:
        new = [l for l in f.read().splitlines() if l.strip()][len(old):]
    if not new:
        print("Thay đổi repo nhưng KHÔNG ghi sổ bàn giao (BAN_GIAO.md phần C)."); return 1
    fork = git("merge-base", base, "HEAD").stdout.strip()
    used = {json.loads(l)["session"] for l in old}
    law = law_sha256(".")
    for line in new:
        e = json.loads(line)
        try:
            validate(e, law)
        except HandoverError as err:
            print(f"Dòng bàn giao {e.get('session')}: {err}"); return 1
        if e["session"] in used:
            print(f"Session '{e['session']}' đã dùng trong sổ — mỗi phiên một mã."); return 1
        used.add(e["session"])
        if os.environ.get("EVENT") == "push":
            # push vào main (merge): phiên phải mở từ một commit đã có trên main trước lần push này
            if git("merge-base", "--is-ancestor", e["started_from"], base).returncode != 0:
                print(f"started_from {e['started_from'][:12]} không nằm trong lịch sử main trước push."); return 1
        elif e["started_from"] != fork:
            print(f"started_from {e['started_from'][:12]} ≠ điểm tách nhánh {fork[:12]} — phiên không mở từ main thật.")
            return 1
    print(f"Sổ bàn giao: {len(new)} dòng mới hợp lệ."); return 0


if __name__ == "__main__":
    sys.exit(main(resolve_base(sys.argv[1] if len(sys.argv) > 1 else "")))
