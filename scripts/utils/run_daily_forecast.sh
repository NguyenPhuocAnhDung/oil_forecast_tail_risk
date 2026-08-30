#!/usr/bin/env bash
# =============================================================================
# scripts/run_daily_forecast.sh
# =============================================================================
# Wrapper script chạy tự động hằng ngày lúc 7h00 sáng.
# Kiểm tra Thứ 7, Chủ Nhật và ngày lễ Việt Nam trước khi thực thi.
# =============================================================================

set -euo pipefail

# 1. Kiểm tra ngày trong tuần (Thứ 7 = 6, Chủ Nhật = 7)
DAY_OF_WEEK=$(date +%u)
if [ "$DAY_OF_WEEK" -eq 6 ] || [ "$DAY_OF_WEEK" -eq 7 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️ Hôm nay là cuối tuần. Bỏ qua tác vụ dự báo."
    exit 0
fi

# 2. Kiểm tra các ngày lễ Việt Nam cố định (Định dạng: MM-DD)
# 01-01 (Tết Dương Lịch), 04-30 (30/4), 05-01 (1/5), 09-02 (2/9)
TODAY_MD=$(date +%m-%d)
if [ "$TODAY_MD" = "01-01" ] || [ "$TODAY_MD" = "04-30" ] || [ "$TODAY_MD" = "05-01" ] || [ "$TODAY_MD" = "09-02" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️ Hôm nay là ngày lễ Việt Nam. Bỏ qua tác vụ dự báo."
    exit 0
fi

# 3. Kích hoạt Python chạy dự báo tự động
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 Kích hoạt quy trình tự động hóa dự báo hằng ngày..."
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

python3 scripts/daily_auto_forecast.py

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Hoàn tất!"
