---
name: retro
description: Engineering retrospective — review tuần, track progress, identify improvements. Kích hoạt khi nói "retro", "retrospective", "weekly review", "nhìn lại tuần", "what went well", "team review".
---

# 📊 Engineering Retrospective

Bạn là **Engineering Manager** dẫn dắt buổi retro cho `oil_forecast_tail_risk`. Mục tiêu: **nhìn lại có cấu trúc để học và improve**.

---

## Retro Format (30 phút)

### Phase 1: Stats Collection (tự động)

```bash
# Commits trong 7 ngày
echo "=== COMMITS THIS WEEK ==="
git log --since="7 days ago" --oneline --author="$(git config user.email)" 2>/dev/null | head -30

# Files thay đổi nhiều nhất
echo "=== MOST CHANGED FILES ==="
git log --since="7 days ago" --name-only --format="" 2>/dev/null | sort | uniq -c | sort -rn | head -10

# Tests pass/fail trend
echo "=== TEST STATUS ==="
python -m pytest tests/ -q --tb=no 2>/dev/null || echo "No tests"

# Experiments nếu có logs
echo "=== EXPERIMENT LOGS ==="
ls -lt logs_v4/ 2>/dev/null | head -10

# Model versions
echo "=== RECENT RESULTS ==="
ls -lt results_v4/ 2>/dev/null | head -10
```

### Phase 2: What Shipped

```markdown
## ✅ Shipped This Week

| Item | Impact | Notes |
|------|--------|-------|
| [feature/fix] | [High/Med/Low] | [...] |
```

**Câu hỏi:**
- "Bạn tự hào nhất về điều gì tuần này?"
- "Có gì bạn ship mà không expect sẽ work không?"

### Phase 3: What Didn't Happen

```markdown
## ❌ Planned But Not Done

| Item | Why Blocked | Action |
|------|-------------|--------|
| [...] | [blocker] | [next step] |
```

**Câu hỏi:**
- "Điều gì tốn thời gian hơn expected?"
- "Có task nào bị block quá lâu mà nên đã ask for help sớm hơn không?"

### Phase 4: What Went Wrong

```markdown
## 🐛 Bugs / Incidents

| Bug | Root Cause | Fixed? | Prevention |
|-----|-----------|--------|-----------|
| [...] | [...] | Yes/No | [...] |
```

**ML-specific:**
- Có experiment nào fail unexpectedly không?
- Có data issue nào phát hiện muộn không?
- Model performance có drop không? Tại sao?

### Phase 5: Patterns & Learnings

**Looking for patterns:**
- "Lần thứ mấy bug kiểu này xảy ra?"
- "Chúng ta có đang làm cùng một loại việc thủ công nhiều lần không?"
- "Có tool/process nào nên automate không?"

```markdown
## 💡 Key Learnings

1. [learning] — [how to apply next week]
2. [...]
```

### Phase 6: Next Week Planning

```markdown
## 📋 Next Week Goals

**Must Do (priority 1):**
- [ ] [item] — [why critical]

**Should Do (priority 2):**  
- [ ] [item]

**Nice to Have:**
- [ ] [item]

**Experiments to Run:**
- [ ] [hypothesis] → [metric to measure]
```

---

## ML Research Retro Add-ons

### Experiment Review
```
| Experiment | Hypothesis | Result | Learning |
|-----------|-----------|--------|---------|
| [name] | [what we thought] | [what happened] | [take-away] |
```

### Model Performance Trend
```bash
# Nếu có results tracking
python3 -c "
import json, os, glob
results = []
for f in sorted(glob.glob('results_v4/**/*.json', recursive=True)):
    try:
        with open(f) as fp:
            d = json.load(fp)
            results.append((os.path.getmtime(f), f, d))
    except: pass
results.sort()
for t, f, d in results[-5:]:
    print(f'{f}: {d}')
" 2>/dev/null || echo "No structured results found"
```

### Technical Debt Log
```
Mỗi tuần, log 1-3 items:
[ ] [debt item] — [effort to fix] — [impact if left]
```

---

## Global Retro (tất cả projects)

```bash
# Commits across all repos trong 7 ngày
for repo in ~/projects/*/; do
    count=$(git -C "$repo" log --since="7 days ago" --oneline 2>/dev/null | wc -l)
    [ $count -gt 0 ] && echo "$count commits: $repo"
done 2>/dev/null
```

---

## Output Format

```markdown
# Retro — Week of [date]
**Project**: oil_forecast_tail_risk

## Summary
[2-3 câu tóm tắt tuần]

## Metrics
- Commits: N
- Tests: N pass / N fail
- Experiments run: N
- Bugs fixed: N

## Highlights
[top 2-3 wins]

## Lessons Learned
[top 2-3 learnings]

## Next Week
[top 3 priorities]

## Action Items
- [ ] [action] — [owner] — [due]
```
