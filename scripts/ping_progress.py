#!/usr/bin/env python3
"""Ping tmux session 1 every 60s with OCR cache progress."""
import subprocess, time

LOG_FILE = "/tmp/ocr_minicpm.log"
TARGET = "1"
INTERVAL = 60

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

    with open("/tmp/ping.txt", "w") as f:
        f.write(msg)
    subprocess.run(["tmux", "load-buffer", "/tmp/ping.txt"])
    subprocess.run(["tmux", "paste-buffer", "-t", TARGET])
    subprocess.run(["tmux", "send-keys", "-t", TARGET, "Enter"])

    if num >= 774:
        done = "MiniCPM-V OCR cache COMPLETE."
        with open("/tmp/ping.txt", "w") as f:
            f.write(done)
        subprocess.run(["tmux", "load-buffer", "/tmp/ping.txt"])
        subprocess.run(["tmux", "paste-buffer", "-t", TARGET])
        subprocess.run(["tmux", "send-keys", "-t", TARGET, "Enter"])
        break

    time.sleep(INTERVAL)
