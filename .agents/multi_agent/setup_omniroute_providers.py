#!/usr/bin/env python3
"""
Auto-setup OmniRoute providers.
Chạy: python3 .agents/multi_agent/setup_omniroute_providers.py

Sẽ thêm tất cả free providers vào OmniRoute.
Bạn chỉ cần nhập API keys khi được hỏi.
"""
import requests
import json
import sys

BASE = "http://localhost:20128"
SESSION = requests.Session()


def login(password="CHANGEME"):
    r = SESSION.post(f"{BASE}/api/auth/login", json={"password": password})
    if r.status_code == 200:
        print("✅ Logged in to OmniRoute")
        return True
    print(f"❌ Login failed: {r.text[:200]}")
    return False


def add_provider(provider_id: str, name: str, api_key: str, extra: dict = None):
    """POST /api/providers để thêm 1 provider."""
    body = {"provider": provider_id, "name": name, "apiKey": api_key}
    if extra:
        body.update(extra)

    r = SESSION.post(f"{BASE}/api/providers", json=body)
    data = r.json()

    if r.status_code in (200, 201) and "error" not in data:
        print(f"  ✅ Added: {name}")
        return True
    else:
        err = data.get("error", data)
        print(f"  ⚠️  {name}: {err}")
        return False


def get_existing():
    r = SESSION.get(f"{BASE}/api/providers")
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list):
            return {p.get("provider") for p in data}
        elif isinstance(data, dict) and "connections" in data:
            return {p.get("provider") for p in data["connections"]}
    return set()


def main():
    print("\n🤖 OmniRoute Provider Auto-Setup")
    print("=" * 50)

    if not login():
        pwd = input("Enter OmniRoute password: ")
        if not login(pwd):
            sys.exit(1)

    existing = get_existing()
    print(f"Existing providers: {existing or 'none'}\n")

    # Providers định nghĩa — user sẽ nhập API keys
    providers = [
        {
            "id": "gemini",
            "name": "Google Gemini Free",
            "key_env": "GEMINI_API_KEY",
            "get_key_url": "https://ai.google.dev",
            "free_tier": "1M tokens/day",
            "priority": True,
        },
        {
            "id": "groq",
            "name": "Groq (Llama/Mixtral Free)",
            "key_env": "GROQ_API_KEY",
            "get_key_url": "https://console.groq.com",
            "free_tier": "14,400 tokens/min",
            "priority": True,
        },
        {
            "id": "openrouter",
            "name": "OpenRouter Free Models",
            "key_env": "OPENROUTER_API_KEY",
            "get_key_url": "https://openrouter.ai",
            "free_tier": "$10 credit miễn phí",
        },
        {
            "id": "siliconflow",
            "name": "SiliconFlow (Qwen/DeepSeek)",
            "key_env": "SILICONFLOW_API_KEY",
            "get_key_url": "https://siliconflow.cn",
            "free_tier": "Không giới hạn",
        },
        {
            "id": "moonshot",
            "name": "Kimi / Moonshot",
            "key_env": "MOONSHOT_API_KEY",
            "get_key_url": "https://platform.moonshot.cn",
            "free_tier": "15M tokens/month",
        },
        {
            "id": "deepseek",
            "name": "DeepSeek",
            "key_env": "DEEPSEEK_API_KEY",
            "get_key_url": "https://platform.deepseek.com",
            "free_tier": "Free credits on signup",
        },
        {
            "id": "together",
            "name": "Together AI (Free tier)",
            "key_env": "TOGETHER_API_KEY",
            "get_key_url": "https://api.together.xyz",
            "free_tier": "$5 credit miễn phí",
        },
    ]

    added = 0
    skipped = 0

    for p in providers:
        if p["id"] in existing:
            print(f"⏭️  Skip {p['name']} (already exists)")
            skipped += 1
            continue

        free = p.get("free_tier", "")
        print(f"\n📦 {p['name']}")
        print(f"   Free tier: {free}")
        print(f"   Get key:   {p['get_key_url']}")

        api_key = input(f"   Enter API key (Enter to skip): ").strip()
        if not api_key:
            print(f"   ⏭️  Skipped")
            skipped += 1
            continue

        if add_provider(p["id"], p["name"], api_key):
            added += 1
        else:
            # Thử format khác
            if add_provider(p["id"], p["name"], api_key, {"key": api_key}):
                added += 1

    print(f"\n{'='*50}")
    print(f"✅ Added: {added} providers")
    print(f"⏭️  Skipped: {skipped} providers")
    print(f"\n🚀 OmniRoute Dashboard: {BASE}")
    print(f"🔗 API Endpoint: {BASE}/v1")

    # Test với một model
    if added > 0:
        print("\n🧪 Testing connection...")
        test_r = SESSION.post(
            f"{BASE}/v1/chat/completions",
            headers={"Authorization": "Bearer omniroute"},
            json={
                "model": "auto",
                "messages": [{"role": "user", "content": "Say 'OK' in 3 words"}],
                "max_tokens": 20,
            },
            timeout=30,
        )
        if test_r.status_code == 200:
            resp = test_r.json()
            model = resp.get("model", "?")
            content = resp["choices"][0]["message"]["content"]
            print(f"   ✅ Test OK! Model: {model}")
            print(f"   Response: {content[:100]}")
        else:
            print(f"   ⚠️  Test failed: {test_r.text[:200]}")


if __name__ == "__main__":
    main()
