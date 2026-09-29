"""Định vị bộ não chuẩn trên đĩa (thư mục brain/ trong repo GitHub)."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAIN = os.path.join(ROOT, "brain")
LEDGER = os.path.join(BRAIN, "ledger", "predictions.jsonl")
LESSONS = os.path.join(BRAIN, "lessons", "book.jsonl")
PROVIDERS = os.path.join(BRAIN, "providers.json")
DOMAINS = os.path.join(BRAIN, "domains")
STATE = os.path.join(BRAIN, "state.json")
BENCHMARKS = os.path.join(ROOT, "benchmarks")


def load_state() -> dict:
    with open(STATE, encoding="utf-8") as f:
        return json.load(f)
