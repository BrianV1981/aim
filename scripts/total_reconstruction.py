import json
import os
import time
import random
import re
import subprocess
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin, urlparse

CLAWGLE_BIN = "/usr/bin/node projects/clawgle/scripts/clawgle.mjs"
MAP_FILE = "projects/arma3-biki/biki_pages.json"
MIRROR_DIR = "projects/arma3-biki/mirror"
ASSET_DIR = os.path.join(MIRROR_DIR, "assets")
STATE_FILE = os.path.expanduser("~/.cache/clawgle/biki_state.json")
BASE_URL = "https://community.bistudio.com"

# Memory state to track downloaded assets and avoid duplicates
DOWNLOADED_ASSETS = {} # original_url -> local_relative_path

def run_clawgle(cmd_args):
    env = os.environ.copy()
    env["CLAWGLE_STATE_FILE"] = STATE_FILE
    env["CDP_PORT"] = "9222"
    full_cmd = f"{CLAWGLE_BIN} {cmd_args}"
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, check=True, env=env)
        return result.stdout.strip()
    except Exception:
        return None

def enforce_tab_lockdown():
    """Nuclear tab sweep. Closes all tabs except Tab 0 to prevent memory leaks."""
    try:
        tabs_json = run_clawgle("tabs --json")
        if not tabs_json: return
        tabs = json.loads(tabs_json)
        if len(tabs) > 1:
            # We close from the end to avoid index shifting issues
            for i in range(len(tabs) - 1, 0, -1):
                run_clawgle(f"close {i}")
    except Exception:
        pass

def url_to_filename(url):
    """
    Derives the filename directly from the URL slug rather than the HTML Title.
    This guarantees 1:1 mathematical mapping when rewriting internal links.
    """
    if "/wiki/" in url:
        slug = url.split("/wiki/", 1)[1].split('#')[0]
        slug = slug.replace(".html", "")
        # Unquote URL encoding (e.g. %20 -> space) and sanitize
        safe_name = re.sub(r'[^\w\.-]', '_', unquote(slug))
        return f"{safe_name}.html"
    return "index.html"

def download_asset(url):
    """Downloads an asset (image/css) locally and returns the relative path."""
    if not url: return None
    
    # Normalize URL
    if url.startswith("//"): url = "https:" + url
    elif url.startswith("/") or url.startswith("../"): url = urljoin(BASE_URL, url)
    
    # Check cache
    if url in DOWNLOADED_ASSETS:
        return DOWNLOADED_ASSETS[url]
        
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename or len(filename) < 3: return None
    
    # Sanitize filename
    filename = re.sub(r'[^\w\.-]', '_', unquote(filename))
    
    local_path = os.path.join(ASSET_DIR, filename)
    relative_path = f"assets/{filename}"
    
    try:
        if not os.path.exists(local_path):
            # Fetch with a strict timeout so we don't hang on bad assets
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5.0)
            if res.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(res.content)
            else:
                return None
        
        # Save to memory map so we don't download it again
        DOWNLOADED_ASSETS[url] = relative_path
        return relative_path
    except Exception:
        return None

def setup_offline_css():
    """Injects a robust baseline Wikipedia CSS framework for offline viewing."""
    css_path = os.path.join(ASSET_DIR, "wiki_offline.css")
    if not os.path.exists(css_path):
        print("[*] Downloading Vector Wiki CSS framework...")
        try:
            res = requests.get("https://en.wikipedia.org/w/load.php?debug=false&lang=en&modules=skins.vector.styles&only=styles&skin=vector-2022", headers={"User-Agent": "Mozilla/5.0"}, timeout=10.0)
            css_content = res.text if res.status_code == 200 else ""
            
            # Additional fallback padding for offline Vector 2022
            css_content += """
            /* Offline tweaks for Vector 2022 */
            body { background-color: #f8f9fa; }
            .mw-page-container { padding: 20px; max-width: 1400px; margin: 0 auto; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
            """
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(css_content)
        except Exception as e:
            print(f"  [Error] Failed to fetch CSS: {e}")

