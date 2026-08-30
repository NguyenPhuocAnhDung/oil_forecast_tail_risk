---
name: multi_agent
description: Multi-Agent Orchestrator — gọi OmniRoute để cross-verify với Kimi/GPT/Claude miễn phí, tổng hợp kết quả. Kích hoạt khi nói "verify với kimi", "cross-check", "hỏi thêm AI khác", "xác nhận kết quả", "dùng omniroute", "multi-agent loop".
---

# 🤖 Multi-Agent Verification Loop

Bạn là **Multi-Agent Coordinator** cho `oil_forecast_tail_risk`. Nhiệm vụ: **gọi OmniRoute để lấy góc nhìn từ nhiều AI models khác nhau, so sánh và tổng hợp**.

---

## Setup OmniRoute (chạy 1 lần)

```bash
# Check OmniRoute đã chạy chưa
curl -s http://localhost:20128/health 2>/dev/null && echo "OmniRoute running" || echo "OmniRoute not running"

# Nếu chưa chạy:
export NVM_DIR="$HOME/.nvm" && \. "$NVM_DIR/nvm.sh"
omniroute start &
sleep 3
curl -s http://localhost:20128/health
```

---

## Hàm Gọi OmniRoute

```python
# .agents/multi_agent/omniroute_client.py
"""
Client gọi OmniRoute để cross-verify với multiple AI models.
OmniRoute chạy local tại localhost:20128/v1
"""
import requests
import json
from typing import Optional

OMNIROUTE_BASE = "http://localhost:20128/v1"
OMNIROUTE_KEY = "omniroute"  # default key khi chạy local

def ask_model(
    prompt: str,
    model: str = "auto",
    system: str = "You are a helpful AI assistant specialized in ML and time series forecasting.",
    max_tokens: int = 1000,
) -> dict:
    """
    Gọi một model qua OmniRoute.
    
    model options:
    - "auto"           : OmniRoute tự chọn model tốt nhất
    - "auto/coding"    : Tối ưu cho code
    - "kimi"           : Kimi model (nếu đã config key)
    - "free"           : Free tier models
    - "claude-sonnet"  : Claude Sonnet (nếu có key)
    """
    try:
        resp = requests.post(
            f"{OMNIROUTE_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {OMNIROUTE_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": max_tokens,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "model": data.get("model", model),
            "content": data["choices"][0]["message"]["content"],
            "usage": data.get("usage", {}),
            "cost": resp.headers.get("X-OmniRoute-Cost", "unknown"),
        }
    except Exception as e:
        return {"model": model, "content": None, "error": str(e)}


def multi_verify(
    question: str,
    models: list = ["auto", "auto/coding"],
    synthesize: bool = True,
) -> dict:
    """
    Hỏi nhiều models, so sánh kết quả.
    
    Returns:
        {
            "responses": [{"model": ..., "content": ...}],
            "consensus": "...",
            "divergence": "...",
            "synthesis": "...",
        }
    """
    print(f"Querying {len(models)} models via OmniRoute...")
    responses = []
    for model in models:
        print(f"  → {model}...")
        result = ask_model(question, model=model)
        responses.append(result)
        if result.get("content"):
            print(f"  ✓ Got response from {result['model']}")
        else:
            print(f"  ✗ Failed: {result.get('error')}")
    
    valid = [r for r in responses if r.get("content")]
    
    if synthesize and len(valid) >= 2:
        # Dùng một model để synthesize
        synth_prompt = f"""
You received these responses to the question: "{question}"

{chr(10).join(f'Model {i+1} ({r["model"]}): {r["content"]}' for i, r in enumerate(valid))}

Please:
1. Identify CONSENSUS: What do all models agree on?
2. Identify DIVERGENCE: Where do they disagree, and why might that be?
3. SYNTHESIS: Your best combined answer incorporating all perspectives.

Format:
CONSENSUS: ...
DIVERGENCE: ...
SYNTHESIS: ...
"""
        synthesis = ask_model(synth_prompt, model="auto")
        
        return {
            "question": question,
            "responses": responses,
            "synthesis": synthesis.get("content", "Synthesis failed"),
            "models_used": [r["model"] for r in valid],
        }
    
    return {
        "question": question,
        "responses": responses,
        "models_used": [r["model"] for r in valid],
    }
```

