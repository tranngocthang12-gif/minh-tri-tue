"""NHÀ CUNG CẤP NHẬN THỨC — AI là nhân sự thay được, không phải bộ não.

- Tên provider được chuẩn hoá (claude-opus, anthropic → claude) để không lách luật bằng bí danh.
- Mỗi (provider, đề, việc) chỉ được ghi MỘT lần — thi lại cùng đề không thành mẫu mới.
- Champion cần ≥ min_samples ĐỀ KHÁC NHAU mỗi việc và phải hơn champion cũ ≥ margin.
"""
import json
import os
from statistics import mean
from typing import Dict, List, Optional

TASKS = ["research", "critique", "writing", "quant", "coding", "directing", "finance"]

CANONICAL = ("chatgpt", "claude", "gemini", "grok")
_ALIASES = {
    "chatgpt": ("chatgpt", "gpt", "openai", "o1", "o3", "o4"),
    "claude": ("claude", "anthropic"),
    "gemini": ("gemini", "google", "bard"),
    "grok": ("grok", "xai", "x.ai"),
}


class ProviderError(ValueError):
    pass


def canonical(name: str) -> str:
    n = name.strip().lower()
    for canon, prefixes in _ALIASES.items():
        if any(n == p or n.startswith(p + "-") or n.startswith(p + " ") or n.startswith(p)
               for p in prefixes):
            return canon
    raise ProviderError(f"Provider lạ '{name}'. Chỉ nhận: {', '.join(CANONICAL)}.")


class ProviderRegistry:
    def __init__(self, path: str, min_samples: int = 5, margin: float = 0.05):
        self.path, self.min_samples, self.margin = path, min_samples, margin
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {"providers": {}, "champions": {}}

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")

    def add(self, name: str, model: str) -> None:
        self.data["providers"].setdefault(canonical(name), {"model": model, "scores": {}, "failures": []})

    def record(self, name: str, task: str, score: float, benchmark_id: str) -> None:
        name = canonical(name)
        if task not in TASKS:
            raise ProviderError(f"Task lạ: {task}")
        if name not in self.data["providers"]:
            raise ProviderError(f"Chưa đăng ký provider {name}")
        if not 0.0 <= score <= 1.0:
            raise ProviderError("Điểm benchmark phải trong [0, 1].")
        rows = self.data["providers"][name]["scores"].setdefault(task, [])
        if any(r["benchmark"] == benchmark_id for r in rows):
            raise ProviderError(f"{name} đã có điểm {task} trên đề {benchmark_id} — không thi lại cùng đề.")
        rows.append({"score": score, "benchmark": benchmark_id})

    def _mean(self, name: str, task: str) -> Optional[float]:
        s = self.data["providers"][name]["scores"].get(task, [])
        distinct = {x["benchmark"] for x in s}
        return mean(x["score"] for x in s) if len(distinct) >= self.min_samples else None

    def elect(self, task: str) -> Dict:
        """Chọn champion. Challenger chỉ thay khi hơn champion ≥ margin."""
        ranked = sorted(((m, n) for n in self.data["providers"]
                         if (m := self._mean(n, task)) is not None), reverse=True)
        if not ranked:
            return {"task": task, "champion": None,
                    "reason": f"Chưa provider nào thi đủ {self.min_samples} đề khác nhau."}
        best_score, best = ranked[0]
        current = self.data["champions"].get(task)
        cur_score = self._mean(current, task) if current in self.data["providers"] else None
        if current and cur_score is not None and best != current and best_score - cur_score < self.margin:
            return {"task": task, "champion": current,
                    "reason": f"{best} hơn chưa đủ {self.margin} — giữ champion."}
        self.data["champions"][task] = best
        return {"task": task, "champion": best, "reason": f"Điểm TB {best_score:.3f}."}

    def roster(self) -> List[str]:
        return sorted(self.data["providers"])
