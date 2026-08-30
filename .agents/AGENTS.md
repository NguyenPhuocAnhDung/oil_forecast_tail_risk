# AGENTS.md — oil_forecast_tail_risk
# Hướng dẫn đầy đủ cho AI agents làm việc trong repo này

## 🏗️ Project Overview

**oil_forecast_tail_risk** — Probabilistic oil price forecasting với tail risk quantification.
- **Stack**: Python 3.10, PyTorch, pandas, scikit-learn
- **Models**: GumNet family (`src/models/gumnet_family.py`)
- **Training**: `scripts/train_unified.py`, `config.py`
- **Data**: Multivariate time series + exogenous variables

---

## 🤖 Multi-Agent Stack (ĐANG CHẠY)

### Antigravity (Orchestrator)
- Role: Đọc code, viết file, chạy commands, plan, synthesize
- Interface: Chat trực tiếp trong IDE này

### OmniRoute (AI Gateway)
- URL: `http://localhost:20128`
- Dashboard: Mở browser tại `http://localhost:20128`
- API: `http://localhost:20128/v1` (OpenAI-compatible)
- Providers: 250 providers, 90+ free, ~1.6B tokens/month

**Start OmniRoute:**
```bash
export NVM_DIR="$HOME/.nvm" && \. "$NVM_DIR/nvm.sh"
omniroute serve --no-open --daemon --port 20128
```

**Verify running:**
```bash
curl -s http://localhost:20128/health | head -1
```

### Python Client
```python
# Dùng ngay trong dự án
import sys; sys.path.insert(0, '.agents')
from multi_agent.omniroute_client import ask_model, multi_verify

# Hỏi Kimi
result = ask_model("Your question", model="kimi")

# Cross-verify với 2 models
result = multi_verify("Question", models=["auto", "kimi"])
print(result["synthesis"])
```

---

## 🛠️ Skills Available

Gọi bằng cách nói từ trigger với Antigravity:

### Strategic Planning
| Skill | Trigger | Mô tả |
|-------|---------|-------|
| `office_hours` | "office hours", "brainstorm ý tưởng", "tôi có ý tưởng" | YC-style product/research strategy session |
| `plan_ceo_review` | "ceo review", "review kế hoạch", "challenge ý tưởng" | CEO review — find better research hiding in your plan |
| `plan_eng_review` | "eng review", "architecture review", "thiết kế hệ thống" | Lock architecture, flush hidden assumptions |
| `plan_design_review` | "design review", "check UI", "UX review" | Detect AI slop, rate design quality |
| `autoplan` | "autoplan", "plan this", "lên kế hoạch tự động" | Auto-run CEO+Eng review, only ask taste decisions |
| `codex` | "write spec", "viết spec", "spec this out" | Turn vague ideas into precise executable specs |

### Build & Code
| Skill | Trigger | Mô tả |
|-------|---------|-------|
| `review` | "review code", "code review", "kiểm tra code" | Staff engineer review — find production bugs |
| `investigate` | "investigate", "debug this", "tại sao lỗi này" | Systematic root cause debugging |
| `benchmark` | "benchmark", "đo performance", "profile model" | Inference speed, memory, throughput benchmarks |

### Quality & Security
| Skill | Trigger | Mô tả |
|-------|---------|-------|
| `qa` | "qa", "test", "kiểm thử", "tìm bugs" | Test pipeline, find & fix bugs with atomic commits |
| `cso` | "security audit", "kiểm tra bảo mật", "owasp" | OWASP + STRIDE security audit |
| `ship` | "ship", "push code", "tạo PR", "deploy" | Run tests, commit, push, open PR |

### Knowledge & Learning
| Skill | Trigger | Mô tả |
|-------|---------|-------|
| `learn` | "learn this", "lưu lại", "ghi nhớ" | Save patterns, bugs, pitfalls to memory |
| `document_generate` | "generate docs", "tạo documentation", "viết README" | Generate docs using Diataxis framework |
| `retro` | "retro", "weekly review", "nhìn lại tuần" | Engineering retrospective |

### Multi-Agent
| Skill | Trigger | Mô tả |
|-------|---------|-------|
| `multi_agent` | "verify với kimi", "cross-check", "hỏi thêm AI khác" | OmniRoute cross-verification loop |

---

## 🎯 Addy Osmani Agent Skills (24 skills — `.agents/addy-skills/`)

Nguồn: [github.com/addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)

### Lifecycle Commands (8 entry points)
| Trigger | Skill | Mô tả |
|---------|-------|-------|
| "write spec", "/spec" | `spec-driven-development` | Spec before code — structured PRD |
| "plan this", "/plan" | `planning-and-task-breakdown` | Break into small atomic tasks |
| "build this", "/build" | `incremental-implementation` | One slice at a time, test-driven |
| "run tests", "/test" | `test-driven-development` | Red-green-refactor, enforced TDD |
| "review code", "/review" | `code-review-and-quality` | Five-axis review before merge |
| "simplify", "/code-simplify" | `code-simplification` | Reduce complexity, no behavior change |
| "ship it", "/ship" | `shipping-and-launch` | Pre-launch checklist, parallel personas |
| "web performance", "/webperf" | `web-performance-audit` | Core Web Vitals audit |

