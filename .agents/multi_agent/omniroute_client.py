"""
OmniRoute Python Client
=======================
Gọi 250 AI providers (90+ miễn phí) qua một endpoint duy nhất.
OmniRoute chạy local tại http://localhost:20128

    import sys; sys.path.insert(0, '.agents')
    from multi_agent.omniroute_client import multi_verify, ask_model

    # Hỏi 1 model
    result = ask_model("Explain quantile regression", model="kimi")

    # Hỏi nhiều models, so sánh
    result = multi_verify("Is this result reasonable?", models=["kimi", "auto"])
    print(result["synthesis"])
"""
import requests
import json
import time
from typing import Optional, List

OMNIROUTE_BASE = "http://localhost:20128/v1"
OMNIROUTE_KEY = "omniroute"  # default local key


def check_omniroute() -> bool:
    """Kiểm tra OmniRoute đang chạy không."""
    try:
        resp = requests.get("http://localhost:20128/v1/models", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def start_omniroute_hint():
    """In hướng dẫn start OmniRoute."""
    print("""
OmniRoute chưa chạy! Để start:

  export NVM_DIR="$HOME/.nvm" && \\. "$NVM_DIR/nvm.sh"
  omniroute start --headless &

Rồi mở browser: http://localhost:20128
Thêm API keys: Kimi, Gemini, Groq, etc.
""")


def ask_model(
    prompt: str,
    model: str = "auto",
    system: str = "You are an expert in ML, time series forecasting, and quantitative finance.",
    max_tokens: int = 1500,
    timeout: int = 60,
) -> dict:
    """
    Gọi một model qua OmniRoute.

    Args:
        prompt: Câu hỏi
        model: Model ID. Options:
               - "auto"        : OmniRoute tự chọn tốt nhất
               - "auto/coding" : Tối ưu cho code
               - "kimi"        : Kimi (cần Moonshot API key)
               - "free"        : Chỉ dùng free tier models
               - "auto/fast"   : Ưu tiên tốc độ
        system: System prompt
        max_tokens: Max output tokens

    Returns:
        dict với keys: model, content, usage, cost, error (nếu fail)
    """
    if not check_omniroute():
        start_omniroute_hint()
        return {"model": model, "content": None, "error": "OmniRoute not running"}

    headers = {
        "Authorization": f"Bearer {OMNIROUTE_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            f"{OMNIROUTE_BASE}/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": max_tokens,
            },
            timeout=timeout,
            stream=True
        )
        
        # Self-healing: if 401 Unauthorized, retry without Authorization header
        if resp.status_code == 401:
            headers_no_auth = {"Content-Type": "application/json"}
            resp = requests.post(
                f"{OMNIROUTE_BASE}/chat/completions",
                headers=headers_no_auth,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": max_tokens,
                },
                timeout=timeout,
                stream=True
            )
            
        resp.raise_for_status()
        
        # Parse streaming response
        content = ""
        model_name = model
        usage = {}
        cost = resp.headers.get("x-omniroute-response-cost") or resp.headers.get("X-OmniRoute-Cost") or "?"
        
        for line in resp.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    data_str = decoded_line[6:].strip()
                    if data_str == '[DONE]':
                        break
                    try:
                        data_json = json.loads(data_str)
                        if "model" in data_json:
                            model_name = data_json["model"]
                        if "usage" in data_json:
                            usage = data_json["usage"]
                        
                        choices = data_json.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                content += delta["content"]
                    except Exception:
                        pass
                        
        return {
            "model": model_name,
            "content": content if content else None,
            "usage": usage,
            "cost": cost,
        }
    except requests.exceptions.Timeout:
        return {"model": model, "content": None, "error": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"model": model, "content": None, "error": str(e)}


