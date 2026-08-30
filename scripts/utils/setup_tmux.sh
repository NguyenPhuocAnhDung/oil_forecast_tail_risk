#!/usr/bin/env bash
# =============================================================================
# setup_tmux.sh  ─  Kiến Trúc Song Song Hoàn Chỉnh
# =============================================================================
# Tạo tmux sessions song song cho thực nghiệm 44 models trên 2-3 T4 GPUs.
# Dùng trên Linux cloud VM / Google Colab / Kaggle / RunPod.
#
# Usage:
#   chmod +x setup_tmux.sh
#   ./setup_tmux.sh --gpus 2                          # 2x T4
#   ./setup_tmux.sh --gpus 3                          # 3x T4
#   ./setup_tmux.sh --gpus auto                       # tự detect
#   ./setup_tmux.sh --gpus 2 --seeds 42,123,777,2025,9999
#   ./setup_tmux.sh --gpus 2 --resume                 # tiếp tục experiments chưa xong
#   ./setup_tmux.sh --gpus 2 --target XANG            # chỉ chạy XANG
#
# Cấu trúc tmux sessions (2x T4):
#   Session "xang"    → GPU 0 → --target XANG  (all 44 models)
#   Session "dau"     → GPU 1 → --target DAU   (all 44 models)
#   Session "monitor" → live GPU stats (nvidia-smi)
#
# Cấu trúc tmux sessions (3x T4):
#   Session "xang"    → GPU 0 → XANG: P1+P2+P3 + GUMNet_Light
#   Session "dau"     → GPU 1 → DAU:  P1+P2+P3 + GUMNet_Light
#   Session "heavy"   → GPU 2 → BOTH: P4+P5+P6+P7 + GUMNet_Heavy
#   Session "monitor" → live GPU stats
# =============================================================================

set -euo pipefail

# ── Colors ──────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# ── Default arguments ────────────────────────────────────────
GPUS="2"
SEEDS="42,123,777,2025,9999"
RESUME_FLAG=""
TARGET_FLAG=""
EXTRA_ARGS=""
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Parse arguments ──────────────────────────────────────────
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --gpus)    GPUS="$2";    shift ;;
        --seeds)   SEEDS="$2";   shift ;;
        --target)  TARGET_FLAG="$2"; shift ;;
        --resume)  RESUME_FLAG="--resume" ;;
        --dir)     PROJECT_DIR="$2"; shift ;;
        --retries) EXTRA_ARGS="$EXTRA_ARGS --retries $2"; shift ;;
        --timeout) EXTRA_ARGS="$EXTRA_ARGS --timeout $2"; shift ;;
        --help|-h)
            grep '^#' "${BASH_SOURCE[0]}" | sed 's/^# \{0,2\}//'
            exit 0
            ;;
        *) echo -e "${RED}[ERROR]${RESET} Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

cd "$PROJECT_DIR"

# ── Pre-flight checks ────────────────────────────────────────
echo ""
echo -e "${CYAN}${BOLD}============================================================${RESET}"
echo -e "${CYAN}${BOLD}  PARALLEL EXPERIMENT SETUP  ─  Pre-flight Checks${RESET}"
echo -e "${CYAN}${BOLD}============================================================${RESET}"

ERRORS=0

# Check tmux
if ! command -v tmux &>/dev/null; then
    echo -e "${RED}  [FAIL]${RESET} tmux not found. Install: apt-get install tmux"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}  [OK]${RESET}   tmux: $(tmux -V)"
fi

# Check python
if ! command -v python &>/dev/null && ! command -v python3 &>/dev/null; then
    echo -e "${RED}  [FAIL]${RESET} python not found"
    ERRORS=$((ERRORS + 1))
else
    PY_CMD=$(command -v python || command -v python3)
    echo -e "${GREEN}  [OK]${RESET}   python: $($PY_CMD --version 2>&1)"
fi

# Check nvidia-smi (GPU presence)
if ! command -v nvidia-smi &>/dev/null; then
    echo -e "${YELLOW}  [WARN]${RESET} nvidia-smi not found — GPU monitoring disabled"
    HAS_GPU=0
