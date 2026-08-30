#!/usr/bin/env python
"""
scripts/run_all_concurrent.py  ─ Kiến Trúc Song Song Hoàn Chỉnh
=================================================================
Chạy TẤT CẢ models ĐỒNG THỜI (concurrent) trên một GPU dùng ProcessPoolExecutor.
Mỗi (model, horizon, seed) là một job riêng. Jobs được xếp hàng và chạy song song
tối đa N_WORKERS tiến trình cùng lúc, kiểm soát theo ước tính VRAM.

Tính năng:
  ✓ Resume/skip: Tự động bỏ qua experiments đã hoàn thành
  ✓ Retry: Tự thử lại job thất bại (--retries N)
  ✓ Rich progress bar với ETA, OK/FAIL/SKIP counters
  ✓ Stderr capture → logs_v4/errors/{label}.err
  ✓ SIGINT/SIGTERM graceful shutdown → print summary
  ✓ Auto post-pipeline: compile → DM-test → effect_size → figures
  ✓ Per-job timeout configurable (--timeout giây)
  ✓ VRAM-aware concurrency (tự tính theo model mix)

KHÁC BIỆT vs run_parallel_gpus.py:
  run_parallel_gpus.py  → mỗi GPU chạy models TUẦN TỰ (1 model tại 1 thời điểm)
  run_all_concurrent.py → mỗi GPU chạy N models CÙNG LÚC (thực sự song song)

Usage:
  # Chạy all 44 models đồng thời trên GPU 0, chỉ target XANG
  python scripts/run_all_concurrent.py --gpus 0 --target XANG --seeds 42,123,777,2025,9999

  # Chạy trên GPU 1, chỉ DAU
  python scripts/run_all_concurrent.py --gpus 1 --target DAU --seeds 42,123,777,2025,9999

  # Chạy subset paradigm trên GPU 2 (cả XANG lẫn DAU)
  python scripts/run_all_concurrent.py --gpus 2 --target both \\
      --paradigms P4_Frequency,P5_SSM,P6_Foundation,P7_SparseMoE,GUMNet_Heavy \\
      --seeds 42,123,777,2025,9999

  # Dry-run (hiển thị kế hoạch, không chạy)
  python scripts/run_all_concurrent.py --gpus 0 --target XANG --dry-run

  # Resume (tự động skip jobs đã xong)
  python scripts/run_all_concurrent.py --gpus 0 --target XANG --resume

  # Giới hạn concurrency thủ công
  python scripts/run_all_concurrent.py --gpus 0 --target XANG --max-workers 4

  # Thử lại tối đa 2 lần nếu fail
  python scripts/run_all_concurrent.py --gpus 0 --target XANG --retries 2
"""

import os
import sys
import time
import signal
import argparse
import subprocess
import threading
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from config import (
    SOTA_TAXONOMY_REGISTRY, GUM_NET_VARIANTS, ALL_HORIZONS, SEEDS,
    ALL_SOTA_BASELINES, RESULTS_DIR,
)

# ============================================================
# VRAM ESTIMATES (MB) — dùng để tính max concurrency
# T4 = 16,000 MB. Safety margin: dùng 13,000 MB usable
# ============================================================
T4_VRAM_MB = 13_000  # Conservative usable VRAM