### Auto-Activated Skills (activate based on context)
| Context | Skill | Kích hoạt khi |
|---------|-------|---------------|
| Designing API | `api-and-interface-design` | Nói về REST, Python API, interface |
| Building UI | `frontend-ui-engineering` | HTML/CSS/JS work |
| Debug error | `debugging-and-error-recovery` | Stack trace, exception |
| Security work | `security-and-hardening` | Authentication, secrets, injection |
| CI/CD | `ci-cd-and-automation` | GitHub Actions, pipelines |
| Browser testing | `browser-testing-with-devtools` | E2E tests, Playwright |
| Observability | `observability-and-instrumentation` | Logging, metrics, tracing |
| Performance | `performance-optimization` | Profiling, benchmarks |
| Migrate code | `deprecation-and-migration` | API changes, upgrade |
| Write ADR | `documentation-and-adrs` | Architecture decisions |
| Git workflow | `git-workflow-and-versioning` | Branching, commits, tags |
| Simplify | `code-simplification` | Refactor, reduce complexity |
| Context mgmt | `context-engineering` | Long context, retrieval |
| Ideas | `idea-refine` | Brainstorm, validate |
| Interviews | `interview-me` | Requirements gathering |
| Doubts | `doubt-driven-development` | Challenge assumptions |
| Source truth | `source-driven-development` | Read source before coding |

---

## 🔄 Standard Workflows

### Workflow 1: Research New Feature
```
1. "office hours" → Brainstorm + challenge assumptions
2. "ceo review" → Find better approach
3. "eng review" → Lock architecture
4. Build code
5. "review code" → Catch bugs
6. "qa" → Test everything
7. "ship" → Create PR
8. "retro" → Learn from session
```

### Workflow 2: Debug một vấn đề
```
1. "investigate [vấn đề]" → Root cause analysis
2. Fix code
3. "qa" → Verify fix + add regression test
4. "ship" → Push fix
```

### Workflow 3: Verify kết quả với AI khác
```
1. Train model, get results
2. "verify với kimi rằng CRPS=0.234 có hợp lý không"
3. Antigravity gọi OmniRoute → Kimi phân tích
4. Cross-check với model khác
5. Synthesize → Report
```

### Workflow 4: Security check trước khi deploy
```
1. "security audit" → Full OWASP + STRIDE scan
2. Fix critical issues
3. "ship" → PR with security report
```

---

## 📦 Project Conventions

### Code Style
- Python 3.10+, type hints khuyến khích
- Docstrings: Google style
- Tests: pytest, file `tests/test_*.py`
- Commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`

### ML Conventions
- Seed luôn phải set: `torch.manual_seed(42)`, `np.random.seed(42)`
- Normalization: `scaler.fit(X_train)` ONLY, never on full data
- Time series split: chronological, NEVER random
- Models: eval mode + no_grad khi inference
- Logging: `logging` module, KHÔNG dùng `print()` trong production code

### Experiment Tracking
- Lưu config cho mỗi run
- Results trong `results_v4/`
- Logs trong `logs_v4/`
- Checkpoint naming: `{model_name}_{date}_{metric}.pth`

---

## 🔑 API Keys cho OmniRoute (Optional nhưng recommended)

Thêm vào OmniRoute Dashboard (`http://localhost:20128`):

| Provider | URL lấy key | Free tier |
|----------|------------|-----------|
| Kimi (Moonshot) | https://platform.moonshot.cn | 15M tokens/month |
| Google Gemini | https://ai.google.dev | 1M tokens/day |
| Groq | https://console.groq.com | 30 req/min |
| SiliconFlow | https://siliconflow.cn | Unlimited free |
| OpenRouter | https://openrouter.ai | $10 credit on signup |

Không có key? Dùng `model="auto"` — OmniRoute tự tìm free provider.

---

## 📂 File Structure

```
.agents/
├── AGENTS.md                    ← File này — hướng dẫn toàn bộ
├── skills.json                  ← Registry cả 2 bộ skills
├── skills/                      ← 16 gstack skills (Garry Tan)
│   ├── office_hours/
│   ├── plan_ceo_review/
│   ├── plan_eng_review/
│   ├── plan_design_review/
│   ├── autoplan/
│   ├── codex/
│   ├── review/
│   ├── investigate/
│   ├── benchmark/
│   ├── qa/
│   ├── cso/
│   ├── ship/
│   ├── learn/
│   ├── document_generate/
│   ├── retro/
│   └── multi_agent/
├── addy-skills/                 ← 24 skills (Addy Osmani) — git clone
│   └── skills/
│       ├── spec-driven-development/
│       ├── planning-and-task-breakdown/
│       ├── incremental-implementation/
│       ├── test-driven-development/
│       ├── code-review-and-quality/
│       ├── security-and-hardening/
│       ├── debugging-and-error-recovery/
│       ├── observability-and-instrumentation/
│       ├── api-and-interface-design/
│       ├── performance-optimization/
│       └── ... (24 total)
├── multi_agent/
│   └── omniroute_client.py      ← Python client cho OmniRoute
├── memory/
│   └── learnings.md             ← Accumulated project learnings
└── sessions/                    ← Office hours & autoplan sessions

TOTAL: 40 skills từ 2 repositories hàng đầu GitHub
```

---

## 📝 Quy chuẩn đặt tên bản thảo (Manuscript Title)
Khi làm việc với các kết quả thực nghiệm để viết bản thảo, luôn luôn sử dụng tên chính thức:
**"Robust Probabilistic Energy Forecasting under Geopolitical Shocks: An Adaptive Mixture of Local-Global Experts"**

