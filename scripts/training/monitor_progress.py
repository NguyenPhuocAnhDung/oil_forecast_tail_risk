#!/usr/bin/env python
"""
scripts/monitor_progress.py  ─ Live Terminal Dashboard
=======================================================
Màn hình theo dõi live tiến độ thực nghiệm song song.
Đọc log files, quét kết quả, và hiển thị bảng trạng thái cập nhật liên tục.

Usage:
  python scripts/monitor_progress.py                   # mặc định: cập nhật 5s
  python scripts/monitor_progress.py --interval 10     # cập nhật mỗi 10 giây
  python scripts/monitor_progress.py --results-dir results_v4
  python scripts/monitor_progress.py --no-gpu          # tắt nvidia-smi
  python scripts/monitor_progress.py --once            # chạy 1 lần rồi thoát
"""

import os
import sys
import time
import json
import subprocess
import argparse
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config import ALL_SOTA_BASELINES, GUM_NET_VARIANTS, ALL_HORIZONS, SEEDS

ALL_MODELS = ALL_SOTA_BASELINES + GUM_NET_VARIANTS
ALL_TARGETS = ["XANG", "DAU"]

# ── ANSI colors ──────────────────────────────────────────────
C_RESET  = "\033[0m"
C_BOLD   = "\033[1m"
C_GREEN  = "\033[92m"
C_RED    = "\033[91m"
C_YELLOW = "\033[93m"
C_CYAN   = "\033[96m"
C_GRAY   = "\033[90m"
C_BLUE   = "\033[94m"

CLEAR_SCREEN = "\033[2J\033[H"


def clear():
    print(CLEAR_SCREEN, end="", flush=True)


def color(text, code):
    return f"{code}{text}{C_RESET}"


def bold(text):
    return f"{C_BOLD}{text}{C_RESET}"


# ── GPU stats via nvidia-smi ─────────────────────────────────

def get_gpu_stats():
    """Trả về list of dict với GPU stats. Trả về [] nếu không có nvidia-smi."""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return []
        gpus = []
        for line in result.stdout.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 6:
                try:
                    gpus.append({
                        "id":        int(parts[0]),
                        "name":      parts[1][:16],
                        "util":      int(parts[2]),
                        "mem_used":  int(parts[3]),
                        "mem_total": int(parts[4]),
                        "temp":      int(parts[5]),
                    })
                except ValueError:
                    pass
        return gpus
    except Exception:
        return []


