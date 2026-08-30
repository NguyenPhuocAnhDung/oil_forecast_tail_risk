# Kiến Trúc Song Song Hoàn Chỉnh — Parallel Architecture

> **Tài liệu hướng dẫn chạy 44 models đồng thời trên Cloud VM / Google Colab với 2-3x T4 GPUs**

---

## Sơ đồ kiến trúc

```
Cloud VM / Colab (2-3x T4)
│
├── setup_tmux.sh ──────────────► Tạo tmux sessions tự động
│       │
│       ├── Session "xang"    → GPU 0 → run_all_concurrent.py --target XANG
│       ├── Session "dau"     → GPU 1 → run_all_concurrent.py --target DAU
│       ├── Session "heavy"   → GPU 2 → run_all_concurrent.py --target both  (3x T4)
│       └── Session "monitor" → watch nvidia-smi live
│
└── run_all_concurrent.py ──────► Chạy 44 models ĐỒNG THỜI (ProcessPoolExecutor)
        │
        ├── Auto VRAM-aware: max 3-4 workers/T4 (16GB)
        ├── Resume: skip experiments đã hoàn thành
        ├── Retry:  tự thử lại jobs thất bại (--retries 1)
        ├── Progress: [  5/770] 0.6% | OK:4  FAIL:1  SKIP:0 | ETA: 47m | GUMNet|XANG|H5|s42
        └── Auto post-pipeline: compile → DM-test → effect_size → figures
```

---

## Quick Start — Copy-Paste

```bash
# 1. Clone & cài đặt
git clone https://github.com/NguyenPhuocAnhDung/oil_forecast_tail_risk.git
cd oil_forecast_tail_risk
pip install -r requirements_32models.txt
pip install git+https://github.com/Blealtan/efficient-kan.git

# 2. Khởi chạy tmux (chọn theo số GPU)
chmod +x setup_tmux.sh
./setup_tmux.sh --gpus 2 --seeds 42,123,777,2025,9999   # 2x T4
./setup_tmux.sh --gpus 3 --seeds 42,123,777,2025,9999   # 3x T4
./setup_tmux.sh --gpus auto                              # tự detect GPU count

# 3. Theo dõi tiến độ
tmux attach -t monitor      # GPU usage (live nvidia-smi)
tmux attach -t xang         # XANG progress bar
tmux attach -t dau          # DAU progress bar
tail -f logs_v4/xang_run.log
python scripts/monitor_progress.py   # Dashboard full

# 4. Thoát tmux (không kill session)
Ctrl+B, D
```

---

## Cơ chế VRAM-Aware Concurrency

**Câu hỏi: Tại sao không chạy tất cả 44 models cùng lúc?**

Các Foundation models cần rất nhiều VRAM:

| Loại model | VRAM ước tính | T4 16GB chứa được |
|------------|:-------------:|:-----------------:|
| Chronos / Moirai / TimesFM | 4,500 MB | ~3 models |
| GUMNet_Fusion / GUMNet_Graph | 2,500-3,000 MB | ~4-5 models |
| PatchTST / Autoformer | 1,800 MB | ~6-7 models |
| DLinear / LTSF_Linear | 400 MB | ~30 models |

Script tự tính `max_workers` dựa trên công thức:
```
heavy = VRAM của model nặng nhất trong batch
light_avg = trung bình VRAM của 2nd-6th nặng nhất
max_workers = floor((13,000 - heavy) / light_avg) + 1
```

Với full 44 models mix → thường ra **max_workers = 3** (an toàn cho T4 16GB).

---

## Phân chia GPU (2x T4 vs 3x T4)

### 2x T4 — Đơn giản nhất

| Session | GPU | Target | Models |
|---------|-----|--------|--------|
| `xang`  |  0  | XANG   | Tất cả 44 models |
| `dau`   |  1  | DAU    | Tất cả 44 models |

### 3x T4 — Tối ưu theo VRAM

| Session  | GPU | Target | Paradigms |
|----------|-----|--------|-----------|
| `xang`   |  0  | XANG   | P1+P2+P3+GUMNet_Light (20 models) |
| `dau`    |  1  | DAU    | P1+P2+P3+GUMNet_Light (20 models) |
| `heavy`  |  2  | Both   | P4+P5+P6+P7+GUMNet_Heavy (24 models) |

---

## Tất cả options của run_all_concurrent.py

```bash
python scripts/run_all_concurrent.py \
    --gpus 0 \                      # GPU ID (0, 1, 2, ...)
    --target XANG \                 # XANG | DAU | both
    --seeds 42,123,777,2025,9999 \ # Seeds (default: config.SEEDS)
    --horizons 1,3,5,7,10,20,60 \ # Horizons (default: ALL_HORIZONS)
    --paradigms P1_Linear,GUMNet \ # Subset paradigms (default: tất cả)
    --max-workers 4 \              # Override concurrent workers
    --timeout 3600 \               # Timeout mỗi job (giây)
    --retries 1 \                  # Thử lại nếu fail
    --resume \                     # Skip experiments đã xong
    --no-post-pipeline \           # Không chạy compile/DM-test sau
    --results-dir results_v4 \     # Thư mục kết quả
    --dry-run                      # Xem kế hoạch, không chạy
```

---

