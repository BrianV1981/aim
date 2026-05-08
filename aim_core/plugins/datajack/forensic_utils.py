import os
import json
import keyring
import requests
import sys
import sqlite3
import struct
import math
from google import genai

# --- CONFIGURATION (Dynamic Load) ---
from config_utils import CONFIG, AIM_ROOT
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

# --- PROVIDER LOGIC ---
PROVIDER_TYPE = CONFIG['models'].get('embedding_provider', 'local') # google, local (ollama), openai-compat
PROVIDER_MODEL = CONFIG['models'].get('embedding', 'nomic-embed-text')
PROVIDER_ENDPOINT = CONFIG['models'].get('embedding_endpoint', 'http://127.0.0.1:11434/api/embeddings')


def summarize_massive_turn(text, model_name="qwen3.5:4b"):
    import hashlib
    import time
    import json
    import os
    import requests
    from config_utils import AIM_ROOT
    CACHE_FILE = os.path.join(AIM_ROOT, "archive", "massive_turn_cache.json")
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
        except Exception:
            pass
            
    if text_hash in cache:
        return cache[text_hash]
        
    print(f"  [RAG 4.0] Extracting Semantic Anchor for massive chunk ({len(text)} chars)...")
    
    prompt = f"Summarize the core technical actions, decisions, and facts in the following massive text block. This summary will be used for semantic vector search, so ensure key nouns and entities are preserved. Do not include conversational filler.\n\nTEXT:\n{text}"
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_ctx": 32000
        }
    }
    
    for attempt in range(3):
        try:
            res = requests.post("http://127.0.0.1:11434/api/generate", json=payload, timeout=300)
            if res.status_code == 429:
                print(f"  [API RATE LIMIT HIT] Sleeping for 60 seconds (Attempt {attempt+1}/3)...")
                time.sleep(60)
                continue
            res.raise_for_status()
            summary = res.json().get("response", "").strip()
            
            cache[text_hash] = summary
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache, f)
            time.sleep(3) # Mandatory anti-429 cooldown
            return summary
        except Exception as e:
            print(f"  [ERROR] Summarization failed: {e}")
            time.sleep(5)
            
    return text[:300] + " ... [MASSIVE TEXT OMITTED] ... " + text[-300:]


def get_embedding(text, task_type='RETRIEVAL_DOCUMENT'):
    """
    Unified entry point for embeddings. Supports:
    - google: Gemini API
    - local: Ollama Native API
    - openai-compat: Standard OpenAI Embedding API (LocalAI, vLLM, OpenAI)
    """
    if not text: return None
    
    # 1. GOOGLE PROVIDER
    if PROVIDER_TYPE == 'google':
        api_key = keyring.get_password("aim-system", "google-api-key")
        if not api_key:
            sys.stderr.write("Error: Google API Key not found in keyring.\n")
            return None
        try:
            client = genai.Client(api_key=api_key)
            result = client.models.embed_content(
                model=PROVIDER_MODEL,
                contents=text,
                config={'task_type': task_type}
            )
            return result.embeddings[0].values
        except Exception as e:
            sys.stderr.write(f"Google Embedding Error: {e}\n")
            return None

    # 2. OLLAMA PROVIDER (Native)
    elif PROVIDER_TYPE == 'local':
        import time
        max_retries = 5
        base_delay = 1
        for attempt in range(max_retries):
            try:
                payload = { "model": PROVIDER_MODEL, "prompt": text }
                response = requests.post(PROVIDER_ENDPOINT, json=payload, timeout=15)
                response.raise_for_status()
                return response.json().get('embedding')
            except Exception as e:
                if attempt == max_retries - 1:
                    sys.stderr.write(f"Ollama Embedding Error after {max_retries} attempts: {e}\n")
                    return None
                time.sleep(base_delay * (2 ** attempt))

    # 3. OPENAI-COMPATIBLE PROVIDER
    elif PROVIDER_TYPE == 'openai-compat':
        api_key = keyring.get_password("aim-system", "embedding-api-key") or ""
        try:
            # Note: Standard OpenAI format is /v1/embeddings
            url = PROVIDER_ENDPOINT if "/embeddings" in PROVIDER_ENDPOINT else f"{PROVIDER_ENDPOINT.rstrip('/')}/v1/embeddings"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = { "model": PROVIDER_MODEL, "input": text }
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            # OpenAI format: data[0].embedding
            return response.json()['data'][0]['embedding']
        except Exception as e:
            sys.stderr.write(f"OpenAI-Compat Embedding Error: {e}\n")
            return None
    
    return None

def cosine_similarity(v1, v2):
    if not v1 or not v2 or len(v1) != len(v2): return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = math.sqrt(sum(a * a for a in v1))
    magnitude2 = math.sqrt(sum(b * b for b in v2))
    if magnitude1 == 0 or magnitude2 == 0: return 0.0
    return dot_product / (magnitude1 * magnitude2)

def chunk_text(text, max_chars=2000, overlap=200, turn_based=True, window_size=6, window_overlap=1):
    """
    Splits long text into overlapping chunks.
    Uses Turn-Based Overlapping Windows by default for conversational/markdown data.
    Falls back to character-based chunking if no natural breaks are found.
    """
    if not text:
        return []
        
    if turn_based and '\n\n' in text:
        blocks = [b.strip() for b in text.split('\n\n') if b.strip()]
        chunks = []
        i = 0
        while i < len(blocks):
            window_blocks = blocks[i : i + window_size]
            chunk_content = '\n\n'.join(window_blocks)
            if chunk_content:
                chunks.append(chunk_content)
            i += (window_size - window_overlap)
            if i >= len(blocks):
                break
        return chunks
    else:
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + max_chars
            chunks.append(text[start:end])
            start += (max_chars - overlap)
        return chunks
