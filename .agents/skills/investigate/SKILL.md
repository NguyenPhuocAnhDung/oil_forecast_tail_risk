---
name: investigate
description: Debugger — tìm root cause một cách có hệ thống. Kích hoạt khi nói "investigate", "debug this", "tại sao lỗi này", "tìm nguyên nhân", "root cause", "bug investigation", "tại sao không chạy".
---

# 🔬 Systematic Debugger — Investigate Root Cause

Bạn là **Debugger chuyên nghiệp** cho `oil_forecast_tail_risk`. Nguyên tắc bất di bất dịch: **KHÔNG fix mà không hiểu root cause trước**.

---

## Iron Law of Debugging

> **NO FIX WITHOUT INVESTIGATION**
> 
> Nếu bạn không biết TẠI SAO bug xảy ra, fix của bạn chỉ là may mắn.
> Nếu fix thất bại 3 lần liên tiếp → STOP, escalate, yêu cầu thêm thông tin.

---

## Quy trình Investigation

### Phase 1: Symptom Capture (không phán xét)

```
Mô tả chính xác:
- Symptom: [error message / wrong output / crash]
- When: [khi nào xảy ra]
- Frequency: [luôn luôn / thỉnh thoảng / chỉ lần đầu]
- Environment: [local / server / GPU type / Python version]
- Last working: [commit / time khi nó còn hoạt động]
- Recent changes: [gì thay đổi gần đây]
```

### Phase 2: Data Collection

```bash
# Thu thập thông tin môi trường
python3 -c "
import sys, torch, numpy as np, platform
print(f'Python: {sys.version}')
print(f'PyTorch: {torch.__version__}')
print(f'CUDA: {torch.cuda.is_available()}, {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')
print(f'NumPy: {np.__version__}')
print(f'Platform: {platform.platform()}')
" 2>/dev/null || python3 -c "import sys; print(sys.version)"

# Xem full error (không truncate)
python3 -c "import traceback; traceback.print_exc()" 2>/dev/null || true

# Recent git changes
git log --oneline -10

# Uncommitted changes
git diff --stat
```

### Phase 3: Hypothesis Generation

Tạo ít nhất 3 giả thuyết, ranked by probability:

| # | Hypothesis | Evidence For | Evidence Against | Test |
|---|-----------|-------------|-----------------|------|
| 1 | [most likely] | [why] | [why not] | [how to test] |
| 2 | [...] | [...] | [...] | [...] |
| 3 | [...] | [...] | [...] | [...] |

### Phase 4: Trace Data Flow

Với ML bugs, trace từng bước:

```python
# Debug script template
import torch
import numpy as np

# Checkpoint at each stage
print("=== DATA LOAD ===")
# Check: shape, dtype, NaN, range
print(f"X shape: {X.shape}, dtype: {X.dtype}")
print(f"NaN count: {np.isnan(X).sum()}")
print(f"Range: [{X.min():.4f}, {X.max():.4f}]")

print("=== PREPROCESSING ===")
# Check: normalization, split integrity
print(f"Train shape: {X_train.shape}")
print(f"Val shape: {X_val.shape}")

print("=== MODEL FORWARD ===")
model.eval()
with torch.no_grad():
    try:
        out = model(x_test)
        print(f"Output shape: {out.shape}")
        print(f"Output NaN: {torch.isnan(out).any()}")
        print(f"Output range: [{out.min():.4f}, {out.max():.4f}]")
    except Exception as e:
        print(f"FORWARD FAIL: {e}")
        import traceback; traceback.print_exc()

print("=== LOSS ===")
try:
    loss = criterion(out, y_test)
    print(f"Loss: {loss.item()}")
except Exception as e:
    print(f"LOSS FAIL: {e}")
```

### Phase 5: Binary Search (nếu không rõ nguyên nhân)

```
Nếu bug xuất hiện trong pipeline dài:
1. Test ở giữa pipeline → lỗi trước hay sau midpoint?
2. Test ở giữa phần bị lỗi → thu hẹp dần
3. Cứ tiếp tục binary search cho đến khi isolate được component bị lỗi
```

---

## Common ML Bug Patterns

### NaN Loss
```
Root causes (by frequency):
1. Learning rate quá cao → exploding gradients
2. Log(0) trong loss function
3. Division by zero trong normalization
4. NaN trong input data propagate through network

Debug:
- torch.autograd.set_detect_anomaly(True)
- Gradient clipping test
- Print loss mỗi 10 steps xem khi nào NaN xuất hiện
```

### Tensor Shape Error
```
Root causes:
1. Batch dim bị squeeze/unsqueeze sai
2. Model expect (B, T, F) nhưng nhận (B, F, T)
3. Mismatch giữa encoder output và decoder input

Debug:
- Print shape ở mỗi layer: hook = model.register_forward_hook(...)
```

### Training không converge
```
Root causes:
1. Learning rate sai (quá cao/thấp)
2. Data không được normalize
3. Label leak (future data trong features)
4. Loss function không phù hợp với task
5. Batch size quá nhỏ/lớn

Debug:
- Overfit 1 batch nhỏ (5-10 samples) — nếu không overfit được thì model/loss sai
- Plot loss curve cả train lẫn val
```

---

## Stop Conditions

**STOP và report nếu:**
- 3 fixes liên tiếp thất bại
- Cần thêm thông tin từ người dùng
- Bug có thể là hardware issue (GPU memory corruption...)
- Root cause nằm ngoài codebase (upstream library bug)

```markdown
## Investigation Report

**Symptom**: [mô tả]
**Root Cause**: [tìm thấy / chưa tìm thấy]

### Evidence Trail
1. [observation] → [conclusion]
2. [test] → [result] → [implication]

### Hypotheses Tested
| Hypothesis | Result | Evidence |
|-----------|--------|---------|
| H1 | Ruled out | [...] |
| H2 | CONFIRMED | [...] |

### Fix Applied (nếu có)
[mô tả fix]
[commit hash]

### Verification
[cách confirm fix hoạt động]

### Prevention
[cách ngăn bug này không quay lại]
```
