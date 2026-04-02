#!/usr/bin/env python3
import sys
import os
import time
import subprocess

try:
    import aria2p
except ImportError:
    print("[ERROR] aria2p is not installed. Please run: pip install aria2p")
    sys.exit(1)

def ensure_aria2c_running():
    """Ensures the aria2c daemon is running in the background with RPC enabled."""
    try:
        # Check if it's already running on the default port
        import requests
        requests.get("http://localhost:6800/jsonrpc", timeout=1)
        return True
    except:
        pass

    # Start the daemon
    print("  -> Igniting local aria2c RPC daemon...")
    try:
        subprocess.Popen([
            "aria2c",
            "--enable-rpc",
            "--rpc-listen-all=false",
            "--rpc-listen-port=6800",
            "--daemon=true",
            "--seed-time=0", # Don't seed infinitely for simple downloads
            "--quiet=true"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1) # Give it a second to bind
        return True
    except FileNotFoundError:
        print("[ERROR] aria2c executable not found on the system. Please install it (e.g., sudo apt install aria2c or brew install aria2).")
        sys.exit(1)

def download_magnet(magnet_uri, dest_dir):
    ensure_aria2c_running()
    
    # Connect to the RPC interface
    aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=6800,
            secret=""
        )
    )
    
    print(f"  -> Handshaking via DHT...")
    try:
        # Add the download
        download = aria2.add_magnet(magnet_uri, options={"dir": dest_dir})
        
        # Wait for metadata to resolve
        print("  -> Resolving metadata (finding peers)...")
        while download.is_metadata:
            time.sleep(1)
            download.update()
            
        print(f"  -> Payload resolved: {download.name}")
        
        # Track progress
        while not download.is_complete and not download.has_failed:
            time.sleep(1)
            download.update()
            if download.total_length > 0:
                percent = (download.completed_length / download.total_length) * 100
                sys.stdout.write(f"\r  -> Downloading... {percent:.1f}% ({download.download_speed_string()})")
                sys.stdout.flush()
                
        print() # Clear line
        
        if download.has_failed:
            print(f"[ERROR] Torrent failed: {download.error_message}")
            sys.exit(1)
            
        # Success! Print the absolute path so the CLI can pick it up
        final_path = os.path.join(dest_dir, download.name)
        print(f"SUCCESS_PATH:{final_path}")
        
    except Exception as e:
        print(f"[ERROR] aria2p exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4 or sys.argv[1] != "download":
        print("Usage: aim_torrent.py download <magnet_link> <destination_dir>")
        sys.exit(1)
        
    magnet_uri = sys.argv[2]
    dest_dir = sys.argv[3]
    
    download_magnet(magnet_uri, dest_dir)