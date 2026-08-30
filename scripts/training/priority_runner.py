#!/usr/bin/env python3
"""
priority_runner.py
==================
Chạy có ưu tiên: GUMNet variants (proposed models) seed 42 trước,
rồi tới SOTA baselines seed 42, cuối cùng là tất cả seeds còn lại.
Output: model_checkpoint.pth + processor.pkl cho mỗi run.

Thứ tự ưu tiên:
  Phase 1: GUMNet variants  | seed=42  | all horizons
  Phase 2: SOTA baselines   | seed=42  | all horizons
  Phase 3: GUMNet variants  | other seeds | all horizons
  Phase 4: SOTA baselines   | other seeds | all horizons
"""
import os, sys, subprocess
from datetime import datetime

sys.path.insert(0, '.')
from config import GUM_NET_VARIANTS, ALL_SOTA_BASELINES, ALL_HORIZONS

TARGETS       = ['XANG', 'DAU']
WALKFORWARD   = 'results_v4/walkforward'
ALL_SEEDS     = [42, 123, 777, 2025, 9999]
GPU_CYCLE     = [3, 1, 2, 0]   # GPU 3 nhanh nhất, ưu tiên trước


def is_done(model, target, horizon, seed):
    p = os.path.join(WALKFORWARD, model, f'{target}_H{horizon}_seed{seed}', 'results.json')
    return os.path.exists(p)


def run_job(model, target, horizon, seed, gpu_id, job_num, total):
    log = f"logs_v4/priority_{model}_{target}_H{horizon}_seed{seed}.log"
    cmd = [
        'python3', 'scripts/train_unified.py',
        '--type', target,
        '--model', model,
        '--horizon', str(horizon),
        '--protocol', 'walkforward',
        '--seed', str(seed),
    ]
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = str(gpu_id)

    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] [{job_num:3d}/{total}] GPU{gpu_id} | {model:25s} | {target} | H{horizon:2d} | seed={seed}", flush=True)

    os.makedirs('logs_v4', exist_ok=True)
    with open(log, 'w') as lf:
        proc = subprocess.run(cmd, env=env, stdout=lf, stderr=lf)

    ckpt = os.path.join(WALKFORWARD, model, f'{target}_H{horizon}_seed{seed}', 'model_checkpoint.pth')
    pkl  = os.path.join(WALKFORWARD, model, f'{target}_H{horizon}_seed{seed}', 'processor.pkl')

    if proc.returncode == 0:
        ok_ckpt   = 'checkpoint=OK' if os.path.exists(ckpt) else 'checkpoint=MISSING'
        ok_scaler = 'scaler=OK'     if os.path.exists(pkl)  else 'scaler=MISSING'
        print(f"        Done | {ok_ckpt} | {ok_scaler}")
    else:
        print(f"        FAILED (rc={proc.returncode}) -> {log}")


# Build ordered job list
phases = [
    ("Phase 1: GUMNet seed=42",       GUM_NET_VARIANTS,  [42]),
    ("Phase 2: Baselines seed=42",     ALL_SOTA_BASELINES,[42]),
    ("Phase 3: GUMNet other seeds",    GUM_NET_VARIANTS,  [s for s in ALL_SEEDS if s != 42]),
    ("Phase 4: Baselines other seeds", ALL_SOTA_BASELINES,[s for s in ALL_SEEDS if s != 42]),
]

all_jobs = []
for phase_name, models, seeds in phases:
    for seed in seeds:
        for model in models:
            for target in TARGETS:
                for horizon in ALL_HORIZONS:
                    if not is_done(model, target, horizon, seed):
                        all_jobs.append((phase_name, model, target, horizon, seed))

total = len(all_jobs)
print(f"[{datetime.now():%Y-%m-%d %H:%M}] Priority Runner started")
print(f"Total pending jobs: {total}")
print()

# Print phase breakdown
from collections import Counter
phase_counts = Counter(p for p,m,t,h,s in all_jobs)
for phase, cnt in phase_counts.items():
    print(f"  {phase}: {cnt} jobs")
print()

if total == 0:
    print("All jobs already completed!")
    sys.exit(0)

for i, (phase_name, model, target, horizon, seed) in enumerate(all_jobs):
    gpu_id = GPU_CYCLE[i % len(GPU_CYCLE)]
    run_job(model, target, horizon, seed, gpu_id, i+1, total)

print()
print(f"[{datetime.now():%Y-%m-%d %H:%M}] All {total} priority jobs completed!")
