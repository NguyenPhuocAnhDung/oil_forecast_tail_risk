#!/bin/bash
# ==============================================================================
# Script khởi chạy toàn bộ 4 GPU trong TMUX session 'oil_4gpus'
# Hỗ trợ tắt máy cá nhân, SSH, đóng trình duyệt mà không bị ngắt tiến trình.
# ==============================================================================

SESSION="oil_4gpus"

# Kiểm tra nếu session cũ đang chạy thì kill session cũ
tmux kill-session -t $SESSION 2>/dev/null || true
pkill -f run_all_concurrent 2>/dev/null || true
sleep 2

mkdir -p logs_v4

echo "Đang tạo TMUX session '$SESSION' với 4 windows riêng cho 4 GPU..."

# Window 0: GPU 0 (Seed 123)
tmux new-session -d -s $SESSION -n "GPU0_s123" "python3 scripts/training/run_all_concurrent.py --gpus 0 --seeds 123 --target both --resume --max-workers 7"

# Window 1: GPU 1 (Seed 777)
tmux new-window -t $SESSION -n "GPU1_s777" "python3 scripts/training/run_all_concurrent.py --gpus 1 --seeds 777 --target both --resume --max-workers 7"

# Window 2: GPU 2 (Seed 2025)
tmux new-window -t $SESSION -n "GPU2_s2025" "python3 scripts/training/run_all_concurrent.py --gpus 2 --seeds 2025 --target both --resume --max-workers 7"

# Window 3: GPU 3 (Seed 9999)
tmux new-window -t $SESSION -n "GPU3_s9999" "python3 scripts/training/run_all_concurrent.py --gpus 3 --seeds 9999 --target both --resume --max-workers 7"

echo "=============================================================================="
echo "🎉 ĐÃ KHỞI TẠO THÀNH CÔNG TMUX SESSION '$SESSION' VỚI 4 GPU!"
echo "=============================================================================="
echo "👉 Xem trực tiếp 4 GPU:"
echo "   tmux attach -t $SESSION"
echo ""
echo "👉 Phím tắt điều hướng trong tmux:"
echo "   - Chuyển cửa sổ: Ctrl+B rồi bấm phím 0, 1, 2, hoặc 3"
echo "   - Thoát ra màn hình ngoài (để tắt máy): Ctrl+B rồi bấm phím D (Detach)"
echo "=============================================================================="
