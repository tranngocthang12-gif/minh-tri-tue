"""CI: sổ chỉ-ghi-thêm — mọi dòng cũ ở commit gốc phải còn nguyên, đúng thứ tự, ở đầu tệp.

Chặn kiểu viết lại toàn bộ sổ từ GENESIS rồi băm lại (verify() vẫn xanh nếu chỉ tự kiểm).
Dùng: python tools/check_append_only.py <base-ref>
"""
import subprocess
import sys

BOOKS = ["brain/ledger/predictions.jsonl", "brain/lessons/book.jsonl"]


def old_lines(ref: str, path: str):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return None if r.returncode != 0 else [l for l in r.stdout.splitlines() if l.strip()]


def main(ref: str) -> int:
    bad = 0
    for path in BOOKS:
        old = old_lines(ref, path)
        if old is None:
            print(f"{path}: chưa có ở {ref} — bỏ qua.")
            continue
        with open(path, encoding="utf-8") as f:
            new = [l for l in f.read().splitlines() if l.strip()]
        if new[:len(old)] != old:
            print(f"{path}: DÒNG CŨ BỊ SỬA/XÓA so với {ref}.")
            bad += 1
        else:
            print(f"{path}: giữ nguyên {len(old)} dòng cũ, thêm {len(new) - len(old)} dòng.")
    return 1 if bad else 0


if __name__ == "__main__":
    ref = sys.argv[1] if len(sys.argv) > 1 else ""
    if not ref or set(ref) == {"0"}:
        print("Không có commit gốc để so — bỏ qua.")
        sys.exit(0)
    sys.exit(main(ref))
