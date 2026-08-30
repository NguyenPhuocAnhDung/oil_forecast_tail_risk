#!/bin/bash
# ==============================================================================
# scripts/training/start_tmux_dau_sota.sh
# Kịch bản B: Tối ưu hóa toàn diện 4 GPU cho DẦU (Diesel DO)
# 27 SOTA Models x 7 Horizons x 2 Seeds còn thiếu (123 & 777)
# 
# Phân bổ tải hoàn hảo không xung đột:
# - GPU 0: Seed 123 | 14 GUMNet Models (98 jobs)
# - GPU 1: Seed 123 | 13 SOTA Baselines & Foundation (91 jobs)
# - GPU 2: Seed 777 | 14 GUMNet Models (98 jobs)
# - GPU 3: Seed 777 | 13 SOTA Baselines & Foundation (91 jobs)
# ==============================================================================
set -e

SESSION="oil_4gpus"

GUMNET_MODELS="GUMNet,GUMNet_Wavelet,GUMNet_Fourier,GUMNet_iTrans,GUMNet_Mamba,GUMNet_Patch,GUMNet_Diffusion,GUMNet_Graph,GUMNetHet,GUMNet_Adaptive,GUMNet_Decomp,GUMNet_Fusion,GUMNet_RL,GUMNet_MoE_Sparse"
BASELINES_MODELS="TimesFM,Chronos,Moirai,TTM,PatchTST,RLinear,DLinear,LTSF_Linear,iTransformer,TimesNet,TimeMixer,TFT,Autoformer"

echo "=============================================================================="
echo "🚀 KHỞI CHẠY DẦU (DIESEL DO) 4-GPU TỐI ƯU (KỊCH BẢN B)"
echo "27 SOTA MODELS x 3 SEEDS (376 JOBS CÒN LẠI ĐƯỢC CHIA ĐỀU 4 GPU)"
echo "=============================================================================="

# Tắt session cũ và dọn dẹp các tiến trình thừa
tmux kill-session -t $SESSION 2>/dev/null || true
pkill -f "train_unified.py.*--type DAU" 2>/dev/null || true
pkill -f "run_all_concurrent" 2>/dev/null || true
sleep 2

mkdir -p logs_v4

# Window 0: GPU 0 -> Seed 123 (GUMNet)
tmux new-session -d -s $SESSION -n "GPU0_s123_gum" \
  "python3 scripts/training/run_all_concurrent.py --gpus 0 --seeds 123 --target DAU --models '$GUMNET_MODELS' --resume --max-workers 7"

# Window 1: GPU 1 -> Seed 123 (Baselines)
tmux new-window -t $SESSION -n "GPU1_s123_base" \
  "python3 scripts/training/run_all_concurrent.py --gpus 1 --seeds 123 --target DAU --models '$BASELINES_MODELS' --resume --max-workers 7"

# Window 2: GPU 2 -> Seed 777 (GUMNet)
tmux new-window -t $SESSION -n "GPU2_s777_gum" \
  "python3 scripts/training/run_all_concurrent.py --gpus 2 --seeds 777 --target DAU --models '$GUMNET_MODELS' --resume --max-workers 7"

# Window 3: GPU 3 -> Seed 777 (Baselines)
tmux new-window -t $SESSION -n "GPU3_s777_base" \
  "python3 scripts/training/run_all_concurrent.py --gpus 3 --seeds 777 --target DAU --models '$BASELINES_MODELS' --resume --max-workers 7"

echo "=============================================================================="
echo "🎉 ĐÃ KHỞI TẠO THÀNH CÔNG TMUX SESSION '$SESSION' VỚI 4 GPU CHO DẦU!"
echo "=============================================================================="
echo "👉 Xem trực tiếp 4 GPU:"
echo "   tmux attach -t $SESSION"
echo ""
echo "👉 Phím tắt điều hướng trong tmux:"
echo "   - Cửa sổ 0: GPU 0 (Seed 123 - 14 GUMNet models)"
echo "   - Cửa sổ 1: GPU 1 (Seed 123 - 13 Baselines models)"
echo "   - Cửa sổ 2: GPU 2 (Seed 777 - 14 GUMNet models)"
echo "   - Cửa sổ 3: GPU 3 (Seed 777 - 13 Baselines models)"
echo "   - Thoát ra màn hình ngoài (để tắt máy): Ctrl+B rồi bấm phím D (Detach)"
echo "=============================================================================="