def multi_verify(
    question: str,
    models: List[str] = ["auto", "auto/coding"],
    synthesize: bool = True,
    verbose: bool = True,
) -> dict:
    """
    Hỏi nhiều models song song, so sánh và tổng hợp.

    Args:
        question: Câu hỏi cần cross-verify
        models: Danh sách models cần hỏi
        synthesize: Có tổng hợp kết quả không
        verbose: In progress không

    Returns:
        {
            "question": str,
            "responses": [{"model", "content", ...}],
            "synthesis": str (nếu synthesize=True),
            "models_used": [str],
            "consensus": str,
            "divergence": str,
        }
    """
    if verbose:
        print(f"\n🤖 Multi-Agent Verification")
        print(f"Question: {question[:100]}...")
        print(f"Models: {models}\n")

    responses = []
    for model in models:
        if verbose:
            print(f"  → Querying {model}...", end="", flush=True)
        result = ask_model(question, model=model)
        responses.append(result)
        if verbose:
            if result.get("content"):
                tokens = result.get("usage", {}).get("total_tokens", "?")
                cost = result.get("cost", "?")
                print(f" ✓ ({tokens} tokens, cost: ${cost})")
            else:
                print(f" ✗ FAILED: {result.get('error', 'unknown')}")

    valid = [r for r in responses if r.get("content")]

    result = {
        "question": question,
        "responses": responses,
        "models_used": [r["model"] for r in valid],
    }

    if not valid:
        result["synthesis"] = "All models failed. Check OmniRoute and API keys."
        return result

    if len(valid) == 1:
        result["synthesis"] = valid[0]["content"]
        result["consensus"] = valid[0]["content"]
        result["divergence"] = "Only one model responded."
        return result

    if synthesize:
        if verbose:
            print(f"\n  → Synthesizing {len(valid)} responses...")

        synth_prompt = f"""You received these responses to: "{question}"

{chr(10).join(f'=== {r["model"]} ==={chr(10)}{r["content"]}{chr(10)}' for r in valid)}

Analyze these responses:
1. CONSENSUS: What key points do ALL models agree on?
2. DIVERGENCE: Where do they differ? Which view is more defensible and why?
3. SYNTHESIS: The single best combined answer.

Format exactly as:
CONSENSUS: [key agreements]
DIVERGENCE: [key differences and your assessment]
SYNTHESIS: [your best combined answer]"""

        synth = ask_model(synth_prompt, model="auto", max_tokens=2000)

        if synth.get("content"):
            content = synth["content"]
            # Parse sections
            def extract_section(text, key):
                import re
                match = re.search(rf'{key}:\s*(.*?)(?=\n[A-Z]+:|$)', text, re.DOTALL)
                return match.group(1).strip() if match else ""

            result["consensus"] = extract_section(content, "CONSENSUS")
            result["divergence"] = extract_section(content, "DIVERGENCE")
            result["synthesis"] = extract_section(content, "SYNTHESIS") or content
        else:
            result["synthesis"] = "\n\n".join(f"[{r['model']}]: {r['content']}" for r in valid)

    return result


def verification_loop(initial_question: str = None):
    """
    Interactive multi-agent verification loop.
    Antigravity orchestrates → OmniRoute routes → Kimi/GPT/Gemini respond → Synthesize.
    """
    print("\n" + "="*60)
    print("🔄 MULTI-AGENT VERIFICATION LOOP")
    print("   Antigravity → OmniRoute → [Kimi, GPT, Gemini, ...]")
    print("="*60)

    if not check_omniroute():
        start_omniroute_hint()
        return

    if not initial_question:
        initial_question = input("\nEnter your question: ").strip()

    question = initial_question
    iteration = 0
    history = []

    while True:
        iteration += 1
        print(f"\n[Iteration {iteration}]")

        result = multi_verify(question)
        history.append(result)

        # Show results
        print("\n" + "─"*50)
        for r in result["responses"]:
            if r.get("content"):
                print(f"\n📌 [{r['model']}]:")
                print(r["content"][:600] + ("..." if len(r["content"]) > 600 else ""))

        if result.get("synthesis"):
            print("\n" + "─"*50)
            print("🔬 SYNTHESIS:")
            print(result["synthesis"])

        if result.get("consensus"):
            print(f"\n✅ CONSENSUS: {result['consensus'][:200]}")
        if result.get("divergence"):
            print(f"\n⚡ DIVERGENCE: {result['divergence'][:200]}")

        print("\n" + "─"*50)
        followup = input("Follow-up (Enter=done): ").strip()
        if not followup or followup.lower() in ('done', 'exit', 'q'):
            break
        question = followup

    print(f"\n✅ Completed {iteration} verification iterations.")
    return history


# ─── Quick examples ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
    else:
        q = "For oil price tail risk forecasting, is CRPS of 0.234 a good result?"

    # Single model
    print("\n=== Single Model (auto) ===")
    r = ask_model(q)
    print(r.get("content", r.get("error")))

    # Multi-model verification
    print("\n=== Multi-Model Verification ===")
    result = multi_verify(q, models=["auto", "auto/coding"])
    print("\nSYNTHESIS:", result.get("synthesis", ""))
