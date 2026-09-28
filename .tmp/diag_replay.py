# 诊断：seed=11 跑局出 trace，再逐决策步重放并对比 after_state_hash 分叉点
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")

from riftsim import engine, legality
from riftsim.policies import RandomPolicy
from riftsim.replay import action_from_digest
from riftsim.runner import run_episode
from riftsim.snapshot import state_hash

out = Path(".tmp/diag_traces")
out.mkdir(exist_ok=True)
r = run_episode(RandomPolicy(1), RandomPolicy(2), 11, trace_level="debug", out_dir=out)
recs = [json.loads(x) for x in (out / f"{r.match_id}.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]

state = engine.reset(11, None)
h0 = state_hash(state)
print("initial hash:", h0[:16])
mismatch = 0
for rec in recs:
    if rec.get("type") != "decision":
        continue
    chosen = rec["chosen_action_id"]
    sid = rec["step_id"]
    engine.step(state, action_from_digest(chosen))
    h = state_hash(state)
    # 找该 step 的事件 after hash（debug 等级有事件记录）
    evs = [e for e in recs if e.get("type") == "event" and e.get("step_id") == sid]
    traced_after = evs[-1]["after_state_hash"] if evs else None
    if traced_after and h != traced_after:
        mismatch += 1
        print(f"MISMATCH step={sid} replay={h[:16]} traced={traced_after[:16]} chosen={chosen[:80]}")
        if mismatch >= 3:
            break
foot = recs[-1]
print("final replay:", state_hash(state)[:16], " footer:", foot["final_state_hash"][:16])