else
    HAS_GPU=1
    echo -e "${GREEN}  [OK]${RESET}   nvidia-smi available"
fi

# Auto-detect GPU count if requested
if [[ "$GPUS" == "auto" ]]; then
    if [[ "$HAS_GPU" -eq 1 ]]; then
        GPUS=$(nvidia-smi --list-gpus | wc -l)
        echo -e "${GREEN}  [AUTO]${RESET} Detected $GPUS GPU(s)"
    else
        echo -e "${YELLOW}  [WARN]${RESET} Cannot auto-detect GPUs (no nvidia-smi). Defaulting to --gpus 1"
        GPUS=1
    fi
fi

# Check config.py exists
if [[ ! -f "$PROJECT_DIR/config.py" ]]; then
    echo -e "${RED}  [FAIL]${RESET} config.py not found at $PROJECT_DIR"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}  [OK]${RESET}   config.py found"
fi

# Check run_all_concurrent.py exists
if [[ ! -f "$PROJECT_DIR/scripts/run_all_concurrent.py" ]]; then
    echo -e "${RED}  [FAIL]${RESET} scripts/run_all_concurrent.py not found"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}  [OK]${RESET}   scripts/run_all_concurrent.py found"
fi

# Check data
if [[ ! -f "$PROJECT_DIR/data/processed/unified_data.csv" ]]; then
    echo -e "${YELLOW}  [WARN]${RESET} data/processed/unified_data.csv not found — experiments will fail!"
else
    echo -e "${GREEN}  [OK]${RESET}   unified_data.csv found"
fi

if [[ "$ERRORS" -gt 0 ]]; then
    echo ""
    echo -e "${RED}  [ABORT]${RESET} $ERRORS pre-flight check(s) failed. Fix issues above and retry."
    exit 1
fi

# ── Create directories ────────────────────────────────────────
mkdir -p "$PROJECT_DIR/logs_v4/errors"
mkdir -p "$PROJECT_DIR/results_v4"
echo -e "${GREEN}  [OK]${RESET}   Directories: logs_v4/ and results_v4/ ready"

echo ""
echo -e "${CYAN}${BOLD}============================================================${RESET}"
echo -e "${CYAN}${BOLD}  TMUX SESSION SETUP${RESET}"
echo -e "${CYAN}${BOLD}  GPUs: $GPUS  |  Seeds: $SEEDS  |  Resume: ${RESUME_FLAG:-no}${RESET}"
echo -e "${CYAN}${BOLD}  Project: $PROJECT_DIR${RESET}"
echo -e "${CYAN}${BOLD}============================================================${RESET}"

# ── Kill existing sessions ────────────────────────────────────
for sess in xang dau heavy monitor; do
    if tmux has-session -t "$sess" 2>/dev/null; then
        echo -e "${YELLOW}  [tmux]${RESET} Killing existing session: $sess"
        tmux kill-session -t "$sess"
    fi
done

# ── Build Python command prefix ───────────────────────────────
PY="python"
if ! command -v python &>/dev/null; then
    PY="python3"
fi

COMMON_ARGS="--seeds $SEEDS $RESUME_FLAG $EXTRA_ARGS"

# Override target if --target was passed
if [[ -n "$TARGET_FLAG" ]]; then
    XANG_TARGET="$TARGET_FLAG"
    DAU_TARGET="$TARGET_FLAG"
    HEAVY_TARGET="$TARGET_FLAG"
else
    XANG_TARGET="XANG"
    DAU_TARGET="DAU"
    HEAVY_TARGET="both"
fi

# ── Create sessions by GPU count ─────────────────────────────

