#!/usr/bin/env python3
"""
scripts/smart_fill_scheduler.py
================================
GPU GAP FILLER — "Bon Chen" Scheduler (Kimi + Antigravity)
===========================================================

Tự động phát hiện khoảng trống VRAM trên mỗi GPU và liên tục
"bon chen" các jobs còn thiếu vào những khoảng trống đó.

Chiến lược:
  - Poll VRAM mỗi POLL_INTERVAL giây
  - Mỗi GPU có N slot (configurable) cho concurrent jobs
  - Dispatch job từ hàng đợi khi GPU đủ VRAM
  - Resume-aware: skip completed jobs
  - Priority: short horizons first (H1 < H3 < H5 ...) để kết quả sớm nhất

Usage:
  python scripts/smart_fill_scheduler.py --gpus 0,3 --slots 2
  python scripts/smart_fill_scheduler.py --gpus 0,1,2,3 --slots 1
  python scripts/smart_fill_scheduler.py --gpus 0,3 --dry-run
  python scripts/smart_fill_scheduler.py --gpus 0,3 --filter-paradigm GUMNet
"""

import os, sys, re, time, queue, argparse, threading, subprocess, json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from config import (
    SOTA_TAXONOMY_REGISTRY, GUM_NET_VARIANTS, ALL_HORIZONS,
    ALL_SOTA_BASELINES, SEEDS,
)

GREEN  = "\033[92m"; RED   = "\033[91m"; YELLOW = "\033[93m"
CYAN   = "\033[96m"; BOLD  = "\033[1m";  RESET  = "\033[0m"
GRAY   = "\033[90m"
def g(t): return f"{GREEN}{t}{RESET}"
def r(t): return f"{RED}{t}{RESET}"
def y(t): return f"{YELLOW}{t}{RESET}"
def c(t): return f"{CYAN}{t}{RESET}"
def b(t): return f"{BOLD}{t}{RESET}"
def gr(t): return f"{GRAY}{t}{RESET}"

VRAM_SAFETY_MB  = 1500
VRAM_HEAVY_MB   = 3500
VRAM_MEDIUM_MB  = 2000
VRAM_LIGHT_MB   = 700
POLL_INTERVAL   = 15
RESULTS_DIR     = os.path.join(PROJECT_ROOT, "results_v4", "walkforward")
LOG_DIR         = os.path.join(PROJECT_ROOT, "logs_v4", "smart_scheduler")

HEAVY_MODELS = {
    "Chronos","TimesFM","Moirai","Lag_Llama","TEMPO","GPT4TS",
    "GUMNet_Fusion","GUMNet_Diffusion","GUMNet_Graph",
}
MEDIUM_MODELS = {
    "PatchTST","TFT","Autoformer","FedFormer","Informer","Reformer",
    "iTransformer","TimesNet","TimeMixer","S_Mamba","MambaFormer",
    "BiMamba","TimeMachine","GUMNet_Mamba","GUMNet_iTrans","GUMNet_RL",
    "GUMNet_Decomp","GUMNet_Wavelet","GUMNet_Patch","GUMNet_Fourier",
    "GUMNet_MoE_Sparse",
}

def estimate_vram_mb(model):
    if model in HEAVY_MODELS:   return VRAM_HEAVY_MB
    elif model in MEDIUM_MODELS: return VRAM_MEDIUM_MB
    return VRAM_LIGHT_MB