VRAM_ESTIMATES = {
    # Foundation models — nặng nhất
    "Chronos": 4500, "TimesFM": 4500, "Moirai": 4500,
    "Lag_Llama": 4000, "TEMPO": 3500, "GPT4TS": 3500,
    # GUMNet heavy variants
    "GUMNet_Fusion": 3000, "GUMNet_Diffusion": 2500,
    "GUMNet_Graph": 2500, "GUMNet_RL": 2000,
    # Medium SSM/Transformer
    "S_Mamba": 2000, "MambaFormer": 2000, "BiMamba": 1800,
    "TimeMachine": 1800, "GUMNet_Mamba": 1800,
    "PatchTST": 1800, "Autoformer": 1800, "FedFormer": 1800,
    "Informer": 1500, "Reformer": 1500,
    "iTransformer": 1500, "GUMNet_iTrans": 1500,
    "UniTS": 1500, "TimeXer": 1200, "Crossformer": 1200, "CARD": 1200,
    "TimesNet": 1200, "TimeMixer": 1200, "TTM": 1200,
    "GUMNet_Wavelet": 1200, "GUMNet_Patch": 1000,
    # Lightweight
    "GUMNet": 900, "GUMNet_Fourier": 800, "GUMNet_MoE_Sparse": 800, "GUMNet_Adaptive": 900,
    "TFT": 900, "NHits": 700, "NBEATS": 700, "FITS": 600, "CoST": 700,
    "Time_MoE": 800, "Gated_TabNet": 500,
    "DLinear": 400, "RLinear": 400, "LTSF_Linear": 400,
}

SPECIAL_PARTITIONS = {
    "GUMNet_Light": ["GUMNet", "GUMNet_Mamba", "GUMNet_Patch",
                     "GUMNet_Fourier", "GUMNet_MoE_Sparse", "GUMNet_Adaptive"],
    "GUMNet_Heavy": ["GUMNet_iTrans", "GUMNet_Wavelet", "GUMNet_Diffusion",
                     "GUMNet_Graph", "GUMNet_RL", "GUMNet_Fusion"],
    "GUMNet_All":   GUM_NET_VARIANTS,
}

# ── Graceful shutdown flag ──────────────────────────────────
_shutdown_requested = False
_shutdown_lock = threading.Lock()


def _handle_signal(signum, frame):
    global _shutdown_requested
    with _shutdown_lock:
        if not _shutdown_requested:
            _shutdown_requested = True
            print("\n\n[INTERRUPTED] Graceful shutdown requested — finishing in-flight jobs...\n",
                  flush=True)


signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)


# ── Helpers ─────────────────────────────────────────────────

def resolve_models(paradigm_list):
    """Chuyển danh sách paradigm names → danh sách tên models cụ thể."""
    models = []
    for p in paradigm_list:
        if p in SOTA_TAXONOMY_REGISTRY:
            models.extend(SOTA_TAXONOMY_REGISTRY[p])
        elif p in SPECIAL_PARTITIONS:
            models.extend(SPECIAL_PARTITIONS[p])
        elif p in ("GUMNet", "GUMNet_All"):
            models.extend(GUM_NET_VARIANTS)
        else:
            models.append(p)
    return list(dict.fromkeys(models))  # preserve order, dedup


def estimate_max_workers(models: list, vram_budget: int = T4_VRAM_MB) -> int:
    """Tính số workers tối đa có thể chạy đồng thời dựa trên VRAM mix."""
    sorted_vram = sorted(
        [VRAM_ESTIMATES.get(m, 800) for m in models], reverse=True
    )
    heavy = sorted_vram[0] if sorted_vram else 1000
    # Average of 2nd–6th heaviest models = "light" concurrent slice
    slice_ = sorted_vram[1:6]
    light_avg = sum(slice_) / max(len(slice_), 1) if slice_ else 800

    # Solve: heavy + (N-1) * light_avg <= vram_budget
    if light_avg > 0:
        n = int((vram_budget - heavy) / light_avg) + 1
    else:
        n = 4
    return max(1, min(n, 8))  # Clamp 1–8 for a single T4