if [[ "$GPUS" -eq 1 ]]; then
    # ── 1x GPU: XANG then DAU sequentially in one session ────
    echo -e "  ${CYAN}[1-GPU]${RESET} Creating single session (XANG → DAU sequential)..."

    tmux new-session -d -s xang -x 220 -y 50
    tmux send-keys -t xang "cd $PROJECT_DIR" Enter
    tmux send-keys -t xang "echo '=== GPU 0: XANG → DAU (sequential) ===' && \
        $PY scripts/run_all_concurrent.py --gpus 0 --target XANG $COMMON_ARGS \
        2>&1 | tee logs_v4/xang_run.log && \
        $PY scripts/run_all_concurrent.py --gpus 0 --target DAU $COMMON_ARGS \
        --no-post-pipeline 2>&1 | tee logs_v4/dau_run.log" Enter

    echo ""
    echo -e "  ${GREEN}✓${RESET} 1 session created"
    echo -e "    Attach: ${BOLD}tmux attach -t xang${RESET}"
    echo -e "    Log:    logs_v4/xang_run.log | logs_v4/dau_run.log"

elif [[ "$GPUS" -eq 2 ]]; then
    # ── 2x GPU: GPU0=XANG, GPU1=DAU ──────────────────────────
    echo -e "  ${CYAN}[2-GPU]${RESET} Creating sessions: XANG(GPU0) + DAU(GPU1)..."

    # Session XANG → GPU 0
    tmux new-session -d -s xang -x 220 -y 50
    tmux send-keys -t xang "cd $PROJECT_DIR" Enter
    tmux send-keys -t xang "echo '=== GPU 0: ALL 44 MODELS | XANG ===' && \
        $PY scripts/run_all_concurrent.py --gpus 0 --target $XANG_TARGET $COMMON_ARGS \
        2>&1 | tee logs_v4/xang_run.log" Enter

    # Session DAU → GPU 1
    tmux new-session -d -s dau -x 220 -y 50
    tmux send-keys -t dau "cd $PROJECT_DIR" Enter
    tmux send-keys -t dau "echo '=== GPU 1: ALL 44 MODELS | DAU ===' && \
        $PY scripts/run_all_concurrent.py --gpus 1 --target $DAU_TARGET $COMMON_ARGS \
        2>&1 | tee logs_v4/dau_run.log" Enter

    echo ""
    echo -e "  ${GREEN}✓${RESET} 2 sessions created"
    printf "  %-12s → GPU 0 → %-8s  log: logs_v4/xang_run.log\n" "xang" "$XANG_TARGET"
    printf "  %-12s → GPU 1 → %-8s  log: logs_v4/dau_run.log\n"  "dau"  "$DAU_TARGET"

elif [[ "$GPUS" -ge 3 ]]; then
    # ── 3x GPU: GPU0=XANG-light, GPU1=DAU-light, GPU2=Heavy(both) ─
    echo -e "  ${CYAN}[3-GPU]${RESET} Creating sessions: XANG(GPU0) + DAU(GPU1) + Heavy(GPU2)..."

    LIGHT_PARADIGMS="P1_Linear,P2_Transformer,P3_Inverted,GUMNet_Light"
    HEAVY_PARADIGMS="P4_Frequency,P5_SSM,P6_Foundation,P7_SparseMoE,GUMNet_Heavy"

    # GPU 0: XANG — lightweight + medium models
    tmux new-session -d -s xang -x 220 -y 50
    tmux send-keys -t xang "cd $PROJECT_DIR" Enter
    tmux send-keys -t xang "echo '=== GPU 0: P1+P2+P3+GUMNet_Light | XANG ===' && \
        $PY scripts/run_all_concurrent.py --gpus 0 --target XANG \
        --paradigms $LIGHT_PARADIGMS $COMMON_ARGS \
        2>&1 | tee logs_v4/xang_gpu0.log" Enter

    # GPU 1: DAU — lightweight + medium models
    tmux new-session -d -s dau -x 220 -y 50
    tmux send-keys -t dau "cd $PROJECT_DIR" Enter
    tmux send-keys -t dau "echo '=== GPU 1: P1+P2+P3+GUMNet_Light | DAU ===' && \
        $PY scripts/run_all_concurrent.py --gpus 1 --target DAU \
        --paradigms $LIGHT_PARADIGMS $COMMON_ARGS \
        2>&1 | tee logs_v4/dau_gpu1.log" Enter

    # GPU 2: Both targets — P4/P5/P6/P7 + GUMNet-Heavy
    tmux new-session -d -s heavy -x 220 -y 50
    tmux send-keys -t heavy "cd $PROJECT_DIR" Enter
    tmux send-keys -t heavy "echo '=== GPU 2: P4+P5+P6+P7+GUMNet_Heavy | BOTH ===' && \
        $PY scripts/run_all_concurrent.py --gpus 2 --target $HEAVY_TARGET \
        --paradigms $HEAVY_PARADIGMS $COMMON_ARGS \
        2>&1 | tee logs_v4/heavy_gpu2.log" Enter

    echo ""
    echo -e "  ${GREEN}✓${RESET} 3 sessions created"
    printf "  %-12s → GPU 0 → XANG  (P1-P3, GUMNet_Light)   log: logs_v4/xang_gpu0.log\n"  "xang"
    printf "  %-12s → GPU 1 → DAU   (P1-P3, GUMNet_Light)   log: logs_v4/dau_gpu1.log\n"   "dau"
    printf "  %-12s → GPU 2 → BOTH  (P4-P7, GUMNet_Heavy)   log: logs_v4/heavy_gpu2.log\n" "heavy"

