# AI Agent Stack — oil_forecast_tail_risk

## 🚀 Auto-Activation: Mọi cuộc hội thoại mới

Khi bắt đầu HỌP TÁC MỌI PHIÊN LÀM VIỆC, agent TỰ ĐỘNG:

1. **Đọc** `.agents/AGENTS.md` để nắm bộ skills hiện có
2. **Kích hoạt** `using-superpowers` skill từ Superpowers repo
3. **Load** context từ `.agents/memory/learnings.md` (project learnings)
4. **Kiểm tra** OmniRoute tại `http://localhost:20128` có sẵn không

## 📦 373+ Skills — 6 Repos GitHub Hàng Đầu

| Repo | Skills | Stars | Tác giả |
|------|--------|-------|---------|
| **gstack** | 16 | 114k | Garry Tan (YC CEO) |
| **agent-skills** | 24 | trending | Addy Osmani (Chrome VP) |
| **ECC** | 278 | 211k | affaan-m |
| **Superpowers** | 14 | trending | obra/Prime Radiant |
| **mattpocock/skills** | 41 | trending | Matt Pocock |
| **Anthropic official** | 17 | official | Anthropic |

## 🤖 Multi-Agent Stack

- **Antigravity** — Orchestrator chính, đọc code, viết file, chạy commands
- **OmniRoute** (`http://localhost:20128`) — AI Gateway: 250 providers, 90+ free
- **OmniRoute Python Client** — `.agents/multi_agent/omniroute_client.py`

## 🎯 Trigger Phrases (Tiếng Việt + English)

### Strategic
- `"office hours"` → YC brainstorm session
- `"ceo review"` → Challenge strategy
- `"eng review"` → Lock architecture
- `"autoplan"` → Full planning pipeline

### Build & Code  
- `"write spec"` / `"/spec"` → Spec-driven development
- `"build this"` / `"/build"` → Incremental implementation
- `"run tests"` / `"/test"` → TDD workflow
- `"review code"` / `"/review"` → 5-axis code review
- `"simplify"` → Reduce complexity

### Debug & QA
- `"investigate [vấn đề]"` → Root cause analysis
- `"diagnose this bug"` → Matt Pocock debug methodology
- `"qa"` → Full test pipeline

### Ship
- `"ship it"` / `"/ship"` → Pre-launch checklist
- `"ship"` → Commit + push + PR

### Multi-AI Verification
- `"verify với kimi"` → OmniRoute → Kimi analysis
- `"cross-check"` → 3 models vote
- `"hỏi thêm AI khác"` → Multi-model review

## 🔑 Thêm API Keys cho OmniRoute (Free!)

```bash
python3 .agents/multi_agent/setup_omniroute_providers.py
```

| Provider | URL | Free |
|----------|-----|------|
| Gemini | https://ai.google.dev | 1M tokens/ngày |
| Groq | https://console.groq.com | 14K tokens/phút |
| Kimi | https://platform.moonshot.cn | 15M tokens/tháng |
| SiliconFlow | https://siliconflow.cn | Không giới hạn |

## 📂 Cấu Trúc

```
.agents/
├── AGENTS.md                 ← Hướng dẫn tổng thể
├── GEMINI.md                 ← File này — auto-activation
├── skills.json               ← Registry 6 bộ skills
├── skills/                   ← gstack (16)
├── addy-skills/              ← Addy Osmani (24)
├── ecc/                      ← ECC (278)
├── superpowers/              ← Superpowers (14)
├── mattpocock-skills/        ← Matt Pocock (41)
├── anthropic-skills/         ← Anthropic (17)
└── multi_agent/
    ├── omniroute_client.py
    └── setup_omniroute_providers.py
```