def query_gpu_free_vram():
    try:
        result = subprocess.run(
            ["nvidia-smi","--query-gpu=index,memory.free","--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5)
        free = {}
        for line in result.stdout.strip().split("\n"):
            parts = line.split(",")
            if len(parts) == 2:
                free[int(parts[0].strip())] = int(parts[1].strip())
        return free
    except Exception as e:
        print(f"{r('[GPU ERROR]')} nvidia-smi failed: {e}")
        return {}

def is_completed(model, target, horizon, seed):
    json_path = os.path.join(RESULTS_DIR, model, f"{target}_H{horizon}_seed{seed}", "results.json")
    if not os.path.exists(json_path):
        return False
    try:
        with open(json_path) as f:
            data = json.load(f)
        return data.get("status") == "completed"
    except Exception:
        return False

def build_job_queue(filter_paradigm=None, filter_model=None, priority_horizons=None):
    all_models = ALL_SOTA_BASELINES + GUM_NET_VARIANTS
    if filter_paradigm:
        if filter_paradigm == "GUMNet":
            all_models = GUM_NET_VARIANTS
        elif filter_paradigm in SOTA_TAXONOMY_REGISTRY:
            all_models = SOTA_TAXONOMY_REGISTRY[filter_paradigm]
        else:
            all_models = [m for m in all_models if filter_paradigm.lower() in m.lower()]
    if filter_model:
        all_models = [m for m in all_models if m == filter_model]

    horizons = priority_horizons if priority_horizons else ALL_HORIZONS

    # === Priority ordering: GUMNet seed=42 FIRST ===
    # Phase 1: GUMNet variants, seed=42
    # Phase 2: Baselines, seed=42
    # Phase 3: GUMNet variants, other seeds
    # Phase 4: Baselines, other seeds
    gumnet_models   = [m for m in all_models if m in GUM_NET_VARIANTS]
    baseline_models = [m for m in all_models if m not in GUM_NET_VARIANTS]
    priority_seed   = 42
    other_seeds     = [s for s in SEEDS if s != priority_seed]

    def make_jobs(models, seeds):
        jobs = []
        for horizon in horizons:
            for seed in seeds:
                for target in ["XANG", "DAU"]:
                    light  = [m for m in models if m not in HEAVY_MODELS and m not in MEDIUM_MODELS]
                    medium = [m for m in models if m in MEDIUM_MODELS]
                    heavy  = [m for m in models if m in HEAVY_MODELS]
                    for model in light + medium + heavy:
                        if not is_completed(model, target, horizon, seed):
                            jobs.append((model, target, horizon, seed))
        return jobs

    jobs = (
        make_jobs(gumnet_models,   [priority_seed]) +   # Phase 1
        make_jobs(baseline_models, [priority_seed]) +   # Phase 2
        make_jobs(gumnet_models,   other_seeds)     +   # Phase 3
        make_jobs(baseline_models, other_seeds)         # Phase 4
    )
    print(f"\n{b('Job Queue:')} {len(jobs)} missing jobs found.")
    print(f"  Phase 1 (GUMNet seed=42):       {len(make_jobs(gumnet_models,[priority_seed]))}")
    print(f"  Phase 2 (Baselines seed=42):    {len(make_jobs(baseline_models,[priority_seed]))}")
    print(f"  Phase 3 (GUMNet other seeds):   {len(make_jobs(gumnet_models,other_seeds))}")
    print(f"  Phase 4 (Baselines other seeds):{len(make_jobs(baseline_models,other_seeds))}")
    return jobs



class GPUSlotManager:
    def __init__(self, gpu_id, max_slots, vram_headroom=VRAM_SAFETY_MB):
        self.gpu_id        = gpu_id
        self.max_slots     = max_slots
        self.vram_headroom = vram_headroom
        self.active_procs  = []  # (proc, label, vram_est)
        self._lock         = threading.Lock()
        self.completed     = 0
        self.failed        = 0
        os.makedirs(LOG_DIR, exist_ok=True)
        self.log_file = os.path.join(LOG_DIR, f"gpu{gpu_id}_scheduler.log")

    def reap(self):
        with self._lock:
            alive = []
            for proc, label, vram_est in self.active_procs:
                if proc.poll() is None:
                    alive.append((proc, label, vram_est))
                else:
                    rc = proc.returncode
                    if rc == 0:
                        self.completed += 1
                        self._log(f"[OK] {label}")
                        print(f"  {g('[DONE]')} GPU{self.gpu_id} ✓ {label}")
                    else:
                        self.failed += 1
                        self._log(f"[FAIL rc={rc}] {label}")
                        print(f"  {r('[FAIL]')} GPU{self.gpu_id} rc={rc} {label}")
            self.active_procs = alive

    def free_slots(self):
        self.reap()
        with self._lock:
            return max(0, self.max_slots - len(self.active_procs))

    def active_count(self):
        with self._lock:
            return len(self.active_procs)

    def can_fit_vram(self, model, free_vram):
        return free_vram >= (estimate_vram_mb(model) + self.vram_headroom)

    def dispatch(self, model, target, horizon, seed, dry_run=False):
        label = f"{model} | {target} | H{horizon} | seed={seed}"
        cmd = [
            sys.executable,
            os.path.join(PROJECT_ROOT, "scripts", "train_unified.py"),
            "--type", target,
            "--model", model,
            "--horizon", str(horizon),
            "--seed", str(seed),
            "--protocol", "walkforward",
        ]
        if dry_run:
            print(f"  {gr('[DRY]')} GPU{self.gpu_id}: {label}")
            return True

        env = os.environ.copy()
        env["CUDA_VISIBLE_DEVICES"] = str(self.gpu_id)
        env["PYTHONUNBUFFERED"]     = "1"
        log_path = os.path.join(LOG_DIR, f"gpu{self.gpu_id}_{model}_{target}_H{horizon}_s{seed}.log")
        log_f = open(log_path, "w", encoding="utf-8")
        try:
            proc = subprocess.Popen(cmd, stdout=log_f, stderr=log_f, env=env, cwd=PROJECT_ROOT)
            with self._lock:
                self.active_procs.append((proc, label, estimate_vram_mb(model)))
            now = datetime.now().strftime("%H:%M:%S")
            print(f"  {g('[LAUNCH]')} GPU{self.gpu_id} [{now}] → {c(label)}")
            self._log(f"[LAUNCH] {label} PID={proc.pid}")
            return True
        except Exception as e:
            print(f"  {r('[ERROR]')} GPU{self.gpu_id}: {e}")
            log_f.close()
            return False

    def status(self, free_vram):
        active = self.active_count()
        return (f"GPU{self.gpu_id}: {g(str(active)+'active')}/{self.max_slots}slots | "
                f"{y(str(free_vram)+'MB')} free | done={self.completed} fail={self.failed}")

    def _log(self, msg):
        line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)


def run_scheduler(gpu_ids, slots_per_gpu, filter_paradigm=None, filter_model=None,
                  dry_run=False, priority_horizons=None, vram_headroom=VRAM_SAFETY_MB):
    print(f"\n{'='*70}")
    print(f"  {b('SMART GPU GAP-FILLER SCHEDULER')} (Kimi + Antigravity)")
    print(f"{'='*70}")
    print(f"  GPUs      : {gpu_ids}  |  Slots/GPU: {slots_per_gpu}")
    print(f"  VRAM head : {vram_headroom}MB  |  Poll: {POLL_INTERVAL}s")
    print(f"  Filter    : {filter_paradigm or 'ALL'}")
    print(f"  Dry-run   : {dry_run}")
    print(f"  Logs      : {LOG_DIR}")
    print(f"{'='*70}\n")

    job_list = build_job_queue(filter_paradigm, filter_model, priority_horizons)
    if not job_list:
        print(g("All jobs already completed! Nothing to do."))
        return

    jq = queue.Queue()
    for j in job_list:
        jq.put(j)

    managers   = {gid: GPUSlotManager(gid, slots_per_gpu, vram_headroom) for gid in gpu_ids}
    total      = len(job_list)
    dispatched = 0
    start_time = time.time()
    last_print = 0

    print(f"{b('Scheduler running.')} {total} jobs queued. Ctrl+C to stop gracefully.\n")

    try:
        while True:
            vram_info = query_gpu_free_vram()

            for gid in gpu_ids:
                mgr = managers[gid]
                free_vram = vram_info.get(gid, 0)

                while mgr.free_slots() > 0:
                    deferred = []
                    dispatched_flag = False
                    for _ in range(min(60, jq.qsize() + 1)):
                        if jq.empty():
                            break
                        job = jq.get_nowait()
                        model, target, horizon, seed = job
                        if is_completed(model, target, horizon, seed):
                            continue
                        if mgr.can_fit_vram(model, free_vram):
                            ok = mgr.dispatch(model, target, horizon, seed, dry_run)
                            if ok:
                                dispatched += 1
                                free_vram -= estimate_vram_mb(model)
                                for dj in deferred:
                                    jq.put(dj)
                                dispatched_flag = True
                                break
                            else:
                                deferred.append(job)
                        else:
                            deferred.append(job)
                    for dj in deferred:
                        jq.put(dj)
                    if not dispatched_flag:
                        break

            # Status every 2 minutes
            elapsed = (time.time() - start_time) / 60
            if elapsed - last_print >= 2.0:
                last_print = elapsed
                total_done = sum(m.completed for m in managers.values())
                total_fail = sum(m.failed for m in managers.values())
                remaining  = jq.qsize()
                speed = total_done / elapsed if elapsed > 0 else 0
                eta   = (remaining / speed / 60) if speed > 0 else 0
                print(f"\n{gr('─'*65)}")
                print(f"  {b('STATUS')} {elapsed:.1f}min | dispatched={dispatched} "
                      f"done={g(str(total_done))} fail={r(str(total_fail))} "
                      f"queue={y(str(remaining))} ETA~{eta:.0f}h")
                for gid in gpu_ids:
                    print(f"    {managers[gid].status(vram_info.get(gid, 0))}")
                print(f"{gr('─'*65)}\n")

            # Termination
            all_active = sum(m.active_count() for m in managers.values())
            if jq.empty() and all_active == 0:
                total_done = sum(m.completed for m in managers.values())
                print(f"\n{g('All jobs completed!')} total_done={total_done} "
                      f"failed={sum(m.failed for m in managers.values())} "
                      f"elapsed={elapsed:.1f}min")
                break

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print(f"\n{y('[Stopped]')} Remaining in queue: {jq.qsize()}")
        print(f"  In-flight jobs (not killed): "
              f"{sum(m.active_count() for m in managers.values())}")
    finally:
        print(f"\n{'='*65}")
        for gid in gpu_ids:
            m = managers[gid]
            print(f"  GPU{gid}: completed={g(str(m.completed))} failed={r(str(m.failed))}")
        print(f"  Elapsed: {(time.time()-start_time)/60:.1f}min  |  Logs: {LOG_DIR}")
        print(f"{'='*65}")


def main():
    parser = argparse.ArgumentParser(description="Smart GPU Gap-Filler Scheduler")
    parser.add_argument("--gpus",             type=str, default="0,3")
    parser.add_argument("--slots",            type=int, default=2)
    parser.add_argument("--vram-headroom",    type=int, default=VRAM_SAFETY_MB)
    parser.add_argument("--filter-paradigm",  type=str, default=None)
    parser.add_argument("--filter-model",     type=str, default=None)
    parser.add_argument("--horizons",         type=str, default=None)
    parser.add_argument("--dry-run",          action="store_true")
    args = parser.parse_args()

    gpu_ids = [int(x.strip()) for x in args.gpus.split(",")]
    priority_horizons = [int(h.strip()) for h in args.horizons.split(",")] if args.horizons else None

    run_scheduler(
        gpu_ids=gpu_ids,
        slots_per_gpu=args.slots,
        filter_paradigm=args.filter_paradigm,
        filter_model=args.filter_model,
        dry_run=args.dry_run,
        priority_horizons=priority_horizons,
        vram_headroom=args.vram_headroom,
    )

if __name__ == "__main__":
    main()
