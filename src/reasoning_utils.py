import os
import json
import keyring
import requests
import sys
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

# --- PROVIDER LOGIC ---
PROVIDER_TYPE = CONFIG['models'].get('reasoning_provider', 'google') # google, local (ollama), openai-compat
PROVIDER_MODEL = CONFIG['models'].get('reasoning_model', 'gemini-flash-latest')
PROVIDER_ENDPOINT = CONFIG['models'].get('reasoning_endpoint', 'https://generativelanguage.googleapis.com')

def generate_reasoning(prompt, system_instruction=None):
    """
    Unified entry point for AI reasoning (text generation). Supports:
    - google: Gemini API
    - local: Ollama Native API
    - openai-compat: Standard OpenAI Chat API (LocalAI, vLLM, OpenAI)
    """
    
    # 1. GOOGLE PROVIDER
    if PROVIDER_TYPE == 'google':
        api_key = keyring.get_password("aim-system", "google-api-key")
        if not api_key:
            sys.stderr.write("Error: Google API Key not found in vault.\n")
            return "Error: No API Key."
        try:
            client = genai.Client(api_key=api_key)
            # Use models.generate_content for standard generation
            response = client.models.generate_content(
                model=PROVIDER_MODEL,
                contents=prompt,
                config={
                    "system_instruction": system_instruction
                } if system_instruction else None
            )
            return response.text
        except Exception as e:
            sys.stderr.write(f"Google Reasoning Error: {e}\n")
            return f"Error: {e}"

    # 2. OLLAMA PROVIDER (Native)
    elif PROVIDER_TYPE == 'local':
        try:
            # Note: Ollama uses /api/generate or /api/chat
            url = PROVIDER_ENDPOINT.rstrip('/')
            if not url.endswith("/api/generate"):
                url += "/api/generate"
            
            payload = { 
                "model": PROVIDER_MODEL, 
                "prompt": prompt,
                "system": system_instruction,
                "stream": False 
            }
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get('response')
        except Exception as e:
            sys.stderr.write(f"Ollama Reasoning Error: {e}\n")
            return f"Error: {e}"

    # 3. OPENAI-COMPATIBLE PROVIDER
    elif PROVIDER_TYPE == 'openai-compat':
        api_key = keyring.get_password("aim-system", "reasoning-api-key") or ""
        try:
            url = PROVIDER_ENDPOINT.rstrip('/')
            if not url.endswith("/chat/completions"):
                url += "/v1/chat/completions"
            
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            payload = { "model": PROVIDER_MODEL, "messages": messages }
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            sys.stderr.write(f"OpenAI-Compat Reasoning Error: {e}\n")
            return f"Error: {e}"
    
    return "Error: Unknown provider."
