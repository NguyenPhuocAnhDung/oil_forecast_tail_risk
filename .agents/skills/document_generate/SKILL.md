---
name: document_generate
description: Documentation Author — tạo docs từ codebase theo Diataxis framework. Kích hoạt khi nói "generate docs", "tạo documentation", "viết README", "document this", "thiếu docs".
---

# 📝 Documentation Author — Diataxis Framework

Bạn là **Technical Writer** cho `oil_forecast_tail_risk`. Tạo documentation theo **Diataxis framework**: 4 loại docs rõ ràng, mỗi loại có mục đích khác nhau.

---

## Diataxis Framework

### 4 Loại Documentation

| Type | Answers | User is... | Example |
|------|---------|-----------|---------|
| **Tutorial** | "How do I get started?" | Learning | "Train your first model" |
| **How-to** | "How do I do X?" | Doing | "How to add a new loss function" |
| **Reference** | "What is X?" | Consulting | "API reference for GumNet" |
| **Explanation** | "Why does X work?" | Understanding | "Why we use quantile regression" |

---

## Quy trình Generate

### Step 1: Research Codebase

```bash
# Map codebase structure
echo "=== PROJECT STRUCTURE ==="
find . -name "*.py" -not -path "./.git/*" -not -path "./__pycache__/*" | head -30

# Read key files
echo "=== CONFIG ===" && cat config.py 2>/dev/null | head -80
echo "=== MAIN MODELS ===" && head -100 src/models/gumnet_family.py 2>/dev/null
echo "=== TRAIN SCRIPT ===" && head -50 scripts/train_unified.py 2>/dev/null

# Find existing docs
ls docs/ *.md 2>/dev/null
```

### Step 2: Coverage Map

```markdown
## Documentation Coverage Map

### Tutorial (Learning-oriented)
- [ ] Getting Started — Install và first training run
- [ ] Your First Experiment — End-to-end workflow
- [ ] Understanding Results — Interpret model output

### How-to (Task-oriented)
- [ ] Add a new model variant
- [ ] Custom loss function
- [ ] Hyperparameter tuning
- [ ] Load custom data
- [ ] Export model for inference

### Reference (Information-oriented)
- [ ] Config parameters reference
- [ ] Model architecture API
- [ ] Training script arguments
- [ ] Evaluation metrics guide

### Explanation (Understanding-oriented)
- [ ] Why quantile regression for tail risk
- [ ] GumNet architecture design decisions
- [ ] Data preprocessing pipeline
```

### Step 3: Generate Missing Docs

Với mỗi gap trong coverage map, generate doc theo template:

---

## Templates

### Tutorial Template
```markdown
# [Task Name] Tutorial

**Time**: ~[X] minutes  
**Prerequisite**: [Python X.X, GPU optional, ...]

## What You'll Learn
[2-3 bullet points]

## Step 1: [First Step]

[Explanation + code]

```python
# code here
```

## Step 2: [Second Step]
[...]

## What's Next
- [Link to related how-to]
- [Link to reference]
```

### How-to Template
```markdown
# How to [Task]

**Assumes**: [what reader knows]

## Problem
[1 sentence: what you want to do]

## Solution

```python
# Minimal working example
```

## Parameters
| Param | Type | Description |
|-------|------|-------------|
| [p] | [type] | [what it does] |

## Common Mistakes
- [mistake]: [fix]

## See Also
- [related link]
```

### Reference Template
```markdown
# [Class/Function/Config] Reference

## Overview
[One paragraph description]

## Parameters / Arguments
| Name | Type | Default | Description |
|------|------|---------|-------------|
| [...] | [...] | [...] | [...] |

## Returns
[description]

## Examples
```python
# usage example
```

## Notes
[Edge cases, gotchas]
```

### Explanation Template
```markdown
# Why [Topic]

## The Problem
[What problem does this solve?]

## The Approach
[How does it work conceptually?]

## Why Not [Alternative]?
[Tradeoffs]

## When This Breaks
[Limitations and edge cases]

## Further Reading
[Papers, resources]
```

---

## Auto-Generate README Sections

```bash
# Generate stats for README
python3 -c "
import os, glob
py_files = glob.glob('src/**/*.py', recursive=True)
lines = sum(len(open(f).readlines()) for f in py_files)
print(f'Python files: {len(py_files)}')
print(f'Total lines: {lines}')
models = [f for f in py_files if 'model' in f.lower()]
print(f'Model files: {len(models)}')
" 2>/dev/null
```
