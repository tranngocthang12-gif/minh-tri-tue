"""Dòng lệnh MINH TRÍ TUỆ.  python -m minhtri.cli <lệnh>"""
import argparse
import json
import os
import sys

from . import brain
from . import bench
from .domains import create_domain
from .gates import GatePolicy
from .handover import HandoverLog, check_law
from .lessons import LessonBook
from .ledger import PredictionLedger
from .providers import ProviderRegistry


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="minhtri")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("verify")
    d = sub.add_parser("domain"); d.add_argument("name"); d.add_argument("purpose")
    p = sub.add_parser("predict")
    for a in ("id", "domain", "question", "provider"):
        p.add_argument(a)
    p.add_argument("--p", type=float); p.add_argument("--low", type=float)
    p.add_argument("--high", type=float); p.add_argument("--by")
    r = sub.add_parser("resolve"); r.add_argument("id"); r.add_argument("outcome"); r.add_argument("source")
    s = sub.add_parser("score"); s.add_argument("--domain"); s.add_argument("--provider")
    s.add_argument("--max-rel-width", type=float, default=GatePolicy().max_rel_width,
                   help="khoảng rộng hơn tính là trượt (mặc định theo cổng kỹ năng)")
    c = sub.add_parser("champion"); c.add_argument("task")
    sub.add_parser("skills")
    sub.add_parser("handover")
    ha = sub.add_parser("handover-add"); ha.add_argument("entry")
    be = sub.add_parser("bench-export"); be.add_argument("suite")
    bg = sub.add_parser("bench-grade")
    for x in ("suite", "key", "answers", "provider", "session"):
        bg.add_argument(x)
    bk = sub.add_parser("bench-check-key"); bk.add_argument("suite"); bk.add_argument("key")
    a = ap.parse_args(argv)

    led = PredictionLedger(brain.LEDGER)
    if a.cmd == "status":
        st = brain.load_state()
        st["ledger_entries"] = len(led.entries())
        print(json.dumps(st, ensure_ascii=False, indent=2))
    elif a.cmd == "verify":
        led.verify(); print("Sổ dự đoán: chuỗi băm nguyên vẹn.")
        LessonBook(brain.LESSONS).verify(); print("Sổ bài học & kỹ năng: chuỗi băm nguyên vẹn.")
        for f in sorted(os.listdir(brain.BENCHMARKS)):
            if f.endswith(".json"):
                sui = bench.load(os.path.join(brain.BENCHMARKS, f))
                if len(str(sui.get("key_sha256", ""))) != 64:
                    raise bench.BenchError(f"{f}: thiếu key_sha256 hợp lệ.")
                if bench.leaks(sui):
                    raise bench.BenchError(f"{f}: có trường mang đáp án: {bench.leaks(sui)}")
        print("Đề benchmark: không lộ đáp án.")
        check_law(brain.ROOT); print("Luật Kiến trúc Tối cao: khớp khoá băm.")
        HandoverLog(brain.HANDOVER).verify(); print("Sổ bàn giao: chuỗi băm nguyên vẹn.")
    elif a.cmd == "domain":
        print("Đã mở miền:", create_domain(brain.DOMAINS, a.name, a.purpose))
    elif a.cmd == "predict":
        e = led.register(a.id, a.domain, a.question, a.provider, probability=a.p,
                         low=a.low, high=a.high, resolve_by=a.by)
        print("Đã đăng ký:", e["id"], e["hash"][:12])
    elif a.cmd == "resolve":
        o = a.outcome
        outcome = True if o.lower() in ("true", "yes", "1") else False if o.lower() in ("false", "no", "0") else float(o)
        e = led.resolve(a.id, outcome, a.source)
        print("Đã chấm:", e["prediction_id"], e["hash"][:12])
    elif a.cmd == "score":
        sc = led.score(a.domain, a.provider, max_rel_width=a.max_rel_width, late_is_miss=True)
        print(json.dumps(sc.to_dict(), ensure_ascii=False, indent=2))
    elif a.cmd == "champion":
        reg = ProviderRegistry(brain.PROVIDERS)
        res = reg.elect(a.task); reg.save()
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif a.cmd == "skills":
        st = LessonBook(brain.LESSONS).state()
        view = {k: {"status": v["status"], "active_version": v["active_version"],
                    "versions": len(v["versions"])} for k, v in st["skills"].items()}
        print(json.dumps({"lessons": len(st["lessons"]), "skills": view}, ensure_ascii=False, indent=2))
    elif a.cmd == "bench-export":
        print(bench.export_prompt(bench.load(a.suite)))
    elif a.cmd == "bench-grade":
        suite = bench.load(a.suite)
        scores = bench.grade(suite, bench.load(a.key), bench.load(a.answers), a.provider, a.session)
        reg = ProviderRegistry(brain.PROVIDERS)
        bench.record(reg, a.provider, suite["id"], scores); reg.save()
        print(json.dumps({"provider": a.provider, "suite": suite["id"], "scores": scores},
                         ensure_ascii=False, indent=2))
    elif a.cmd == "handover":
        lock = check_law(brain.ROOT)
        log = HandoverLog(brain.HANDOVER); log.verify()
        last = log.last()
        print(f"LUẬT: khớp khoá · phiên bản {lock['version']} · băm {lock['sha256'][:8]} · {lock['adr']}")
        print("BÀN GIAO CUỐI:" if last else "BÀN GIAO CUỐI: (chưa có)")
        if last:
            print(json.dumps({k: v for k, v in last.items() if k not in ("hash", "prev_hash")},
                             ensure_ascii=False, indent=2))
        print("→ Làm tiếp BAN_GIAO.md phần A (xác minh remote, tuyên bố MỞ PHIÊN).")
    elif a.cmd == "handover-add":
        lock = check_law(brain.ROOT)
        with open(a.entry, encoding="utf-8") as f:
            e = HandoverLog(brain.HANDOVER).add(json.load(f), lock["sha256"])
        print("Đã ghi bàn giao:", e["session"], e["hash"][:12])
    elif a.cmd == "bench-check-key":
        bench.check_key(bench.load(a.suite), bench.load(a.key))
        print("Đáp án khớp băm niêm phong của đề.")
    return 0


def run() -> int:
    try:
        return main()
    except (ValueError, FileExistsError, FileNotFoundError, KeyError) as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(run())