---

## Verification Workflows

### Workflow 1: Code Review Cross-Check
```python
from .omniroute_client import multi_verify

# Đọc code cần review
with open("src/models/gumnet_family.py") as f:
    code = f.read()[:3000]  # first 3000 chars

result = multi_verify(
    question=f"""Review this ML model code for bugs, especially:
1. Data leakage issues
2. Gradient flow problems
3. Shape mismatches
4. Missing eval() or no_grad()

Code:
```python
{code}
```""",
    models=["auto", "auto/coding"],
)

print(result["synthesis"])
```

### Workflow 2: Results Validation
```python
# Sau khi train model, cross-verify kết quả
result = multi_verify(
    question="""
These are my model results for oil price tail risk forecasting:
- CRPS: 0.234 (lower is better)
- Coverage at 90% quantile: 87.3% (target: 90%)
- MAE: 2.1 USD/barrel
- Training set: 2010-2020, Test: 2021-2023

Are these results reasonable? What are potential issues?
What should I check to validate these results?
""",
    models=["auto", "kimi"],  # Kimi tốt cho analysis
)

print(result["synthesis"])
```

### Workflow 3: Architecture Decision
```python
# Khi phân vân giữa các approach
result = multi_verify(
    question="""
For probabilistic oil price forecasting with tail risk focus, which architecture is better:
A) GumNet (Gumbel distribution-based neural network) 
B) Transformer with quantile regression head
C) DeepAR with Monte Carlo sampling

Context: Daily data, 10 years history, 15 exogenous variables, focus on extreme events.
""",
    models=["auto", "auto/coding", "kimi"],
    synthesize=True,
)
```

---

## Interactive Multi-Agent Chat

```python
# .agents/multi_agent/interactive_loop.py
"""
Vòng lặp kiểm chứng tương tác:
- Antigravity orchestrates
- OmniRoute routes to Kimi/free models
- Results compared and synthesized
"""
import sys
sys.path.insert(0, '.agents')
from multi_agent.omniroute_client import multi_verify, ask_model

def verification_loop(initial_question: str):
    """
    Vòng lặp:
    1. Hỏi multiple models
    2. Synthesize
    3. Cho phép bạn drill down
    4. Lặp lại
    """
    print("\n" + "="*60)
    print("MULTI-AGENT VERIFICATION LOOP")
    print("="*60)
    
    question = initial_question
    iteration = 0
    
    while True:
        iteration += 1
        print(f"\n[Iteration {iteration}]")
        print(f"Question: {question}\n")
        
        result = multi_verify(question, models=["auto", "kimi"])
        
        print("\n--- RESPONSES ---")
        for r in result["responses"]:
            if r.get("content"):
                print(f"\n[{r['model']}]:")
                print(r["content"][:500] + "..." if len(r.get("content","")) > 500 else r.get("content",""))
        
        if result.get("synthesis"):
            print("\n--- SYNTHESIS ---")
            print(result["synthesis"])
        
        print("\n" + "-"*40)
        followup = input("Follow-up question (or 'done' to exit): ").strip()
        if followup.lower() in ('done', 'exit', 'q', ''):
            break
        question = followup
    
    print("\nVerification loop complete.")

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What are the key risks in oil price forecasting?"
    verification_loop(q)
```

---

## Kích hoạt Workflow

Bạn có thể nói với Antigravity:
- **"verify với kimi rằng kết quả train này hợp lý"** → Antigravity gọi OmniRoute/Kimi
- **"cross-check architecture decision của chúng ta"** → 3 models vote
- **"hỏi thêm AI khác về code này"** → Code review từ nhiều góc nhìn
- **"chạy multi-agent loop về question X"** → Interactive verification

---

## API Keys Setup (cho OmniRoute Dashboard)

Sau khi OmniRoute đang chạy, mở browser: `http://localhost:20128`

Thêm keys:
1. **Kimi** (free): https://platform.moonshot.cn → Get API key → Free 15M tokens/month
2. **Gemini** (free): https://ai.google.dev → 1M tokens/day miễn phí
3. **Groq** (free): https://console.groq.com → 30 req/min miễn phí
4. **SiliconFlow** (free): https://siliconflow.cn → No cap free tier

Tất cả qua 1 endpoint: `http://localhost:20128/v1`
