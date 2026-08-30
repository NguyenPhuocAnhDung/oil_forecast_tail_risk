# ==============================================================================
# scripts/training/start_4gpus_dau_sota.sh
# Pipeline tối ưu hóa thực nghiệm DẦU (Diesel DO) 3 Seeds (42, 123, 777) x 7 Horizons
# Cắt giảm 20 baseline thấp nhất & cắt giảm 2 seeds cuối (9999, 2025)
# Chỉ giữ lại 27 SOTA Models & 3 Seeds chuẩn mực
# ==============================================================================
set -e

mkdir -p logs_v4

# Danh sách 27 SOTA Models chọn lọc (14 GUMNet + 4 Foundation + 4 Linear LTSF + 5 Transformers)
SOTA_MODELS="GUMNet,GUMNet_Wavelet,GUMNet_Fourier,GUMNet_iTrans,GUMNet_Mamba,GUMNet_Patch,GUMNet_Diffusion,GUMNet_Graph,GUMNetHet,GUMNet_Adaptive,GUMNet_Decomp,GUMNet_Fusion,GUMNet_RL,GUMNet_MoE_Sparse,TimesFM,Chronos,Moirai,TTM,PatchTST,RLinear,DLinear,LTSF_Linear,iTransformer,TimesNet,TimeMixer,TFT,Autoformer"

echo "=============================================================================="
echo " KHỞI CHẠY THỰC NGHIỆM DẦU (DIESEL DO) 3 SEEDS (42, 123, 777) x 7 HORIZONS"
echo " 27 SOTA MODELS (TỔNG CỘNG 567 JOBS — TIẾT KIỆM 40% THỜI GIAN)"
echo "=============================================================================="

echo "Starting GPU 0 (Seed 42 - DAU SOTA)..."
python3 scripts/training/run_all_concurrent.py --gpus 0 --seeds 42 --target DAU --models "$SOTA_MODELS" --resume --max-workers 7 > logs_v4/concurrent_dau_gpu0.log 2>&1 &

echo "Starting GPU 1 (Seed 123 - DAU SOTA)..."
python3 scripts/training/run_all_concurrent.py --gpus 1 --seeds 123 --target DAU --models "$SOTA_MODELS" --resume --max-workers 7 > logs_v4/concurrent_dau_gpu1.log 2>&1 &

echo "Starting GPU 2 (Seed 777 - DAU SOTA)..."
python3 scripts/training/run_all_concurrent.py --gpus 2 --seeds 777 --target DAU --models "$SOTA_MODELS" --resume --max-workers 7 > logs_v4/concurrent_dau_gpu2.log 2>&1 &

echo "Starting GPU 3 (Seed 42, 123, 777 balance - DAU SOTA)..."
python3 scripts/training/run_all_concurrent.py --gpus 3 --seeds 42,123,777 --target DAU --models "$SOTA_MODELS" --resume --max-workers 7 > logs_v4/concurrent_dau_gpu3.log 2>&1 &

echo "All 4 GPUs dispatched for DẦU (Diesel DO) 3-Seed SOTA benchmark!"

