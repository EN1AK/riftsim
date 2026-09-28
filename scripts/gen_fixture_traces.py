# 产出阶段 4 回放器用 fixture trace（runs/fixtures/*.jsonl）：
# 覆盖几种代表性对局形态，供 VM-1 加载与一致性复验（T-0131 流程）。
import sys
from pathlib import Path

sys.path.insert(0, "src")

from riftsim.policies import EndTurnPolicy, RandomPolicy
from riftsim.replay import trace_replay_check
from riftsim.runner import run_episode

OUT = Path("runs/fixtures")
OUT.mkdir(parents=True, exist_ok=True)

CASES = [
    ("random-debug-11", RandomPolicy(1), RandomPolicy(2), 11, "debug"),
    ("random-summary-23", RandomPolicy(3), RandomPolicy(4), 23, "summary"),
    ("random-summary-42", RandomPolicy(5), RandomPolicy(6), 42, "summary"),
    ("endturn-debug-7", EndTurnPolicy(), EndTurnPolicy(), 7, "debug"),
]

for label, pa, pb, seed, level in CASES:
    r = run_episode(pa, pb, seed, trace_level=level, out_dir=OUT)
    chk = trace_replay_check(r.trace_path)
    ok = chk["final_hash_ok"] and chk["winner"] == chk["footer_winner"]
    print(
        f"{label}: match={r.match_id} term={r.termination} winner={r.winner} "
        f"steps={r.length_steps} scores={r.final_scores} replay_ok={ok}"
    )
    assert ok, f"replay validation failed for {label}"
print("fixture traces OK ->", OUT)
