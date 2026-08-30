#!/usr/bin/env python3
"""
scripts/training/auto_balance_gpu_when_dau_s777_done.py
Tự động theo dõi DẦU Seed 777 và các GPU.
Ngay khi GPU 2 hoàn thành Seed 777 (GUMNet) hoặc GPU 1 hoàn thành Seed 777 (Baselines),
tự động điều chuyển GPU 2 / GPU 1 sang gánh DẦU Seed 123 (với --resume) để tăng tốc tối đa!
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

results_dir = os.path.join(project_root, "results_v4", "walkforward")
log_file = os.path.join(project_root, "logs_v4", "auto_balance_dau.log")

GUMNET_GROUP_A = "GUMNet,GUMNet_Wavelet,GUMNet_Fourier,GUMNet_iTrans,GUMNet_Mamba,GUMNet_Patch,GUMNet_Diffusion"
GUMNET_GROUP_B = "GUMNet_Graph,GUMNetHet,GUMNet_Adaptive,GUMNet_Decomp,GUMNet_Fusion,GUMNet_RL,GUMNet_MoE_Sparse"
GUMNET_ALL = f"{GUMNET_GROUP_A},{GUMNET_GROUP_B}"
TARGET_HORIZONS = "1,3,5,7,10,20"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def count_dau_seed(seed):
    gum_done = 0
    base_done = 0
    for h in [1, 3, 5, 7, 10, 20]:
        for m in GUM_NET_VARIANTS:
            res_json = os.path.join(results_dir, m, f"DAU_H{h}_seed{seed}", "results.json")
            if os.path.exists(res_json):
                gum_done += 1
        for m in ALL_SOTA_BASELINES:
            res_json = os.path.join(results_dir, m, f"DAU_H{h}_seed{seed}", "results.json")
            if os.path.exists(res_json):
                base_done += 1
    return gum_done, base_done

def is_gpu_busy(gpu_id):
    try:
        out = subprocess.check_output(
            ["nvidia-smi", f"--id={gpu_id}", "--query-compute-apps=pid", "--format=csv,noheader"],
            text=True
        ).strip()
        pids = [p for p in out.splitlines() if p.strip()]
        return len(pids) > 0
    except:
        return True

def main():
    os.makedirs(os.path.join(project_root, "logs_v4"), exist_ok=True)
    log("🚀 Auto-Balance Daemon đã khởi động. Đang theo dõi DẦU Seed 777 & Seed 123 (Zero-Overlap Mode)...")
    
    gpu2_switched = False
    gpu1_switched = False
    
    while True:
        try:
            gum777, base777 = count_dau_seed(777)
            total777 = gum777 + base777
            gum123, base123 = count_dau_seed(123)
            total123 = gum123 + base123
            
            # 1. Kiểm tra GPU 2: khi Seed 777 GUMNet xong (84 jobs H1->H20)
            if not gpu2_switched:
                if gum777 >= 84 or (gum777 >= 75 and not is_gpu_busy(2)):
                    log(f"🎉 GUMNet Seed 777 đã hoàn tất ({gum777}/84 jobs)! Tự động điều chuyển GPU 2 sang gánh Group B GUMNet Seed 123 (Zero Overlap)...")
                    cmd = (
                        f"tmux respawn-window -k -t oil_4gpus:2 "
                        f"\"python3 scripts/training/run_all_concurrent.py --gpus 2 --seeds 123 --target DAU "
                        f"--models '{GUMNET_GROUP_B}' --horizons '{TARGET_HORIZONS}' --resume --max-workers 7\""
                    )
                    subprocess.run(cmd, shell=True)
                    log("✅ Đã khởi chạy thành công GUMNet Group B (Seed 123) trên GPU 2!")
                    gpu2_switched = True

            # 2. Kiểm tra GPU 1: khi Seed 777 xong
            if not gpu1_switched:
                if base777 >= 78 and not is_gpu_busy(1):
                    log("🎉 GPU 1 đã xong Seed 777! Điều chuyển GPU 1 sang hỗ trợ Seed 123...")
                    cmd = (
                        f"tmux respawn-window -k -t oil_4gpus:1 "
                        f"\"python3 scripts/training/run_all_concurrent.py --gpus 1 --seeds 123 --target DAU "
                        f"--models '{GUMNET_ALL}' --horizons '{TARGET_HORIZONS}' --resume --max-workers 7\""
                    )
                    subprocess.run(cmd, shell=True)
                    log("✅ Đã kết nối GPU 1 vào hỗ trợ Seed 123!")
                    gpu1_switched = True

            # Kiểm tra xem H1->H20 của DẦU 123 và 777 đã xong chưa (84 + 78 = 162 jobs/seed)
            if total123 >= 162 and total777 >= 162:
                log("🏆 TOÀN BỘ DẦU H1->H20 (SEED 42, 123, 777) ĐÃ HOÀN TẤT 100%! Daemon sẵn sàng cho H60.")
                break

            time.sleep(15)
        except Exception as e:
            log(f"⚠️ Lỗi trong vòng lặp theo dõi: {e}")
            time.sleep(15)

if __name__ == "__main__":
    main()
