# SPS 粗测（trace off / debug 对比；阶段 3 基线数据点，供 architecture §8 VM/TM 参考）
import sys
import time

sys.path.insert(0, "src")

from riftsim.policies import RandomPolicy
from riftsim.runner import run_episode


def bench(level: str, n: int = 30) -> tuple[int, float]:
    steps = 0
    t0 = time.perf_counter()
    for seed in range(n):
        r = run_episode(RandomPolicy(seed * 2 + 1), RandomPolicy(seed * 2 + 2), seed,
                        trace_level=level, out_dir=None)
        steps += r.length_steps
    dt = time.perf_counter() - t0
    return steps, dt


for level in ("off", "debug"):
    s, dt = bench(level)
    print(f"{level:6s}: {s} decision-steps in {dt:.2f}s  SPS={s / dt:.0f}")
