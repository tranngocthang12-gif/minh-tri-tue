"""Dòng lệnh MINH TRÍ TUỆ.  python -m minhtri.cli <lệnh>"""
import argparse
import json
import sys

from . import brain
from .domains import create_domain
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
    a = ap.parse_args(argv)

    led = PredictionLedger(brain.LEDGER)
    if a.cmd == "status":
        st = brain.load_state()
        st["ledger_entries"] = len(led.entries())
        print(json.dumps(st, ensure_ascii=False, indent=2))
    elif a.cmd == "verify":
        led.verify(); print("Sổ dự đoán: chuỗi băm nguyên vẹn.")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