def fmt_gpu(g):
    util_bar = "█" * (g["util"] // 10) + "░" * (10 - g["util"] // 10)
    mem_pct   = g["mem_used"] / max(g["mem_total"], 1) * 100
    mem_bar   = "█" * int(mem_pct // 10) + "░" * (10 - int(mem_pct // 10))

    util_col = C_GREEN if g["util"] > 50 else (C_YELLOW if g["util"] > 20 else C_GRAY)
    mem_col  = C_RED if mem_pct > 85 else (C_YELLOW if mem_pct > 60 else C_GREEN)
    temp_col = C_RED if g["temp"] > 80 else (C_YELLOW if g["temp"] > 65 else C_GRAY)

    gpu_id_str = str(g["id"])
    return (
        f"  {bold('GPU' + gpu_id_str)} {g['name']:<16}  "
        f"Util:{color(util_bar, util_col)} {g['util']:3d}%  "
        f"VRAM:{color(mem_bar, mem_col)} {g['mem_used']:5d}/{g['mem_total']:5d}MB  "
        f"Temp:{color(str(g['temp']) + 'C', temp_col)}"
    )


# ── Experiment completion scan ────────────────────────────────

def scan_results(results_dir, models, targets, horizons, seeds):
    """Quét thư mục results_v4/walkforward và trả về thống kê."""
    walkforward_dir = os.path.join(results_dir, "walkforward")
    total     = len(models) * len(targets) * len(horizons) * len(seeds)
    completed = 0
    failed    = 0
    by_model  = {}

    if not os.path.exists(walkforward_dir):
        return {
            "total": total, "completed": 0, "failed": 0,
            "pct": 0.0, "by_model": {}, "by_target": {}
        }

    by_target = {t: {"done": 0, "fail": 0} for t in targets}

    for model in models:
        m_dir = os.path.join(walkforward_dir, model)
        done  = 0
        fail  = 0
        if os.path.isdir(m_dir):
            for run_name in os.listdir(m_dir):
                run_dir  = os.path.join(m_dir, run_name)
                json_p   = os.path.join(run_dir, "results.json")
                if not os.path.exists(json_p):
                    continue
                try:
                    with open(json_p) as f:
                        d = json.load(f)
                    if d.get("status") == "completed":
                        done += 1
                        # Determine target from run_name
                        for t in targets:
                            if run_name.startswith(t + "_"):
                                by_target[t]["done"] += 1
                                break
                    else:
                        fail += 1
                        for t in targets:
                            if run_name.startswith(t + "_"):
                                by_target[t]["fail"] += 1
                                break
                except Exception:
                    fail += 1
        completed += done
        failed    += fail
        by_model[model] = {"done": done, "fail": fail,
                           "total": len(targets) * len(horizons) * len(seeds)}

    pct = completed / max(total, 1) * 100

    return {
        "total": total,
        "completed": completed,
        "failed": failed,
        "pct": pct,
        "by_model": by_model,
        "by_target": by_target,
    }


def read_log_tail(log_path, n=8):
    """Đọc n dòng cuối của log file."""
    if not os.path.exists(log_path):
        return []
    try:
        result = subprocess.run(
            ["tail", f"-n{n}", log_path],
            capture_output=True, text=True, timeout=2,
        )
        return result.stdout.splitlines()
    except Exception:
        return []


def read_error_count(error_dir):
    """Đếm số .err files trong logs_v4/errors/."""
    if not os.path.isdir(error_dir):
        return 0
    return len([f for f in os.listdir(error_dir) if f.endswith(".err")])


# ── Display ───────────────────────────────────────────────────

PARADIGM_ORDER = [
    ("P1_Linear",      ["DLinear", "RLinear", "LTSF_Linear", "NBEATS", "NHits"]),
    ("P2_Transformer", ["PatchTST", "TFT", "Autoformer", "FedFormer", "Informer", "Reformer"]),
    ("P3_Inverted",    ["iTransformer", "UniTS", "TimeXer", "Crossformer", "CARD"]),
    ("P4_Frequency",   ["TimesNet", "TimeMixer", "TTM", "FITS", "CoST"]),
    ("P5_SSM",         ["TimeMachine", "S_Mamba", "MambaFormer", "BiMamba"]),
    ("P6_Foundation",  ["Chronos", "TimesFM", "Moirai", "Lag_Llama", "TEMPO", "GPT4TS"]),
    ("P7_SparseMoE",   ["Time_MoE", "Gated_TabNet"]),
    ("GUMNet",         GUM_NET_VARIANTS),
]


def render(stats, gpus, log_lines, error_count, results_dir, elapsed_sec, args):
    lines = []
    now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    w     = 80

    lines.append(bold(color("═" * w, C_CYAN)))
    lines.append(bold(color(
        f"  OIL FORECAST TAIL RISK  ─  Parallel Monitor  ─  {now}", C_CYAN
    )))
    lines.append(bold(color("═" * w, C_CYAN)))

    # ── Overall progress ───────────────────────────────────────
    comp   = stats["completed"]
    tot    = stats["total"]
    fail   = stats["failed"]
    pct    = stats["pct"]
    remain = tot - comp - fail
    bar_w  = 40
    filled = int(bar_w * pct / 100)
    bar    = color("█" * filled, C_GREEN) + color("░" * (bar_w - filled), C_GRAY)

    lines.append("")
    lines.append(f"  {bold('Overall Progress')}")
    lines.append(f"  [{bar}] {pct:5.1f}%")
    lines.append(
        f"  {color(str(comp), C_GREEN)} done  |  "
        f"{color(str(fail), C_RED)} failed  |  "
        f"{color(str(remain), C_GRAY)} pending  |  "
        f"{bold(str(tot))} total"
    )
    if error_count > 0:
        lines.append(
            f"  {color(f'{error_count} .err file(s) in logs_v4/errors/', C_YELLOW)}"
        )

    # ── Target breakdown ──────────────────────────────────────
    lines.append("")
    lines.append(f"  {bold('By Target:')}")
    for t, d in stats["by_target"].items():
        t_pct = d["done"] / max(stats["total"] // max(len(ALL_TARGETS), 1), 1) * 100
        lines.append(
            f"    {t:<6} → {color(str(d['done']), C_GREEN)} done  "
            f"{color(str(d['fail']), C_RED)} failed"
        )

    # ── GPU stats ─────────────────────────────────────────────
    if gpus:
        lines.append("")
        lines.append(f"  {bold('GPU Status:')}")
        for g in gpus:
            lines.append(fmt_gpu(g))

    # ── Paradigm breakdown ────────────────────────────────────
    lines.append("")
    lines.append(f"  {bold('By Paradigm:')}")
    by_model = stats["by_model"]

    for paradigm_name, paradigm_models in PARADIGM_ORDER:
        p_done  = sum(by_model.get(m, {}).get("done",  0) for m in paradigm_models)
        p_fail  = sum(by_model.get(m, {}).get("fail",  0) for m in paradigm_models)
        p_total = sum(by_model.get(m, {}).get("total", 0) for m in paradigm_models)
        p_pct   = p_done / max(p_total, 1) * 100
        fill    = int(20 * p_pct / 100)
        mini_bar = color("█" * fill, C_GREEN) + color("░" * (20 - fill), C_GRAY)
        status_col = C_GREEN if p_pct >= 100 else (C_YELLOW if p_pct > 0 else C_GRAY)
        lines.append(
            f"    {paradigm_name:<18}  [{mini_bar}] "
            f"{color(f'{p_done:3d}/{p_total}', status_col)}  "
            f"{color(f'✗{p_fail}', C_RED) if p_fail else ''}"
        )

    # ── Recent log lines ──────────────────────────────────────
    if log_lines:
        lines.append("")
        lines.append(f"  {bold('Recent Activity:')}")
        for ll in log_lines[-6:]:
            # Color OK/FAIL lines
            if "| OK" in ll:
                lines.append(f"  {color(ll[:w-4], C_GREEN)}")
            elif "FAIL" in ll or "TIMEOUT" in ll:
                lines.append(f"  {color(ll[:w-4], C_RED)}")
            elif "RETRY" in ll:
                lines.append(f"  {color(ll[:w-4], C_YELLOW)}")
            else:
                lines.append(f"  {color(ll[:w-4], C_GRAY)}")

    # ── Footer ────────────────────────────────────────────────
    lines.append("")
    eta_note = ""
    if comp > 0 and elapsed_sec > 0:
        avg_sec = elapsed_sec / comp
        eta_sec = avg_sec * (tot - comp)
        eta_note = f"  Avg: {avg_sec:.0f}s/job  ETA: {eta_sec/60:.0f}m"
    lines.append(color("─" * w, C_GRAY))
    lines.append(
        f"  Interval: {args.interval}s  |  Results: {results_dir}/"
        f"  |  Press Ctrl+C to exit{eta_note}"
    )
    lines.append(bold(color("═" * w, C_CYAN)))

    print("\n".join(lines), flush=True)


# ── Main ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Live terminal dashboard for parallel experiment monitoring"
    )
    parser.add_argument("--results-dir", default="results_v4",
                        help="Results directory (default: results_v4)")
    parser.add_argument("--interval", type=int, default=5,
                        help="Refresh interval in seconds (default: 5)")
    parser.add_argument("--no-gpu", action="store_true",
                        help="Disable nvidia-smi GPU stats")
    parser.add_argument("--once", action="store_true",
                        help="Print once and exit (non-interactive)")
    args = parser.parse_args()

    results_dir = os.path.join(project_root, args.results_dir)
    log_dir     = os.path.join(project_root, "logs_v4")
    error_dir   = os.path.join(log_dir, "errors")

    # Find most recent log file to show tail
    start_time  = time.time()

    try:
        while True:
            # Collect data
            stats = scan_results(
                results_dir, ALL_MODELS, ALL_TARGETS, ALL_HORIZONS, SEEDS
            )
            gpus  = [] if args.no_gpu else get_gpu_stats()

            # Find most recent log
            log_lines = []
            if os.path.isdir(log_dir):
                logs = sorted(
                    [os.path.join(log_dir, f)
                     for f in os.listdir(log_dir) if f.endswith(".log")],
                    key=os.path.getmtime, reverse=True
                )
                if logs:
                    log_lines = read_log_tail(logs[0], n=8)

            error_count = read_error_count(error_dir)
            elapsed     = time.time() - start_time

            # Render
            if not args.once:
                clear()
            render(stats, gpus, log_lines, error_count, args.results_dir, elapsed, args)

            if args.once:
                break

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n[Monitor] Stopped.")


if __name__ == "__main__":
    main()
