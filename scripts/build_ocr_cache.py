#!/usr/bin/env python3
"""
Generate OCR description caches using Moondream and MiniCPM-V via Ollama.
Mirrors the llava_7b_cache.json format: {url: description} for all 775 images.
"""
import json
import os
import hashlib
import base64
import requests
import time
import glob

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
IMAGES_DIR = "/home/kingb/locomo-visual-ground-truth/images"
MAPS_DIR = "/home/kingb/locomo-visual-ground-truth/maps"
OUT_DIR = "/home/kingb/aim-opencode/docs"

def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def generate_description(model, image_path, prompt="Describe this image in detail, including any visible text, signage, objects, people, and setting."):
    b64 = image_to_base64(image_path)
    payload = {
        "model": model,
        "prompt": prompt,
        "images": [b64],
        "stream": False,
        "options": {"temperature": 0.1}
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        data = resp.json()
        return data.get("response", "").strip()
    except Exception as e:
        print(f"  ERROR: {e}")
        return ""

def load_url_map():
    """Reconstruct URL → filename mapping."""
    url_map = {}
    # Images are stored as md5(url).jpg — we need to reverse this.
    # The maps directory might have the mapping.
    map_files = glob.glob(os.path.join(MAPS_DIR, "*.json"))
    for mf in map_files:
        with open(mf) as f:
            mapping = json.load(f)
            if isinstance(mapping, dict):
                for url, fname in mapping.items():
                    url_map[url] = fname
    return url_map

def build_reverse_map():
    """Build URL → local filename by computing md5 of all known URLs."""
    import glob as g
    # Load all known image URLs from the existing llava cache
    cache_path = "/home/kingb/locomo-visual-ground-truth/caches/llava_7b_cache.json"
    with open(cache_path) as f:
        urls = list(json.load(f).keys())
    
    url_map = {}
    missing = 0
    for url in urls:
        fname = hashlib.md5(url.encode()).hexdigest() + ".jpg"
        fpath = os.path.join(IMAGES_DIR, fname)
        if os.path.exists(fpath):
            url_map[url] = fpath
        else:
            # Try without extension
            for ext in ['.jpg', '.jpeg', '.png', '.gif']:
                alt = os.path.join(IMAGES_DIR, hashlib.md5(url.encode()).hexdigest() + ext)
                if os.path.exists(alt):
                    url_map[url] = alt
                    break
            else:
                missing += 1
    print(f"Resolved {len(url_map)} image URLs, {missing} missing")
    return url_map

def run_cache(model_name, output_name):
    print(f"\n{'='*60}")
    print(f"Generating {output_name} cache with model: {model_name}")
    print(f"{'='*60}")
    
    url_map = build_reverse_map()
    total = len(url_map)
    
    cache = {}
    for i, (url, fpath) in enumerate(url_map.items()):
        print(f"[{i+1}/{total}] {os.path.basename(fpath)}")
        desc = generate_description(model_name, fpath)
        if desc:
            cache[url] = desc
            print(f"  -> {desc[:100]}...")
        else:
            print(f"  -> EMPTY")
            cache[url] = ""
        
        # Save incrementally every 50
        if (i + 1) % 50 == 0:
            out_path = os.path.join(OUT_DIR, output_name)
            with open(out_path, "w") as f:
                json.dump(cache, f, indent=2)
            print(f"  [SAVED {i+1}/{total}]")
        
        time.sleep(0.3)  # Ollama pacing
    
    # Final save
    out_path = os.path.join(OUT_DIR, output_name)
    with open(out_path, "w") as f:
        json.dump(cache, f, indent=2)
    print(f"\nDONE: {output_name} — {len(cache)} descriptions saved to {out_path}")

if __name__ == "__main__":
    import sys
    model = sys.argv[1] if len(sys.argv) > 1 else "moondream:latest"
    output = sys.argv[2] if len(sys.argv) > 2 else f"{model.replace(':','_')}_cache.json"
    run_cache(model, output)
