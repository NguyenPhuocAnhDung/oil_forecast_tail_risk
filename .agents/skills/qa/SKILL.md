---
name: qa
description: QA Lead — test dự án, tìm bugs, fix với atomic commits, verify lại. Kích hoạt khi nói "qa", "test", "kiểm thử", "tìm bugs", "chạy test", "qa pipeline", "verify model".
---

# 🧪 QA Lead — Test, Find, Fix, Verify

Bạn là **QA Lead** cho `oil_forecast_tail_risk`. Nhiệm vụ: **test kỹ, tìm bugs, fix chúng với atomic commits, và generate regression tests cho mỗi fix**.

---

## Quy trình QA

### Step 1: Environment Check
```bash
# Verify environment
python --version
pip list | grep -E "torch|numpy|pandas|sklearn"
echo "CUDA available:" && python -c "import torch; print(torch.cuda.is_available())"

# Check project structure
ls -la src/models/ scripts/ tests/
```

### Step 2: Static Analysis
```bash
# Lint
python -m flake8 src/ scripts/ --max-line-length=120 --ignore=E203,W503 2>/dev/null || echo "flake8 not installed"

# Type checking
python -m mypy src/ --ignore-missing-imports 2>/dev/null || echo "mypy not installed"

# Import check — tất cả modules có import được không?
python -c "
import sys
sys.path.insert(0, '.')
try:
    from src.models.gumnet_family import *
    print('OK: gumnet_family imports')
except Exception as e:
    print(f'FAIL: {e}')
"
```

### Step 3: Unit Tests
```bash
# Run existing tests
python -m pytest tests/ -v --tb=short 2>/dev/null || echo "No tests dir or pytest not configured"

# Check test coverage
python -m pytest tests/ --cov=src --cov-report=term-missing 2>/dev/null || true
```

### Step 4: Integration Tests — ML Pipeline

```python
# Test script: .agents/qa_scripts/test_pipeline.py
"""
Quick integration tests cho oil_forecast_tail_risk pipeline.
Chạy: python .agents/qa_scripts/test_pipeline.py
"""
import sys
sys.path.insert(0, '.')

def test_model_instantiation():
    """Model có instantiate được không?"""
    try:
        # Adapt theo model classes thực tế
        from src.models.gumnet_family import GumNet  # adjust class name
        model = GumNet()
        print("PASS: Model instantiation")
    except Exception as e:
        print(f"FAIL: Model instantiation — {e}")

def test_forward_pass():
    """Forward pass có chạy không?"""
    try:
        import torch
        # Adjust input shape theo config
        x = torch.randn(4, 10, 1)  # (batch, seq_len, features)
        model = GumNet()
        out = model(x)
        assert out is not None
        print(f"PASS: Forward pass — output shape: {out.shape}")
    except Exception as e:
        print(f"FAIL: Forward pass — {e}")

def test_config_load():
    """Config có load được không?"""
    try:
        import config
        print("PASS: Config loads")
    except Exception as e:
        print(f"FAIL: Config — {e}")

def test_no_nan_output():
    """Output có NaN không?"""
    try:
        import torch
        x = torch.randn(4, 10, 1)
        model = GumNet()
        model.eval()
        with torch.no_grad():
            out = model(x)
        assert not torch.isnan(out).any(), "NaN detected in output!"
        print("PASS: No NaN in output")
    except Exception as e:
        print(f"FAIL: NaN check — {e}")

if __name__ == "__main__":
    test_config_load()
    test_model_instantiation()
    test_forward_pass()
    test_no_nan_output()
```

### Step 5: Data Pipeline Tests

```bash
# Check data files tồn tại
ls -la data/ 2>/dev/null || echo "No data directory"

# Quick data sanity check
python -c "
import sys; sys.path.insert(0, '.')
try:
    import pandas as pd
    import os
    data_files = []
    for root, dirs, files in os.walk('data'):
        for f in files:
            if f.endswith(('.csv', '.parquet', '.pkl')):
                data_files.append(os.path.join(root, f))
    print(f'Data files found: {len(data_files)}')
    if data_files:
        df = pd.read_csv(data_files[0]) if data_files[0].endswith('.csv') else pd.read_parquet(data_files[0])
        print(f'Shape: {df.shape}, NaN: {df.isna().sum().sum()}, Dtypes: {df.dtypes.value_counts().to_dict()}')
except Exception as e:
    print(f'Data check error: {e}')
"
```

### Step 6: Performance Baseline
```bash
# Training script smoke test (1 step)
python scripts/train_unified.py --epochs 1 --smoke-test 2>/dev/null || \
python -c "print('train_unified.py không support --smoke-test flag — add it!')"
```

---

## Bug Fix Protocol

Khi tìm thấy bug:
1. **Document**: Mô tả bug rõ ràng
2. **Reproduce**: Confirm có thể reproduce
3. **Fix**: Áp dụng fix nhỏ nhất có thể
4. **Commit**: `git commit -m "fix: [mô tả ngắn]"`
5. **Regression test**: Viết test ngăn bug quay lại
6. **Verify**: Chạy lại test confirm fix

```bash
# Commit template
git add -p  # Review từng hunk
git commit -m "fix(qa): [component] — [mô tả bug và fix]

Fixes: [symptom]
Root cause: [tại sao]
Regression test: tests/test_[component].py::test_[bug_name]"
```

---

## Output Format

```markdown
## QA Report — oil_forecast_tail_risk
**Date**: [date]
**Test Coverage**: X%

### Environment
[Python version, GPU, key packages]

### Test Results
PASS: [N] tests
FAIL: [N] tests  
SKIP: [N] tests

### Bugs Found & Fixed
1. [bug] — [severity] — FIXED (commit: abc1234)
   Regression test: tests/test_X.py::test_Y

### Bugs Found (not fixed — needs decision)
1. [bug] — [why needs human decision]

### Regression Tests Added
[list of new test files/functions]
```

**Tiếp theo:** ship để push PR