def mirror_page(target):
    url = target['url']
    
    # Filter out noisy/broken non-content pages (Special, Talk, User, etc)
    if any(x in url for x in ["Special:", "Talk:", "Template:", "MediaWiki:", "User:"]):
        return
        
    filename = url_to_filename(url)
    filepath = os.path.join(MIRROR_DIR, filename)
    
    if os.path.exists(filepath): return

    print(f"[*] Capturing: {filename}")
    try:
        # 1. Open URL
        run_clawgle(f"open \"{url}\"")
        time.sleep(random.uniform(4.0, 7.0)) # Let Cloudflare/Javascript render
        
        # 2. Extract DOM
        html = run_clawgle("html")
        if not html or "404 Not Found" in html: return

        soup = BeautifulSoup(html, 'html.parser')
        
        # 3. Strip external scripts and old stylesheets to bypass bot protections
        for tag in soup(["script", "link"]):
            tag.decompose()
            
        # Clean up any injected Clawgle banners or global Bohemia headers
        banner = soup.find("div", id="back-to-index")
        if banner: banner.decompose()
        b_header = soup.find("div", id="bohemia-header")
        if b_header: b_header.decompose()

        # 4. Download and localize Images
        for img in soup.find_all("img"):
            if img.has_attr("srcset"):
                del img["srcset"]
            if img.has_attr("loading"):
                del img["loading"] # Remove lazy loading to ensure they render offline
                
            src = img.get("src")
            if src:
                local_src = download_asset(src)
                if local_src:
                    img["src"] = local_src

        # 5. Flawless Internal Link Rewriting
        for a in soup.find_all("a", href=True):
            href = a["href"]
            # If it's an internal wiki link...
            if ("/wiki/" in href or href.startswith("/")) and "http" not in href.replace("community.bistudio.com", ""):
                decoded_href = unquote(href)
                is_filtered = any(x in decoded_href for x in ["Special:", "Talk:", "Template:", "MediaWiki:", "User:", "File:"])
                
                if is_filtered or "action=" in decoded_href or "oldid=" in decoded_href:
                    a["href"] = "./offline_stub.html"
                else:
                    local_file = url_to_filename(href)
                    fragment = "#" + href.split("#")[1] if "#" in href else ""
                    a["href"] = f"./{local_file}{fragment}"

        # 6. Inject our offline CSS wrapper
        if soup.head:
            css_link = soup.new_tag("link", rel="stylesheet", href="./assets/wiki_offline.css")
            soup.head.append(css_link)

        # 7. Save File
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(str(soup))
            
    except Exception as e: print(f"  [Error] {filename}: {e}")
    finally:
        # Nuclear Tab Sweep to keep GPU memory usage strictly flat
        enforce_tab_lockdown()
        
    # Cooldown between hits
    time.sleep(random.uniform(1.0, 2.0))

def main():
    os.makedirs(ASSET_DIR, exist_ok=True)
    setup_offline_css()
    
    if not os.path.exists(MAP_FILE):
        print(f"[Error] Map file {MAP_FILE} not found.")
        return
        
    with open(MAP_FILE, "r") as f:
        targets = json.load(f)
        
    print(f"=== Biki Reconstruction (V3) Started: {len(targets)} Targets ===")
    
    # Minimize browser window to save rendering power
    print("[*] Minimizing browser for low-profile operation...")
    run_clawgle("minimize")
    
    count = 0
    for target in targets:
        mirror_page(target)
        count += 1
        if count % 10 == 0:
            print(f"--- Progress: {count}/{len(targets)} links processed ---")
            
    # Set the homepage redirect
    index_path = os.path.join(MIRROR_DIR, "index.html")
    with open(index_path, "w") as f:
        f.write('<html><head><meta http-equiv="refresh" content="0; url=./Main_Page.html" /></head><body>Redirecting to Biki Main Page...</body></html>')
    print(f"\n[DONE] Biki Mirror Complete. {count} links processed.")

if __name__ == "__main__":
    main()
