#!/usr/bin/env python3
"""Ping session 0 every 30 minutes with MiniCPM-V OCR cache build status."""
import subprocess, time

LOG_FILE = "/tmp/ocr_minicpm.log"
STATUS_FILE = "/tmp/ocr_status.txt"
INTERVAL = 30 * 60

result = subprocess.run(["tmux", "list-sessions", "-F", "#{session_name}"], capture_output=True, text=True)
sessions = [s for s in result.stdout.strip().split('\n') if s]
target = sessions[0] if sessions else "0"

while True:
    try:
        with open(LOG_FILE) as f:
            lines = f.readlines()
        last = [l.strip() for l in lines if '[' in l and '/774]' in l]
        if last:
            progress = last[-1]
            num = int(progress.split('[')[1].split('/')[0])
            pct = num / 774 * 100
            msg = f"MiniCPM-V OCR: {num}/774 ({pct:.0f}%)"
        else:
            msg = "MiniCPM-V OCR: starting..."
            num = 0
    except:
        msg = "MiniCPM-V OCR: checking..."
        num = 0

    subprocess.run(["tmux", "display-message", "-t", target, msg])
    with open(STATUS_FILE, "w") as f:
        f.write(msg)

    if num >= 774:
        done_msg = "MiniCPM-V OCR cache COMPLETE. Both caches in aim-opencode/docs/"
        subprocess.run(["tmux", "display-message", "-t", target, done_msg])
        with open(STATUS_FILE, "w") as f:
            f.write(done_msg)
        break

    time.sleep(INTERVAL)
