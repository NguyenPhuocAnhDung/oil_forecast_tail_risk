#!/bin/bash
set -e

mkdir -p logs_v4

echo "Starting GPU 0 (Seed 123)..."
python3 scripts/training/run_all_concurrent.py --gpus 0 --seeds 123 --target both --resume --max-workers 7 > logs_v4/concurrent_gpu0_resume.log 2>&1 &

echo "Starting GPU 1 (Seed 777)..."
python3 scripts/training/run_all_concurrent.py --gpus 1 --seeds 777 --target both --resume --max-workers 7 > logs_v4/concurrent_gpu1_resume.log 2>&1 &

echo "Starting GPU 2 (Seed 2025)..."
python3 scripts/training/run_all_concurrent.py --gpus 2 --seeds 2025 --target both --resume --max-workers 7 > logs_v4/concurrent_gpu2_resume.log 2>&1 &

echo "Starting GPU 3 (Seed 9999)..."
python3 scripts/training/run_all_concurrent.py --gpus 3 --seeds 9999 --target both --resume --max-workers 7 > logs_v4/concurrent_gpu3_resume.log 2>&1 &

echo "All 4 GPUs dispatched!"
