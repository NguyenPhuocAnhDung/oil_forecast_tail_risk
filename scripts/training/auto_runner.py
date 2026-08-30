#!/usr/bin/env python3
"""
auto_runner.py — Chạy experiments theo đúng thứ tự SEED
=========================================================
Thứ tự: seed=42 ALL → seed=123 ALL → seed=777 ALL → seed=2025 ALL → seed=9999 ALL
Mỗi seed: chờ TẤT CẢ jobs của seed đó xong mới chạy seed tiếp theo
VRAM policy: chừa 3GB/GPU, sử dụng tối đa phần còn lại
"""
import os, sys, re, subprocess, time, threading, queue as qmod
from datetime import datetime

sys.path.insert(0, '.')
from config import GUM_NET_VARIANTS, ALL_SOTA_BASELINES, ALL_HORIZONS, SEEDS

VRAM_RESERVE_MB = 3072
GPU_TOTAL_MB    = 15360
WALKFORWARD     = 'results_v4/walkforward'
LOGS            = 'logs_v4'
TARGETS         = ['XANG', 'DAU']
POLL_INTERVAL   = 30

HEAVY_MODELS = {'GUMNet_Adaptive','GUMNet_MoE_Sparse','GUMNet_Fusion',
                'GUMNet_Diffusion','GUMNet_Mamba','GUMNet_RL','BiMamba'}
MEDIUM_MODELS = set(GUM_NET_VARIANTS) - HEAVY_MODELS

def vram_needed(model):
    if model in HEAVY_MODELS: return 3200
    if model in MEDIUM_MODELS: return 2800
    return 2000

def is_done(model, target, horizon, seed):
    p = os.path.join(WALKFORWARD, model, f'{target}_H{horizon}_seed{seed}', 'results.json')
    return os.path.exists(p)

def get_running_set():
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    running = set()
    for line in result.stdout.split('\n'):
        if 'train_unified' not in line or 'grep' in line: continue
        m=re.search(r'--model (\S+)',line); t=re.search(r'--type (\S+)',line)
        h=re.search(r'--horizon (\S+)',line); s=re.search(r'--seed (\S+)',line)
        if m and t and h and s:
            running.add((m.group(1), t.group(1), int(h.group(1)), int(s.group(1))))
    return running

def get_gpu_free_vram():
    result = subprocess.run(
        ['nvidia-smi','--query-gpu=index,memory.free','--format=csv,noheader,nounits'],
        capture_output=True, text=True)
    vram = {}
    for line in result.stdout.strip().split('\n'):
        parts = line.split(',')
        if len(parts) == 2:
            vram[int(parts[0].strip())] = int(parts[1].strip())
    return vram

def launch_job(model, target, horizon, seed, gpu_id):
    log = os.path.join(LOGS, f'auto_{model}_{target}_H{horizon}_s{seed}.log')
    cmd = ['python3', 'scripts/train_unified.py',
           '--type', target, '--model', model,
           '--horizon', str(horizon), '--protocol', 'walkforward', '--seed', str(seed)]
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
    os.makedirs(LOGS, exist_ok=True)
    proc = subprocess.Popen(cmd, env=env,
                            stdout=open(log,'w'), stderr=subprocess.STDOUT)
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] GPU{gpu_id} >> {model:25s}|{target}|H{horizon:2d}|s={seed}|PID={proc.pid}", flush=True)

def fill_gpu_jobs(seed, all_models):
    """Fill all GPUs with jobs for this seed, respecting VRAM budget."""
    running_set = get_running_set()
    jobs = []
    for model in all_models:
        for target in TARGETS:
            for horizon in ALL_HORIZONS:
                if not is_done(model, target, horizon, seed) and \
                   (model, target, horizon, seed) not in running_set:
                    jobs.append((model, target, horizon))
    if not jobs:
        return 0
    jobs.sort(key=lambda x: x[2])  # light horizons first
    
    # Launch as many as possible right now
    vram = get_gpu_free_vram()
    launched_count = 0
    for model, target, horizon in jobs:
        needed = vram_needed(model)
        # Find GPU with the most free VRAM
        best_gpu = max(vram, key=vram.get)
        if vram[best_gpu] >= needed + VRAM_RESERVE_MB:
            launch_job(model, target, horizon, seed, best_gpu)
            vram[best_gpu] = max(0, vram[best_gpu] - needed)
            launched_count += 1
            time.sleep(1) # Subtle delay to avoid rate-limiting/overloading
    return launched_count

def wait_for_seed_complete(seed, all_models):
    """Poll until ALL jobs for this seed are done. Launch orphaned/pending jobs continuously."""
    ts0 = datetime.now()
    while True:
        pending, running_set = [], get_running_set()
        for model in all_models:
            for target in TARGETS:
                for horizon in ALL_HORIZONS:
                    if not is_done(model, target, horizon, seed):
                        pending.append((model, target, horizon))
        if not pending:
            elapsed = int((datetime.now()-ts0).total_seconds()//60)
            print(f"\n[{datetime.now():%H:%M:%S}] ✅ seed={seed} COMPLETE in {elapsed}min\n", flush=True)
            return
            
        still_run = [(m,t,h) for m,t,h in pending if (m,t,h,seed) in running_set]
        orphans   = [(m,t,h) for m,t,h in pending if (m,t,h,seed) not in running_set]
        ts = datetime.now().strftime('%H:%M:%S')
        print(f"[{ts}] seed={seed}: {len(pending)} remain | {len(still_run)} running | {len(orphans)} pending", flush=True)
        
        # If there are pending (unstarted) jobs, aggressively try to push them to GPUs with VRAM > 3GB
        if orphans:
            vram = get_gpu_free_vram()
            for model, target, horizon in orphans:
                needed = vram_needed(model)
                best = max(vram, key=vram.get)
                if vram[best] >= needed + VRAM_RESERVE_MB:
                    launch_job(model, target, horizon, seed, best)
                    vram[best] = max(0, vram[best] - needed)
                    # Update running set immediately
                    running_set.add((model, target, horizon, seed))
        time.sleep(POLL_INTERVAL)


# ─── MAIN ───────────────────────────────────────────────────────────────────
ALL_MODELS = list(GUM_NET_VARIANTS) + list(ALL_SOTA_BASELINES)
SEED_ORDER = [42, 123, 777, 2025, 9999]

print(f"\n{'='*65}")
print(f"  AUTO RUNNER v2 — Strict seed-by-seed ordering")
print(f"  {' -> '.join(f'seed={s}' for s in SEED_ORDER)}")
print(f"  VRAM buffer: {VRAM_RESERVE_MB//1024}GB per GPU")
print(f"{'='*65}\n")

for seed in SEED_ORDER:
    print(f"\n{'─'*65}")
    print(f"  STARTING seed={seed} — checking what needs to run...")
    print(f"{'─'*65}")
    n = fill_gpu_jobs(seed, ALL_MODELS)
    print(f"  Launched {n} new jobs for seed={seed}")
    wait_for_seed_complete(seed, ALL_MODELS)

print(f"\n{'='*65}")
print(f"  FINISHED: ALL {len(SEED_ORDER)} seeds x {len(ALL_MODELS)} models COMPLETE!")
print(f"{'='*65}\n")