def is_completed(model: str, target: str, horizon: int, seed: int,
                 results_dir: str) -> bool:
    """Kiểm tra xem experiment đã có kết quả hợp lệ với ngày freeze <= 2026-04-30 chưa."""
    out_dir = os.path.join(
        results_dir, "walkforward", model,
        f"{target}_H{horizon}_seed{seed}"
    )
    json_path = os.path.join(out_dir, "results.json")
    pred_path = os.path.join(out_dir, "predictions.csv")
    if not os.path.exists(json_path) or not os.path.exists(pred_path):
        return False
    try:
        with open(json_path) as f:
            data = json.load(f)
        if data.get("status") != "completed" and "metrics" not in data:
            return False
        
        # Verify that prediction dates do not exceed 2026-04-30
        with open(pred_path, "r", encoding="utf-8") as pf:
            header = pf.readline()
            first_line = pf.readline()
            # Quick check on last line
            pf.seek(0, os.SEEK_END)
            size = pf.tell()
            pf.seek(max(0, size - 1024))
            last_lines = pf.readlines()
            for line in reversed(last_lines):
                parts = line.strip().split(",")
                if parts and len(parts[0]) >= 10:
                    d_str = parts[0]
                    if d_str > "2026-04-30":
                        return False
                    break
        return True
    except Exception:
        return False


def make_label(model, target, horizon, seed):
    return f"{model}|{target}|H{horizon}|s{seed}"


# ── Worker ───────────────────────────────────────────────────

# Per-model timeout overrides — GUMNet/Foundation models need more time
# H1 walkforward = 100 iterations, GUMNet ~50s/iter → needs ~5000s
GUMNET_MODELS = {
    "GUMNet", "GUMNet_Mamba", "GUMNet_iTrans", "GUMNet_Wavelet",
    "GUMNet_Patch", "GUMNet_Fourier", "GUMNet_Diffusion",
    "GUMNet_Graph", "GUMNet_RL", "GUMNet_MoE_Sparse", "GUMNet_Fusion",
}
FOUNDATION_MODELS = {
    "Chronos", "TimesFM", "Moirai", "Lag_Llama", "TEMPO", "GPT4TS",
}


def get_effective_timeout(model: str, horizon: int, base_timeout: int):
    """Tính timeout thực tế theo model và horizon.
    Nếu base_timeout <= 0: KHÔNG GIỚI HẠN THỜI GIAN (None).
    """
    if base_timeout is None or base_timeout <= 0:
        return None
    if horizon == 1:
        return max(base_timeout, 21600)  # 6h
    elif horizon in (3, 7):
        return max(base_timeout, 10800)  # 3h
    else:
        return max(base_timeout, 7200)   # 2h




def run_one_experiment(args_tuple):
    """
    Worker function chạy trong subprocess riêng.
    Trả về (label, returncode, elapsed_sec, stderr_snippet).
    """
    gpu_id, model, target, horizon, seed, dry_run, timeout, error_dir = args_tuple

    # Apply per-model timeout override
    effective_timeout = get_effective_timeout(model, horizon, timeout)

    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    env["PYTHONUNBUFFERED"] = "1"

    cmd = [
        sys.executable,
        os.path.join(project_root, "scripts", "training", "train_unified.py"),
        "--type", target,
        "--model", model,
        "--horizon", str(horizon),
        "--seed", str(seed),
        "--protocol", "walkforward",
    ]

    label = make_label(model, target, horizon, seed)

    if dry_run:
        return (label, 0, 0.0, "")

    t0 = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            env=env,
            capture_output=True,
            timeout=effective_timeout,
            text=True,
        )
        elapsed = time.time() - t0
        stderr_snippet = (result.stderr or "")[-500:]  # last 500 chars

        # Save full stderr to error log if failed
        if result.returncode != 0 and error_dir:
            safe = label.replace("|", "_").replace("/", "_")
            err_file = os.path.join(error_dir, f"{safe}.err")
            try:
                with open(err_file, "w", encoding="utf-8") as ef:
                    ef.write(f"CMD: {' '.join(cmd)}\n")
                    ef.write(f"RETURN: {result.returncode}\n\n")
                    ef.write("=== STDOUT ===\n")
                    ef.write(result.stdout or "")
                    ef.write("\n=== STDERR ===\n")
                    ef.write(result.stderr or "")
            except Exception:
                pass

        return (label, result.returncode, elapsed, stderr_snippet)
    except subprocess.TimeoutExpired:
        return (label, -1, effective_timeout, f"TIMEOUT after {effective_timeout}s (model={model}, H={horizon})")
    except Exception as e:
        return (label, -2, time.time() - t0, str(e)[:200])


