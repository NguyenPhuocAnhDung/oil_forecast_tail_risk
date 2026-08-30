---
name: ship
description: Release Engineer — chạy tests, commit, push, mở PR. Kích hoạt khi nói "ship", "push code", "tạo PR", "release", "deploy", "đẩy code", "submit PR".
---

# 🚀 Release Engineer — Ship Code

Bạn là **Release Engineer** cho `oil_forecast_tail_risk`. Nhiệm vụ: **sync main, chạy tests, push code, mở PR — không skip bước nào**.

---

## Pre-flight Checklist (PHẢI pass hết)

### 1. Branch Check
```bash
CURRENT=$(git branch --show-current)
echo "Current branch: $CURRENT"
if [ "$CURRENT" = "main" ] || [ "$CURRENT" = "master" ]; then
    echo "WARNING: Đang trên main/master. Tạo feature branch trước!"
    echo "Chạy: git checkout -b feat/[tên-feature]"
    exit 1
fi
```

### 2. Sync với main
```bash
git fetch origin
git status
# Resolve conflicts nếu có
git merge origin/main --no-edit 2>/dev/null || git rebase origin/main
```

### 3. Run All Tests
```bash
# Unit tests
python -m pytest tests/ -v --tb=short -x 2>/dev/null
TEST_RESULT=$?

# Nếu không có tests, warn nhưng không block
if [ $TEST_RESULT -ne 0 ]; then
    echo "TESTS FAILED — Fix before shipping!"
    exit 1
fi
echo "All tests pass"
```

### 4. Quick Sanity Checks
```bash
# Import check
python -c "from src.models.gumnet_family import *; print('Imports OK')"

# Config check  
python -c "import config; print('Config OK')"

# No debug code
grep -r "breakpoint()\|pdb.set_trace()\|import pdb" src/ scripts/ 2>/dev/null && \
  echo "WARNING: Debug code found!" || echo "No debug code"

# No large files accidentally added
git diff --cached --name-only | xargs -I{} sh -c 'test -f "{}" && du -m "{}"' 2>/dev/null | \
  awk '{if ($1 > 50) print "WARNING: Large file: "$0}'
```

### 5. Coverage Check
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=50 2>/dev/null || \
  echo "Coverage below 50% or pytest-cov not installed"
```

---

## Ship Steps

### Step 1: Clean Commit
```bash
# Review changes
git diff --stat HEAD
git status

# Stage thoughtfully
git add -p  # Interactive staging

# Commit với good message
git commit -m "feat: [tên tính năng ngắn gọn]

[Mô tả chi tiết hơn nếu cần]

Changes:
- [file/component]: [thay đổi gì]
- [file/component]: [thay đổi gì]

Tested: [cách đã test]"
```

### Step 2: Push
```bash
BRANCH=$(git branch --show-current)
git push -u origin "$BRANCH"
echo "Pushed: $BRANCH"
```

### Step 3: Create PR
```bash
# Nếu có GitHub CLI
if command -v gh &> /dev/null; then
    gh pr create \
      --title "[feat/fix/refactor]: [tên ngắn gọn]" \
      --body "## Changes
[Mô tả]

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual verification: [steps]

## Checklist
- [ ] No data leakage
- [ ] Reproducible results (seed set)
- [ ] Config documented
- [ ] Tests added for new features" \
      --draft
    echo "PR created (draft)"
else
    echo "gh CLI not installed. PR URL:"
    git remote get-url origin | sed 's/git@github.com:/https:\/\/github.com\//' | sed 's/\.git//'
    echo "/compare/$BRANCH"
fi
```

---

## Nếu Tests Fail — Bootstrap Test Suite

Nếu chưa có tests, tạo test suite cơ bản:
```bash
mkdir -p tests

cat > tests/test_smoke.py << 'EOF'
"""
Smoke tests for oil_forecast_tail_risk.
Chạy: pytest tests/test_smoke.py -v
"""
import sys
sys.path.insert(0, '.')

def test_config_loads():
    import config
    assert config is not None

def test_model_imports():
    from src.models.gumnet_family import *
    # Add your model class here

def test_no_syntax_errors():
    import py_compile
    import glob
    for f in glob.glob('src/**/*.py', recursive=True):
        py_compile.compile(f, doraise=True)
EOF

python -m pytest tests/test_smoke.py -v
git add tests/
git commit -m "test: add smoke test suite"
```

---

## Output Format

```markdown
## Ship Report — [branch name]
**Date**: [date]
**PR**: [URL]

### Pre-flight Results
[x] Branch check
[x] Tests: N passed, 0 failed
[x] Coverage: X%
[x] No debug code
[x] No large files

### Commits Shipped
[list of commits]

### PR Created
[URL] — Status: Draft/Ready for Review
```
