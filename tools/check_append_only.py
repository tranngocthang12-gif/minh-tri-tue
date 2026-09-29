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


def resolve_base(ref: str):
    """Commit gốc để so. Push nhánh mới (before toàn số 0) → so với merge-base của main."""
    if ref and set(ref) != {"0"}:
        return ref
    for main in ("origin/main", "main"):
        r = subprocess.run(["git", "merge-base", "HEAD", main], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            base = r.stdout.strip()
            head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
            if base != head:
                return base
            parent = subprocess.run(["git", "rev-parse", "HEAD~1"], capture_output=True, text=True)
            return parent.stdout.strip() if parent.returncode == 0 else None
    return None


if __name__ == "__main__":
    base = resolve_base(sys.argv[1] if len(sys.argv) > 1 else "")
    if not base:
        print("Không có commit gốc để so (commit đầu tiên của repo) — bỏ qua.")
        sys.exit(0)
    print(f"So với commit gốc {base[:12]}")
    sys.exit(main(base))