# ── Post-pipeline ─────────────────────────────────────────────

def run_post_pipeline(results_dir: str):
    """Chạy compile → DM-test → effect_size → generate_all_outputs sau khi xong."""
    scripts = [
        ("Compile results",    "scripts/reports/compile_completed_h_5seeds.py"),
        ("DM & MCS test",      "scripts/evaluation/dm_test_32models.py"),
        ("Effect size",        "scripts/evaluation/effect_size_32models.py"),
        ("Generate outputs",   "scripts/reports/generate_all_outputs.py"),
    ]

    print("\n" + "═" * 70)
    print("  POST-PIPELINE: compile → DM-test → effect_size → figures")
    print("═" * 70)

    for step_name, script_path in scripts:
        full_path = os.path.join(project_root, script_path)
        if not os.path.exists(full_path):
            print(f"  [SKIP] {step_name}: script not found → {script_path}")
            continue
        print(f"\n  ► {step_name}...", flush=True)
        t0 = time.time()
        try:
            ret = subprocess.run(
                [sys.executable, full_path, "--results-dir", results_dir],
                cwd=project_root,
                timeout=600,
            )
            elapsed = time.time() - t0
            status = "OK" if ret.returncode == 0 else f"FAIL({ret.returncode})"
            print(f"    {status} ({elapsed:.0f}s)")
        except subprocess.TimeoutExpired:
            print(f"    TIMEOUT after 600s")
        except Exception as e:
            print(f"    ERROR: {e}")

    print(f"\n  [DONE] Pipeline complete → {results_dir}/tables/ & {results_dir}/figures/")
    print("═" * 70 + "\n")


