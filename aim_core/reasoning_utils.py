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
        if os.path.exists(os.path.join(current, "core/CONFIG.json")) or os.path.exists(os.path.join(current, "setup.sh")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

def load_config():
    if not os.path.exists(CONFIG_PATH): return {}
    try:
        with open(CONFIG_PATH, 'r') as f: return json.load(f)
    except: return {}

def generate_reasoning(prompt, system_instruction="You are a helpful assistant.", brain_type="default_reasoning", config=None, timeout=45):
    """
    Unified entry point for AI reasoning tasks.
    Supports Tier-specific routing (Tier 1: Session Summarizer, Tier 2: Memory Proposer, etc.).
    """
    if config is None:
        config = load_config()

    # 1. Resolve Model Configuration (Flattened)
    model_config = config.get('models', {}).get('tiers', {}).get(brain_type)
    if not model_config:
        model_config = config.get('models', {}).get(brain_type) # Fallback to top-level if not in tiers
    if not model_config:
        # Emergency Fallback to default_reasoning if requested brain_type is missing
        model_config = config.get('models', {}).get('default_reasoning', {
            "provider": "openai-compat", "model": "deepseek-chat", "endpoint": "https://api.deepseek.com/v1/chat/completions", "auth_type": "API Key"
        })
    
    provider = model_config.get('provider')
    model = model_config.get('model')
    endpoint = model_config.get('endpoint')
    auth_type = model_config.get('auth_type', 'API Key')

    # 2. Provider-Specific Execution
    if provider == "google":
        return execute_google(prompt, system_instruction, model, auth_type, timeout, brain_type=brain_type)
    elif provider == "local" or provider == "ollama":
        num_ctx = config.get('settings', {}).get('ollama_num_ctx', 32768)
        return execute_ollama(prompt, system_instruction, model, endpoint, num_ctx)
    elif provider == "codex-cli":
        return execute_codex(prompt, system_instruction, model)
    elif provider == "openai-compat":
        return execute_openai(prompt, system_instruction, model, endpoint)
    elif provider == "openrouter":
        return execute_openrouter(prompt, system_instruction, model)
    elif provider == "anthropic":
        return execute_anthropic(prompt, system_instruction, model)

    return "Error: Unsupported Provider Configuration."

def execute_google(prompt, system_instruction, model, auth_type="API Key", timeout=45, brain_type="default_reasoning"):
    """Executes reasoning via the Gemini REST API."""

    # Route 1: Standard REST API (For API Key users and default path)
    api_key = keyring.get_password("aim-system", "google-api-key")
    if not api_key: return f"Error: No Gemini API Key found in vault. Run {os.path.basename(AIM_ROOT)} tui to configure."
    
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
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return "[ERROR: CAPACITY_LOCKOUT]"
        return f"Google API Error: {e}"
    except Exception as e: return f"Google API Error: {e}"

def execute_openrouter(prompt, system_instruction, model):
    """Executes reasoning via OpenRouter."""
    api_key = keyring.get_password("aim-system", "openrouter-api-key")
    if not api_key: return "Error: OpenRouter API Key not found in vault."
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/kingb/aim",
        "X-Title": "A.I.M. Sovereign Intelligence",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        if resp.status_code != 200:
            try:
                err_msg = resp.json().get('error', {}).get('message', resp.text)
                return f"OpenRouter Error ({resp.status_code}): {err_msg}"
            except:
                resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content']
    except Exception as e: return f"OpenRouter API Exception: {e}"

def execute_anthropic(prompt, system_instruction, model):
    """Executes reasoning via Anthropic API."""
    api_key = keyring.get_password("aim-system", "anthropic-api-key")
    if not api_key: return "Error: Anthropic API Key not found in vault."

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": model,
        "max_tokens": 4000,
        "system": system_instruction,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        if resp.status_code != 200:
            try:
                err_msg = resp.json().get('error', {}).get('message', resp.text)
                return f"Anthropic Error ({resp.status_code}): {err_msg}"
            except:
                resp.raise_for_status()
        return resp.json()['content'][0]['text']
    except Exception as e: return f"Anthropic API Exception: {e}"

def execute_ollama(prompt, system_instruction, model, endpoint, num_ctx=32768):
    """Executes reasoning via Local Ollama."""
    url = endpoint or "http://127.0.0.1:11434/api/generate"
    payload = {
        "model": model,
        "prompt": f"{system_instruction}\n\nUSER: {prompt}",
        "stream": False,
        "options": {
            "num_ctx": num_ctx
        }
    }
    try:
        resp = requests.post(url, json=payload, timeout=60)
        if resp.status_code != 200:
            try:
                err_msg = resp.json().get('error', resp.text)
                return f"Ollama Error ({resp.status_code}): {err_msg}"
            except:
                resp.raise_for_status()
        return resp.json().get('response', '')
    except Exception as e: return f"Ollama Error: {e}"

def execute_codex(prompt, system_instruction, model):
    """Executes reasoning via the Codex CLI (local bridge)."""
    try:
        # Pass system instruction + prompt to codex exec
        full_prompt = f"{system_instruction}\n\nCONTEXT:\n{prompt}"
        process = subprocess.run(
            ["codex", "exec", "-m", model, full_prompt],
            capture_output=True, text=True, check=True
        )
        output = process.stdout.strip()
        # Codex output often contains headers. We look for the marker 'codex'
        if "\ncodex\n" in output:
            return output.split("\ncodex\n")[-1].split("\ntokens used\n")[0].strip()
        return output
    except subprocess.CalledProcessError as e:
        err_out = e.stderr.strip() if e.stderr else (e.stdout.strip() if e.stdout else "")
        for line in err_out.split('\n'):
            if "ERROR:" in line:
                try:
                    import json
                    err_json = json.loads(line.split("ERROR:", 1)[1].strip())
                    if "error" in err_json and "message" in err_json["error"]:
                        return f"Codex CLI Error: {err_json['error']['message']}"
                except Exception as e:
                    import sys; print(f"[DEBUG] Codex JSON parse error: {e}", file=sys.stderr)
                return f"Codex CLI Error: {line.strip()}"
        return f"Codex CLI Error: {err_out[-200:] if len(err_out)>200 else err_out}"
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