else
    echo -e "${RED}[ERROR]${RESET} Unsupported GPU count: $GPUS (must be 1, 2, or 3+)"
    exit 1
fi

# ── Monitor session ───────────────────────────────────────────
if [[ "$HAS_GPU" -eq 1 ]]; then
    tmux new-session -d -s monitor -x 220 -y 50
    tmux send-keys -t monitor \
        "watch -n 2 'echo \"=== GPU STATUS ===\"; \
nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu \
--format=csv,noheader,nounits | \
awk -F\",\" \"{printf \\\"  GPU%s %-15s  Util:%3s%%  VRAM:%6s/%6s MB  Temp:%2s°C\\n\\\", \\\$1, \\\$2, \\\$3, \\\$4, \\\$5, \\\$6}\"'" \
        Enter
    echo -e "  ${GREEN}✓${RESET} monitor session → GPU VRAM + utilization"
else
    # Fallback monitor: show log tails
    tmux new-session -d -s monitor -x 220 -y 50
    tmux send-keys -t monitor "watch -n 5 'echo \"=== LOG TAILS ===\"; tail -n 5 logs_v4/*.log 2>/dev/null'" Enter
    echo -e "  ${YELLOW}✓${RESET} monitor session → log tail (no GPU)"
fi

# ── Final summary ─────────────────────────────────────────────
echo ""
echo -e "${CYAN}${BOLD}============================================================${RESET}"
echo -e "${CYAN}${BOLD}  ALL SESSIONS LAUNCHED${RESET}"
echo -e "${CYAN}${BOLD}============================================================${RESET}"
echo ""
echo -e "  ${BOLD}Manage sessions:${RESET}"
echo -e "    tmux ls                          # list all sessions"
echo -e "    tmux attach -t monitor           # GPU live stats"
echo -e "    tmux attach -t xang              # XANG progress"
if [[ "$GPUS" -ge 2 ]]; then
    echo -e "    tmux attach -t dau               # DAU progress"
fi
if [[ "$GPUS" -ge 3 ]]; then
    echo -e "    tmux attach -t heavy             # Heavy models progress"
fi
echo ""
echo -e "  ${BOLD}Follow logs:${RESET}"
if [[ "$GPUS" -eq 2 ]]; then
    echo -e "    tail -f logs_v4/xang_run.log"
    echo -e "    tail -f logs_v4/dau_run.log"
elif [[ "$GPUS" -ge 3 ]]; then
    echo -e "    tail -f logs_v4/xang_gpu0.log"
    echo -e "    tail -f logs_v4/dau_gpu1.log"
    echo -e "    tail -f logs_v4/heavy_gpu2.log"
else
    echo -e "    tail -f logs_v4/xang_run.log"
fi
echo ""
echo -e "  ${BOLD}Monitor progress:${RESET}"
echo -e "    python scripts/monitor_progress.py     # live dashboard"
echo -e "    python scripts/check_resume.py         # check completed experiments"
echo ""
echo -e "  ${BOLD}Kill all:${RESET}"
echo -e "    tmux kill-server"
echo -e "${CYAN}${BOLD}============================================================${RESET}"
echo ""
