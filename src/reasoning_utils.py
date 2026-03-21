#!/usr/bin/env python3
import os
import json
import sys
import subprocess
import requests
import keyring

# --- CONFIG BOOTSTRAP ---
def find_aim_root():
    current = os.path.dirname(os.path.abspath(__file__))
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

def load_config():
    if not os.path.exists(CONFIG_PATH): return {}
    try:
        with open(CONFIG_PATH, 'r') as f: return json.load(f)
    except: return {}

def generate_reasoning(prompt, system_instruction="You are a helpful assistant.", brain_type="default_reasoning"):
    """
    Unified entry point for AI reasoning tasks.
    Supports Tier-specific routing (Librarian, Chancellor, Fellow, Dean).
    """
    config = load_config()
    
    # 1. Resolve Tier Configuration
    # We look for tiers[brain_type] first, then fallback to global reasoning
    tier_config = config.get('models', {}).get('tiers', {}).get(brain_type)
    if not tier_config:
        # Fallback to default reasoning logic
        provider = config.get('models', {}).get(f'{brain_type}_provider', config['models'].get('reasoning_provider', 'google'))
        model = config.get('models', {}).get(f'{brain_type}_model', config['models'].get('reasoning_model', 'gemini-flash-latest'))
        endpoint = config.get('models', {}).get(f'{brain_type}_endpoint', config['models'].get('reasoning_endpoint', ''))
    else:
        provider = tier_config.get('provider')
        model = tier_config.get('model')
        endpoint = tier_config.get('endpoint')

    # 2. Provider-Specific Execution
    if provider == "google":
        return execute_google(prompt, system_instruction, model)
    elif provider == "local" or provider == "ollama":
        return execute_ollama(prompt, system_instruction, model, endpoint)
    elif provider == "codex-cli":
        return execute_codex(prompt, system_instruction, model)
    elif provider == "openai-compat":
        return execute_openai(prompt, system_instruction, model, endpoint)
    
    return "Error: Unsupported Provider Configuration."

def execute_google(prompt, system_instruction, model):
    """Executes reasoning via the Gemini API (Cloud)."""
    api_key = keyring.get_password("aim-system", "gemini-api-key")
    if not api_key: return "Error: Gemini API Key not found in vault."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e: return f"Google Error: {e}"

def execute_ollama(prompt, system_instruction, model, endpoint):
    """Executes reasoning via Local Ollama."""
    url = endpoint or "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": f"{system_instruction}\n\nUSER: {prompt}",
        "stream": False
    }
    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json().get('response', '')
    except Exception as e: return f"Ollama Error: {e}"

def execute_codex(prompt, system_instruction, model):
    """Executes reasoning via the Codex CLI (local bridge)."""
    try:
        # Pass system instruction + prompt to codex exec
        full_prompt = f"{system_instruction}\n\nCONTEXT:\n{prompt}"
        process = subprocess.run(
            ["codex", "exec", model, full_prompt],
            capture_output=True, text=True, check=True
        )
        return process.stdout.strip()
    except Exception as e: return f"Codex Error: {e}"

def execute_openai(prompt, system_instruction, model, endpoint):
    """Executes reasoning via OpenAI-Compatible endpoint."""
    api_key = keyring.get_password("aim-system", "reasoning-api-key")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content']
    except Exception as e: return f"OpenAI Error: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(generate_reasoning(sys.argv[1]))