## Tất cả options của setup_tmux.sh

```bash
./setup_tmux.sh \
    --gpus 2 \                  # Số GPU (1, 2, 3+, hoặc "auto")
    --seeds 42,123,777,2025,9999 \  # Seeds
    --resume \                  # Chạy với --resume flag
    --target XANG \             # Giới hạn 1 target
    --retries 2 \               # Retry count
    --timeout 7200              # Timeout per job (giây)
```

---

## Monitoring & Debugging

### Live Dashboard
```bash
python scripts/monitor_progress.py                # refresh mỗi 5s
python scripts/monitor_progress.py --interval 10  # refresh mỗi 10s
python scripts/monitor_progress.py --once         # in 1 lần rồi thoát
python scripts/monitor_progress.py --no-gpu       # tắt nvidia-smi
```

### Kiểm tra experiments còn thiếu
```bash
python scripts/check_resume.py                    # tổng quan
python scripts/check_resume.py --target XANG      # chỉ XANG
python scripts/check_resume.py --missing          # in list jobs còn thiếu
python scripts/check_resume.py --missing --export missing_jobs.txt
python scripts/check_resume.py --csv status.csv   # xuất CSV đầy đủ
```

### Log files
```
logs_v4/
├── xang_run.log            # Progress từ session xang (2-GPU setup)
├── dau_run.log             # Progress từ session dau
├── xang_gpu0.log           # Progress từ session xang (3-GPU setup)
├── dau_gpu1.log
├── heavy_gpu2.log
├── concurrent_gpu0_*.log   # Timestamped log mỗi lần chạy
└── errors/
    └── {model}_{target}_H{h}_s{seed}.err   # Stderr của jobs thất bại
```

---

## Resume sau khi bị gián đoạn

Nếu quá trình bị ngắt (Ctrl+C, timeout, crash):

```bash
# Kiểm tra đã xong bao nhiêu
python scripts/check_resume.py --missing

# Resume từ chỗ dừng
./setup_tmux.sh --gpus 2 --seeds 42,123,777,2025,9999 --resume
# hoặc
python scripts/run_all_concurrent.py --gpus 0 --target XANG --resume --seeds 42,123,777,2025,9999
```

---

## Post-Pipeline (Tự động sau khi tất cả jobs xong)

Khi 100% experiments hoàn thành, `run_all_concurrent.py` tự chạy:

1. **`compile_32model_results.py`** → `results_v4/compiled_32model_results.csv`
2. **`dm_test_32models.py`** → DM stat/p-value matrices + MCS superior set
3. **`effect_size_32models.py`** → Cliff's Delta + Vargha-Delaney A12
4. **`generate_all_outputs.py`** → Tables (LaTeX/CSV) + Figures (PDF/PNG)

Chạy thủ công nếu cần:
```bash
python scripts/compile_32model_results.py --results-dir results_v4
python scripts/dm_test_32models.py --results-dir results_v4
python scripts/effect_size_32models.py --results-dir results_v4
python scripts/generate_all_outputs.py --results-dir results_v4
```

---

## Troubleshooting

| Vấn đề | Giải pháp |
|--------|-----------|
| `tmux: command not found` | `apt-get install tmux` |
| CUDA OOM Error | Giảm `--max-workers` (ví dụ: `--max-workers 2`) |
| Foundation models fail to load | Cài: `pip install chronos-forecasting timesfm uni2ts` |
| Jobs timeout | Tăng `--timeout 7200` |
| `unified_data.csv` not found | Chạy `python build_unified_data.py` trước |
| Session bị kill | Chạy lại `./setup_tmux.sh --gpus 2 --resume` |
| Nhiều FAIL errors | Xem `logs_v4/errors/*.err` để debug |

---

## Cấu trúc kết quả

```
results_v4/
├── walkforward/
│   ├── GUMNet/
│   │   ├── XANG_H1_seed42/
│   │   │   ├── results.json       # Metrics + metadata
│   │   │   ├── predictions.csv    # Predictions vs actuals
│   │   │   ├── errors.npy         # Raw error series (cho DM test)
│   │   │   └── gating_weights.npy # GUMNet routing weights
│   │   └── ...
│   ├── DLinear/
│   └── ...
├── compiled_32model_results.csv      # Aggregated metrics (seeds mean±std)
├── compiled_32model_results_by_paradigm.csv
├── dm_stat_matrix_XANG_H5_mae.csv   # Diebold-Mariano matrices
├── dm_pvalue_matrix_XANG_H5_mae.csv
├── mcs_superior_set.csv             # Hansen's MCS results
├── effect_size_matrix.csv           # Cliff's Delta + A12
├── tables/                          # LaTeX / CSV tables for paper
└── figures/                         # PDF / PNG figures for paper
```

---

## Ước tính thời gian

| Setup | Models/GPU | Jobs | ETA (T4) |
|-------|-----------|------|----------|
| 1x T4 | 44 (XANG+DAU) | 3,080 | ~8-10 giờ |
| 2x T4 | 44 each | 1,540/GPU | ~4-5 giờ |
| 3x T4 | 20+20+24 mixed | ~1,000/GPU | ~3-4 giờ |

*Ước tính dựa trên avg 4-8 phút/job × max_workers=3-4 concurrent.*
