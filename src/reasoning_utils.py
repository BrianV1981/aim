import os
import json
import keyring
import requests
import sys
import subprocess
import tempfile
from google import genai

# --- CONFIGURATION (Dynamic Load) ---
def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        config_path = os.path.join(current, "core/CONFIG.json")
        if os.path.exists(config_path):
            return current
        current = os.path.dirname(current)
    return "/home/kingb/aim"

AIM_ROOT = find_aim_root(os.getcwd())
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

def generate_reasoning(prompt, system_instruction=None, brain_type="reasoning"):
    """
    Unified entry point for AI reasoning.
    brain_type can be "reasoning" or "sentinel" to use different configurations.
    """
    prefix = "reasoning" if brain_type == "reasoning" else "sentinel"
    
    provider_type = CONFIG['models'].get(f'{prefix}_provider', 'google')
    provider_model = CONFIG['models'].get(f'{prefix}_model', 'gemini-flash-latest')
    provider_endpoint = CONFIG['models'].get(f'{prefix}_endpoint', 'https://generativelanguage.googleapis.com')
    
    # 1. GOOGLE PROVIDER
    if provider_type == 'google':
        api_key = keyring.get_password("aim-system", "google-api-key")
        if not api_key: return "Error: No API Key."
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=provider_model,
                contents=prompt,
                config={ "system_instruction": system_instruction } if system_instruction else None
            )
            return response.text
        except Exception as e:
            return f"Error: {e}"

    # 2. OLLAMA PROVIDER
    elif provider_type == 'local':
        api_key = keyring.get_password("aim-system", f"{prefix}-api-key")
        headers = {}
        if api_key: headers["Authorization"] = f"Bearer {api_key}"
        try:
            url = provider_endpoint.rstrip('/')
            if not url.endswith("/api/generate"): url += "/api/generate"
            payload = { 
                "model": provider_model, 
                "prompt": prompt,
                "system": system_instruction,
                "stream": False 
            }
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            return response.json().get('response')
        except Exception as e:
            return f"Error: {e}"

    # 3. CODEX PROVIDER (ChatGPT) - Hardened for long prompts
    elif provider_type == 'codex':
        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
                tf.write(full_prompt)
                temp_path = tf.name
            
            try:
                cmd = ["codex", "exec", "--model", provider_model]
                with open(temp_path, 'r') as f:
                    result = subprocess.run(cmd, stdin=f, capture_output=True, text=True, check=True)
                return result.stdout.strip()
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            return f"Codex Error: {e}"

    # 4. OPENAI-COMPATIBLE PROVIDER
    elif provider_type == 'openai-compat':
        api_key = keyring.get_password("aim-system", f"{prefix}-api-key") or ""
        headers = {"Content-Type": "application/json"}
        if api_key: headers["Authorization"] = f"Bearer {api_key}"
        try:
            url = provider_endpoint.rstrip('/')
            if not url.endswith("/chat/completions"): url += "/chat/completions"
            messages = []
            if system_instruction: messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            payload = { "model": provider_model, "messages": messages }
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error: {e}"
    
    return "Error: Unknown provider."
