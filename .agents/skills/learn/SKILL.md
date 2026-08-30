---
name: learn
description: Memory management — lưu learnings, patterns, pitfalls từ sessions. Kích hoạt khi nói "learn this", "remember this", "lưu lại", "save this pattern", "ghi nhớ", "add to memory".
---

# 🧠 Memory — Manage What We've Learned

Bạn là **Memory Manager** cho `oil_forecast_tail_risk`. Nhiệm vụ: **lưu learnings, search lại, prune stale info, làm cho agent ngày càng thông minh hơn với codebase này**.

---

## Lệnh Available

### `learn save [content]`
Lưu một learning mới:
```bash
mkdir -p .agents/memory
cat >> .agents/memory/learnings.md << EOF

---
## [$(date +%Y-%m-%d)] [CATEGORY]: [tiêu đề ngắn]

**Context**: [khi nào/tại sao]
**Learning**: [nội dung chi tiết]
**Tags**: #[tag1] #[tag2]
**Applies to**: [file/component]
EOF
echo "Saved learning"
```

### `learn search [keyword]`
Tìm learnings liên quan:
```bash
grep -A5 -B2 "[keyword]" .agents/memory/learnings.md 2>/dev/null || echo "No learnings found for: [keyword]"
```

### `learn list`
Xem tất cả learnings:
```bash
cat .agents/memory/learnings.md 2>/dev/null || echo "No learnings yet"
```

### `learn prune`
Review và xóa stale learnings:
```
1. List tất cả learnings
2. Hỏi: "Learnings nào không còn relevant?" 
3. Archive (không xóa) learnings cũ vào .agents/memory/archive/
```

---

## Categories

Dùng categories nhất quán khi lưu:

| Category | Dùng cho |
|----------|---------|
| `BUG` | Bug đã gặp và cách fix |
| `PATTERN` | Code pattern tốt cho dự án này |
| `PITFALL` | Cái bẫy hay gặp phải tránh |
| `PERF` | Performance insight |
| `DATA` | Data gotcha (format, NaN, alignment...) |
| `MODEL` | Model behavior insight |
| `CONFIG` | Config gotcha |
| `TOOL` | Tool/command hữu ích |

---

## Memory Format

```markdown
---
## [2026-07-18] BUG: NaN loss khi learning rate > 1e-3

**Context**: Training GumNet với lr=1e-2 trên chuỗi giá dầu
**Learning**: 
- GumNet không stable với lr > 1e-3 do gradient explosion ở attention layers
- Fix: clip_grad_norm_(model.parameters(), 1.0) + lr=5e-4
- Warmup schedule cần ít nhất 100 steps

**Tags**: #training #gumnet #nan #learning-rate
**Applies to**: scripts/train_unified.py, src/models/gumnet_family.py

---
## [2026-07-18] DATA: Time alignment của exogenous variables

**Context**: Exogenous variables từ EIA có lag 1 tuần
**Learning**:
- EIA data released weekly on Wednesdays, covers previous week
- Khi merge với daily price data: shift exo vars forward 5 business days
- Không làm điều này gây data leakage (future EIA values)

**Tags**: #data #exogenous #lag #leakage
**Applies to**: merge_exo_data.py

---
## [2026-07-18] PATTERN: Tạo reproducible experiments

**Context**: Cần reproduce kết quả sau 2 tuần
**Learning**:
```python
# Bắt buộc set này trước mỗi experiment:
import torch, numpy as np, random
SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

**Tags**: #reproducibility #seed #best-practice
**Applies to**: scripts/train_unified.py
```

---

## Auto-Load Context

Khi bắt đầu một task mới, tự động:
```bash
# Load relevant learnings
echo "=== RELEVANT MEMORY ==="
grep -A3 "Applies to.*$(basename $PWD)\|Applies to.*$(git rev-parse --show-toplevel 2>/dev/null | xargs basename)" \
  .agents/memory/learnings.md 2>/dev/null | head -40
```

---

## Memory Decay

Learnings có thể stale theo thời gian. Review monthly:
- BUG fixes: archive sau 6 tháng nếu không recur
- PATTERN: review sau 3 tháng xem còn applicable không
- DATA: review mỗi khi data source thay đổi
- MODEL: archive khi model version thay đổi major

---

## Export

```bash
# Export learnings cho team
cp .agents/memory/learnings.md docs/LEARNINGS.md
git add docs/LEARNINGS.md
git commit -m "docs: update team learnings log"
```
