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

def generate_reasoning(prompt, system_instruction="You are a helpful assistant.", brain_type="default_reasoning", config=None):
    """
    Unified entry point for AI reasoning tasks.
    Supports Tier-specific routing (Librarian, Chancellor, Fellow, Dean).
    """
    if config is None:
        config = load_config()
    
    # 1. Resolve Tier Configuration
    # We look for tiers[brain_type] first, then fallback to global reasoning
    tier_config = config.get('models', {}).get('tiers', {}).get(brain_type)
    if not tier_config:
        # Fallback to default reasoning logic
        provider = config.get('models', {}).get(f'{brain_type}_provider', config['models'].get('reasoning_provider', 'google'))
        model = config.get('models', {}).get(f'{brain_type}_model', config['models'].get('reasoning_model', 'gemini-flash-latest'))
        endpoint = config.get('models', {}).get(f'{brain_type}_endpoint', config['models'].get('reasoning_endpoint', ''))
        auth_type = config.get('models', {}).get(f'{brain_type}_auth_type', config['models'].get('reasoning_auth_type', 'API Key'))
    else:
        provider = tier_config.get('provider')
        model = tier_config.get('model')
        endpoint = tier_config.get('endpoint')
        auth_type = tier_config.get('auth_type', 'API Key')

    # 2. Provider-Specific Execution
    if provider == "google":
        return execute_google(prompt, system_instruction, model, auth_type)
    elif provider == "local" or provider == "ollama":
        return execute_ollama(prompt, system_instruction, model, endpoint)
    elif provider == "codex-cli":
        return execute_codex(prompt, system_instruction, model)
    elif provider == "openai-compat":
        return execute_openai(prompt, system_instruction, model, endpoint)
    elif provider == "openrouter":
        return execute_openrouter(prompt, system_instruction, model)
    elif provider == "anthropic":
        return execute_anthropic(prompt, system_instruction, model)
    
    return "Error: Unsupported Provider Configuration."

def execute_google(prompt, system_instruction, model, auth_type="API Key"):
    """Executes reasoning via the Gemini API (Cloud) or Native CLI bridge."""
    
    if "OAuth" in auth_type:
        # Route 1: Native Gemini CLI Bridge (Bypasses all REST API constraints)
        full_prompt = f"{system_instruction}\n\nCONTEXT:\n{prompt}"
        cmd = ["gemini", "-p", "", "-o", "json", "-y"]
        if model and model != "default":
            cmd.extend(["-m", model])
            
        try:
            import re, json
            res = subprocess.run(cmd, input=full_prompt, capture_output=True, text=True, timeout=45)
            if res.returncode != 0:
                # Attempt to parse a clean error if possible, otherwise dump the END of stderr
                # (The beginning is often polluted with harmless keychain warnings)
                stderr_lines = res.stderr.strip().split('\n')
                real_error = "\n".join(stderr_lines[-10:]) # Grab the last 10 lines
                return f"Gemini CLI Error (Code {res.returncode}): ... {real_error}"
                
            match = re.search(r"(\{.*\})", res.stdout.strip(), re.DOTALL)
            if match:
                return json.loads(match.group(1)).get("response", "Error: Empty JSON response")
            return f"Error: No JSON found in CLI output. STDERR: {res.stderr.strip()[:100]}"
        except Exception as e:
            return f"Native CLI Exception: {e}"
            
    # Route 2: Standard REST API (For pure API Key users)
    api_key = keyring.get_password("aim-system", "google-api-key")
    if not api_key: return "Error: No Gemini API Key found in vault. Run aim tui to configure."
    
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
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content']
    except Exception as e: return f"OpenRouter Error: {e}"

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
        "system": system_instruction,
        "max_tokens": 4096,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()['content'][0]['text']
    except Exception as e: return f"Anthropic Error: {e}"

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