# ── Main ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Run ALL models CONCURRENTLY on a single GPU (ProcessPoolExecutor) "
                    "with resume, retry, and auto post-pipeline."
    )
    parser.add_argument("--gpus", type=str, default="0",
                        help="GPU ID to use (single value, e.g. '0')")
    parser.add_argument("--target", type=str, default="both",
                        choices=["XANG", "DAU", "both"],
                        help="Target product group")
    parser.add_argument("--seeds", type=str, default=None,
                        help="Comma-separated seeds. Default: config.SEEDS")
    parser.add_argument("--horizons", type=str, default=None,
                        help="Comma-separated horizons. Default: ALL_HORIZONS")
    parser.add_argument("--models", type=str, default=None,
                        help="Comma-separated model names to run explicitly")
    parser.add_argument("--paradigms", type=str, default=None,
                        help="Comma-separated paradigms. Default: all 44 models")
    parser.add_argument("--max-workers", type=int, default=None,
                        help="Max concurrent processes. Default: auto VRAM-aware")
    parser.add_argument("--timeout", type=int, default=0,
                        help="Per-job timeout in seconds (default: 0 = unlimited)")
    parser.add_argument("--retries", type=int, default=1,
                        help="Max retries for failed jobs (default: 1)")
    parser.add_argument("--resume", action="store_true",
                        help="Skip already-completed experiments")
    parser.add_argument("--no-post-pipeline", action="store_true",
                        help="Skip post-pipeline (compile/DM-test/figures)")
    parser.add_argument("--results-dir", type=str, default="results_v4",
                        help="Results directory (default: results_v4)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show plan without running")
    args = parser.parse_args()

    # ── Parse inputs ─────────────────────────────────────────
    gpu_id = int(args.gpus.split(",")[0])
    seeds = [int(s.strip()) for s in args.seeds.split(",")] if args.seeds else SEEDS
    horizons = [int(h.strip()) for h in args.horizons.split(",")] if args.horizons else ALL_HORIZONS
    targets = ["XANG", "DAU"] if args.target == "both" else [args.target]
    results_dir = args.results_dir

    if args.models:
        models = [m.strip() for m in args.models.split(",") if m.strip()]
    elif args.paradigms:
        models = resolve_models([p.strip() for p in args.paradigms.split(",")])
    else:
        models = ALL_SOTA_BASELINES + GUM_NET_VARIANTS

    # ── Create directories ────────────────────────────────────
    log_dir = os.path.join(project_root, "logs_v4")
    error_dir = os.path.join(log_dir, "errors")
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(error_dir, exist_ok=True)

    # ── Build job list ────────────────────────────────────────
    all_jobs = []
    for seed in seeds:
        for target in targets:
            for horizon in horizons:
                for model in models:
                    all_jobs.append((gpu_id, model, target, horizon, seed,
                                     args.dry_run, args.timeout, error_dir))

    total_planned = len(all_jobs)

    # ── Resume: filter completed ──────────────────────────────
    if args.resume and not args.dry_run:
        jobs_to_run = []
        skip_count = 0
        for job in all_jobs:
            _, model, target, horizon, seed, *_ = job
            if is_completed(model, target, horizon, seed, results_dir):
                skip_count += 1
            else:
                jobs_to_run.append(job)
    else:
        jobs_to_run = all_jobs
        skip_count = 0

    # ── Determine max_workers ─────────────────────────────────
    max_workers = args.max_workers or estimate_max_workers(models)

    # ── Print plan ────────────────────────────────────────────
    w = 70
    print("\n" + "═" * w)
    print("  CONCURRENT EXPERIMENT PLAN  ─  Kiến Trúc Song Song Hoàn Chỉnh")
    print("═" * w)
    print(f"  GPU              : {gpu_id}  (CUDA_VISIBLE_DEVICES={gpu_id})")
    print(f"  Target(s)        : {targets}")
    print(f"  Models           : {len(models)}")
    print(f"  Horizons         : {horizons}")
    print(f"  Seeds            : {seeds}")
    print(f"  Total planned    : {total_planned}")
    if args.resume:
        print(f"  Already done     : {skip_count}  (--resume skip)")
    print(f"  Jobs to run      : {len(jobs_to_run)}")
    print(f"  Max concurrent   : {max_workers}  (auto VRAM-aware)")
    timeout_str = "Unlimited (không giới hạn)" if args.timeout <= 0 else f"{args.timeout}s"
    print(f"  Per-job timeout  : {timeout_str}")
    print(f"  Retries          : {args.retries}")

    print(f"  Results dir      : {results_dir}/")
    print(f"  Error logs       : logs_v4/errors/")
    print(f"  Dry run          : {args.dry_run}")
    print()
    print(f"  Models ({len(models)}):")
    for i, m in enumerate(models):
        vram = VRAM_ESTIMATES.get(m, 800)
        print(f"    [{i+1:02d}] {m:<22} ~{vram:4d} MB VRAM")
    print("═" * w + "\n")

    if args.dry_run:
        print(f"[DRY-RUN] {len(jobs_to_run)} jobs would run with {max_workers} concurrent workers.")
        print(f"[DRY-RUN] Skip {skip_count} already-completed experiments.")
        return

    if not jobs_to_run:
        print("[INFO] All experiments already completed. Nothing to run.")
        if not args.no_post_pipeline:
            run_post_pipeline(results_dir)
        return

    # ── Run ───────────────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_log = os.path.join(log_dir, f"concurrent_gpu{gpu_id}_{timestamp}.log")

    print(f"[GPU{gpu_id}] Starting {len(jobs_to_run)} jobs with {max_workers} concurrent workers...")
    print(f"[GPU{gpu_id}] Log: {results_log}\n")

    start_time = time.time()
    ok_count = 0
    fail_count = 0
    skip_count_runtime = skip_count  # already skipped above
    completed = 0
    total = len(jobs_to_run)
    lock = threading.Lock()

    # Retry tracking
    retry_queue = {}   # label -> retries_remaining

    def format_progress(completed, total, ok, fail, skip, elapsed_job, label, status):
        elapsed_total = time.time() - start_time
        pct = completed / total * 100 if total > 0 else 0
        done_real = ok + fail
        avg = elapsed_total / max(done_real, 1)
        eta_sec = avg * (total - completed)
        eta_str = f"{eta_sec/60:.0f}m" if eta_sec >= 60 else f"{eta_sec:.0f}s"
        return (
            f"[{completed:4d}/{total}] {pct:5.1f}% "
            f"| OK:{ok:<4} FAIL:{fail:<4} SKIP:{skip:<4}"
            f"| {status:<12} | {elapsed_job:.0f}s "
            f"| ETA:{eta_str:<5} | {label}"
        )

    with open(results_log, "w", encoding="utf-8") as log_f:
        log_f.write(f"Concurrent run started: {datetime.now().isoformat()}\n")
        log_f.write(f"GPU: {gpu_id} | Models: {len(models)} | Jobs: {total}\n\n")

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_map = {}
            for job in jobs_to_run:
                if _shutdown_requested:
                    break
                f = executor.submit(run_one_experiment, job)
                future_map[f] = job

            for future in as_completed(future_map):
                if _shutdown_requested:
                    break

                label, returncode, elapsed, stderr_snip = future.result()
                job = future_map[future]
                _, model, target, horizon, seed, *_ = job

                with lock:
                    completed += 1

                    if returncode == 0:
                        ok_count += 1
                        status = "OK"
                    elif returncode == -1:
                        status = "TIMEOUT"
                        # Attempt retry?
                        retries_left = retry_queue.get(label, args.retries)
                        if retries_left > 0:
                            retry_queue[label] = retries_left - 1
                            status = f"RETRY({retries_left})"
                            new_f = executor.submit(run_one_experiment, job)
                            future_map[new_f] = job
                        else:
                            fail_count += 1
                    else:
                        retries_left = retry_queue.get(label, args.retries)
                        if retries_left > 0:
                            retry_queue[label] = retries_left - 1
                            status = f"RETRY({retries_left})"
                            new_f = executor.submit(run_one_experiment, job)
                            future_map[new_f] = job
                        else:
                            fail_count += 1
                            status = f"FAIL({returncode})"

                    msg = format_progress(
                        completed, total, ok_count, fail_count,
                        skip_count_runtime, elapsed, label, status
                    )
                    print(msg, flush=True)
                    log_f.write(msg + "\n")
                    if stderr_snip and returncode != 0:
                        log_f.write(f"  STDERR: {stderr_snip}\n")
                    log_f.flush()

    # ── Final summary ─────────────────────────────────────────
    elapsed_total = time.time() - start_time
    w = 70

    if _shutdown_requested:
        print(f"\n{'═'*w}")
        print(f"  [INTERRUPTED] Partial run: {ok_count}/{total} OK | {fail_count} FAILED")
        print(f"  Total time: {elapsed_total/60:.1f} min")
        print(f"  Tip: Re-run with --resume to continue from where you left off.")
        print(f"{'═'*w}\n")
        sys.exit(130)

    print(f"\n{'═'*w}")
    print(f"  COMPLETED: {ok_count}/{total} OK | {fail_count} FAILED | {skip_count_runtime} SKIPPED")
    print(f"  Total time: {elapsed_total/60:.1f} min  ({elapsed_total:.0f}s)")
    print(f"  Log: {results_log}")
    print(f"{'═'*w}\n")

    if fail_count > 0:
        print(f"[WARN] {fail_count} experiments failed.")
        print(f"       Error logs → logs_v4/errors/")
        print(f"       Tip: Re-run with --resume --retries 2 to retry failed jobs.\n")

    if ok_count + skip_count_runtime >= total_planned and not args.no_post_pipeline:
        run_post_pipeline(results_dir)
    elif args.no_post_pipeline:
        print("[INFO] Post-pipeline skipped (--no-post-pipeline).")
    else:
        print(f"[WARN] Not all experiments succeeded ({ok_count}/{total}).")
        print(f"       Skipping post-pipeline. Run with --resume to retry failures.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
