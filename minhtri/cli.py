"""Dòng lệnh MINH TRÍ TUỆ.  python -m minhtri.cli <lệnh>"""
import argparse
import json
import os
import sys

from . import brain
from . import bench
from .domains import create_domain
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
    c = sub.add_parser("champion"); c.add_argument("task")
    sub.add_parser("skills")
    be = sub.add_parser("bench-export"); be.add_argument("suite")
    bg = sub.add_parser("bench-grade")
    for x in ("suite", "key", "answers", "provider"):
        bg.add_argument(x)
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
                assert len(sui["key_sha256"]) == 64 and "answers" not in sui, f
        print("Đề benchmark: không lộ đáp án.")
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
        print(json.dumps(led.score(a.domain, a.provider).to_dict(), ensure_ascii=False, indent=2))
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
        scores = bench.grade(suite, bench.load(a.key), bench.load(a.answers), a.provider)
        reg = ProviderRegistry(brain.PROVIDERS)
        bench.record(reg, a.provider, suite["id"], scores); reg.save()
        print(json.dumps({"provider": a.provider, "suite": suite["id"], "scores": scores},
                         ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
