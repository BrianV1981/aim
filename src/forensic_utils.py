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

PROVIDER = CONFIG['models'].get('embedding_provider', 'local')
GOOGLE_MODEL = CONFIG['models']['embedding']
LOCAL_MODEL = CONFIG['models'].get('local_embedding', 'nomic-embed-text')

# API Client (Google)
API_KEY = keyring.get_password("aim-system", "google-api-key")
google_client = None
if API_KEY:
    google_client = genai.Client(api_key=API_KEY)

def get_embedding(text, task_type='RETRIEVAL_DOCUMENT'):
    """
    Returns an embedding vector for the provided text using the configured provider.
    Handles fallbacks and silent failures to avoid breaking hooks.
    """
    if PROVIDER == 'google' and google_client:
        try:
            result = google_client.models.embed_content(
                model=GOOGLE_MODEL,
                contents=text,
                config={'task_type': task_type}
            )
            return result.embeddings[0].values
        except Exception as e:
            # If Google fails (e.g., quota), we can optionally fallback to local or just return None
            # For now, let's just log to stderr and fail gracefully
            sys.stderr.write(f"Google Embedding Error: {e}\n")
            return None

    elif PROVIDER == 'local':
        try:
            # Call Ollama API (Local HTTP)
            url = "http://localhost:11434/api/embeddings"
            payload = {
                "model": LOCAL_MODEL,
                "prompt": text
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json().get('embedding')
        except Exception as e:
            sys.stderr.write(f"Local (Ollama) Embedding Error: {e}\n")
            return None
    
    return None
