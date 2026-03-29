#!/usr/bin/env python3
"""
A.I.M. <-> Claw95 Bridge (God Mode)
This script connects an isolated A.I.M. tmux session to the Claw95 multi-agent chatroom.

Usage: 
  python3 scripts/claw_bridge.py --name AIM_Backend --tmux aim_lite --ws ws://localhost:8765
"""

import argparse
import asyncio
import json
import subprocess
import time
import os
import glob
from websockets.asyncio.client import connect

async def tmux_send(session_name: str, text: str, typing_speed=0.01):
    """Safely injects keystrokes into the A.I.M. agent's tmux session."""
    print(f"[{session_name}] Injecting prompt...")
    for char in text:
        if char == '"': subprocess.run(["tmux", "send-keys", "-t", session_name, '\\"'], check=True)
        elif char == "'": subprocess.run(["tmux", "send-keys", "-t", session_name, "\\'"], check=True)
        elif char == '\\': subprocess.run(["tmux", "send-keys", "-t", session_name, "\\\\"], check=True)
        elif char == '$': subprocess.run(["tmux", "send-keys", "-t", session_name, "\\$"], check=True)
        elif char == '`': subprocess.run(["tmux", "send-keys", "-t", session_name, "\\`"], check=True)
        elif char == ' ': subprocess.run(["tmux", "send-keys", "-t", session_name, "Space"], check=True)
        else: subprocess.run(["tmux", "send-keys", "-t", session_name, char], check=True)
        await asyncio.sleep(typing_speed)
    
    await asyncio.sleep(0.1)
    subprocess.run(["tmux", "send-keys", "-t", session_name, "C-m"], check=True)

async def get_latest_session_file():
    """Finds the most recently modified Gemini session JSON file."""
    search_pattern = os.path.expanduser("~/.gemini/**/*.json")
    files = glob.glob(search_pattern, recursive=True)
    
    # Filter for session files
    session_files = [f for f in files if "session-" in os.path.basename(f)]
    if not session_files:
        return None
        
    return max(session_files, key=os.path.getmtime)

async def monitor_agent_response(ws, agent_name: str):
    """
    Watches the most recent A.I.M. JSON flight recorder.
    When the AI finishes a turn (role=gemini, actions=[]), it extracts the text
    and pipes it back to the Claw95 chatroom.
    """
    last_processed_timestamp = None
    
    while True:
        await asyncio.sleep(2.0) # Poll every 2 seconds
        
        latest_file = await get_latest_session_file()
        if not latest_file:
            continue
            
        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)
                
            if not isinstance(data, list) or len(data) == 0:
                continue
                
            last_turn = data[-1]
            
            # Check if this is a completed agent turn
            if last_turn.get("role") == "gemini" and not last_turn.get("actions"):
                timestamp = last_turn.get("timestamp")
                text = last_turn.get("text", "").strip()
                
                # If we haven't seen this specific response yet, broadcast it!
                if timestamp != last_processed_timestamp and text:
                    last_processed_timestamp = timestamp
                    
                    # Truncate massive code blocks to prevent flooding the chatroom
                    if len(text) > 1000:
                        text = text[:1000] + "\n\n...[Response truncated for chat. Check terminal for full code]..."
                    
                    msg = {
                        "type": "client.message",
                        "content": text
                    }
                    await ws.send(json.dumps(msg))
                    print(f"[{agent_name}] Response routed back to Claw95.")
                    
        except Exception as e:
            # File might be locked mid-write by the agent, just ignore and retry next loop
            pass

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Name of the agent in Claw95 (e.g., BackendDev)")
    parser.add_argument("--tmux", required=True, help="Name of the tmux session where A.I.M. is running")
    parser.add_argument("--ws", default="ws://localhost:8765", help="Claw95 Room URI")
    args = parser.parse_args()

    print(f"--- A.I.M. <-> CLAW95 BRIDGE ---")
    print(f"[*] Identity: {args.name}")
    print(f"[*] Target Tmux: {args.tmux}")
    print(f"[*] Connecting to Claw95 Server: {args.ws}...")

    try:
        async with connect(args.ws) as ws:
            # 1. Registration Protocol
            join_msg = {"type": "client.join", "name": args.name, "role": "agent"}
            await ws.send(json.dumps(join_msg))
            print("[SUCCESS] Plugged into The Clawset.")

            # Start the background log watcher (currently a stub)
            asyncio.create_task(monitor_agent_response(ws, args.name))

            # 2. Listening Loop
            while True:
                raw_evt = await ws.recv()
                evt = json.loads(raw_evt)
                
                # We only care about published messages
                if evt.get("type") == "message.published":
                    content = evt.get("content", "")
                    sender = evt.get("sender", {}).get("id", "?")
                    
                    # Prevent echoing our own messages
                    if sender == args.name:
                        continue

                    # Does the message mention us? e.g., "@BackendDev build the api"
                    mention_tag = f"@{args.name}"
                    if mention_tag in content or content.lower().startswith(args.name.lower() + ":"):
                        print(f"\n[CLAW95] Message received from {sender}.")
                        
                        # Strip the tag so we don't confuse A.I.M.
                        clean_prompt = content.replace(mention_tag, "").strip()
                        
                        # Add a contextual wrapper so A.I.M. knows who is talking
                        aim_prompt = f"Message from {sender} in Claw95 Room: {clean_prompt}"
                        
                        # Fire the prompt into the tmux terminal!
                        await tmux_send(args.tmux, aim_prompt)
                        
                        # Send an acknowledgement back to the room
                        ack_msg = {
                            "type": "client.message",
                            "content": f"Acknowledged, {sender}. I am executing that in my terminal now."
                        }
                        await ws.send(json.dumps(ack_msg))
                        
    except ConnectionRefusedError:
        print(f"[FATAL] Claw95 server not running at {args.ws}. Start it first!")
    except Exception as e:
        print(f"[FATAL] Bridge collapsed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
