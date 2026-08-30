#!/usr/bin/env python3
"""
scripts/training/auto_switch_to_dau_when_xang_done.py
Tự động theo dõi tiến độ XĂNG (3 Seeds: 42, 123, 777).
Ngay khi XĂNG hoàn thành 100% (987/987 jobs), sẽ tự động kích hoạt
DẦU cho Seed 123 trên GPU 0 (GUMNet) và GPU 1 (Baselines).
"""
import os
import sys
import time
import json
import subprocess
from datetime import datetime

project_root = "/data/quyhv/oil_forecast_tail_risk"
sys.path.insert(0, project_root)
from config import GUM_NET_VARIANTS, ALL_SOTA_BASELINES, ALL_HORIZONS

TARGET_SEEDS = [42, 123, 777]
results_dir = os.path.join(project_root, "results_v4", "walkforward")
all_models = list(dict.fromkeys(ALL_SOTA_BASELINES + GUM_NET_VARIANTS))
log_file = os.path.join(project_root, "logs_v4", "auto_switch_dau.log")

GUMNET_MODELS = "GUMNet,GUMNet_Wavelet,GUMNet_Fourier,GUMNet_iTrans,GUMNet_Mamba,GUMNet_Patch,GUMNet_Diffusion,GUMNet_Graph,GUMNetHet,GUMNet_Adaptive,GUMNet_Decomp,GUMNet_Fusion,GUMNet_RL,GUMNet_MoE_Sparse"
BASELINES_MODELS = "TimesFM,Chronos,Moirai,TTM,PatchTST,RLinear,DLinear,LTSF_Linear,iTransformer,TimesNet,TimeMixer,TFT,Autoformer"

def count_xang_completed():
    completed = 0
    missing = []
    for m in all_models:
        for h in ALL_HORIZONS:
            for s in TARGET_SEEDS:
                job_dir = os.path.join(results_dir, m, f"XANG_H{h}_seed{s}")
                res_json = os.path.join(job_dir, "results.json")
                done = False
                if os.path.exists(res_json):
                    try:
                        with open(res_json) as f:
                            d = json.load(f)
                        if d.get("status") == "completed" or "metrics" in d:
                            done = True
                    except:
                        pass
                if done:
                    completed += 1
                else:
                    missing.append((m, h, s))
    return completed, missing

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def main():
    os.makedirs(os.path.join(project_root, "logs_v4"), exist_ok=True)
    log("🚀 Auto-switch daemon started. Monitoring XĂNG (3 Seeds: 42, 123, 777)...")
    
    total_xang = len(all_models) * len(ALL_HORIZONS) * len(TARGET_SEEDS)
    
    while True:
        completed, missing = count_xang_completed()
        pct = completed / total_xang * 100
        
        log(f"Status: XĂNG {completed}/{total_xang} completed ({pct:.2f}%) | {len(missing)} jobs remaining")
        
        if len(missing) == 0:
            log("🎉🎉🎉 TOÀN BỘ XĂNG (3 SEEDS) ĐÃ HOÀN THÀNH 100%! Đang chuyển GPU 0 & 1 sang DẦU (Seed 123)...")
            
            # Switch Window 0 (GPU 0) and Window 1 (GPU 1) in tmux oil_4gpus to DAU Seed 123
            cmd0 = f"tmux send-keys -t oil_4gpus:0 C-c; sleep 1; tmux send-keys -t oil_4gpus:0 'python3 scripts/training/run_all_concurrent.py --gpus 0 --seeds 123 --target DAU --models \"{GUMNET_MODELS}\" --resume --max-workers 7' C-m"
            cmd1 = f"tmux send-keys -t oil_4gpus:1 C-c; sleep 1; tmux send-keys -t oil_4gpus:1 'python3 scripts/training/run_all_concurrent.py --gpus 1 --seeds 123 --target DAU --models \"{BASELINES_MODELS}\" --resume --max-workers 7' C-m"
            
            subprocess.run(cmd0, shell=True, cwd=project_root)
            subprocess.run(cmd1, shell=True, cwd=project_root)
            
            log("✅ Đã chuyển đổi thành công GPU 0 & 1 sang DẦU (Seed 123)! Toàn bộ 4 GPU hiện tại đều chạy DẦU SOTA!")
            break
        
        if len(missing) <= 10:
            log(f"Remaining XĂNG jobs: {missing}")
            
        time.sleep(60)

if __name__ == "__main__":
    main()
