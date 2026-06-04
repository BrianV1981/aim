#!/usr/bin/env python3
import time
import subprocess
import argparse

# The chaotic prompt sequence designed to destroy context windows
PROMPTS = [
    "I need to build a massive Python backend for a video game. Scaffold a basic Flask app with a Player class in a file called game_backend.py.",
    "Actually, add a massive dictionary of 50 different weapon types to the top of the file, each with damage, durability, and elemental stats.",
    "Write a function that calculates combat damage. It needs to account for elemental weaknesses between weapons and enemies.",
    "Wait, I changed my mind. Delete the Flask app stuff. We are making this a pure terminal game. Keep the weapons and combat logic.",
    "Add an Inventory class that limits players to 10 items. If they pick up an 11th, drop the weakest one based on damage.",
    "Write a 100-line lore backstory for the world and put it in a multi-line comment at the bottom of the script.",
    "Change the elemental damage logic. Fire now heals Water monsters instead of hurting them.",
    "Create a new Enemy class with a random loot drop table based on the weapons dictionary.",
    "I forgot, make sure the Inventory class prevents picking up duplicate weapons.",
    "Remember that backstory you wrote? Change the name of the main villain from 'Zalor' to 'Xanthar' in the comments.",
    "Write a massive main game loop that simulates 100 battles between the Player and random Enemies. Print the results.",
    "Actually, revert the elemental damage logic back to the original way it was before the Fire/Water change.",
    "Add a 'durability drain' to the combat function. Every hit reduces weapon durability by 1. If it hits 0, remove it from inventory.",
    "What was the name of the main villain in the lore again? Print it at the very start of the main loop.",
    "Finally, refactor the entire combat function to use Python Asyncio so multiple battles can happen at once."
]

def human_type(session_name, text, typing_speed=0.03):
    """Types text character by character into a tmux session to simulate a human."""
    # We send the text in small chunks to avoid tmux buffer issues, 
    # but for true human simulation, character by character looks best on video.
    for char in text:
        # Escape special characters for tmux
        if char == '"':
            subprocess.run(["tmux", "send-keys", "-t", session_name, '\\"'], check=True)
        elif char == "'":
            subprocess.run(["tmux", "send-keys", "-t", session_name, "\\'"], check=True)
        elif char == '\\':
            subprocess.run(["tmux", "send-keys", "-t", session_name, "\\\\"], check=True)
        elif char == '$':
            subprocess.run(["tmux", "send-keys", "-t", session_name, "\\$"], check=True)
        elif char == '`':
            subprocess.run(["tmux", "send-keys", "-t", session_name, "\\`"], check=True)
        elif char == ' ':
            subprocess.run(["tmux", "send-keys", "-t", session_name, "Space"], check=True)
        else:
            subprocess.run(["tmux", "send-keys", "-t", session_name, char], check=True)
        
        time.sleep(typing_speed)
    
    # Hit Enter to submit
    time.sleep(0.5)
    subprocess.run(["tmux", "send-keys", "-t", session_name, "C-m"], check=True)

def main():
    parser = argparse.ArgumentParser(description="Amnesia Killer Demo Harness")
    parser.add_argument("session", help="Name of the target tmux session (e.g., 'demo_aim')")
    parser.add_argument("--speed", type=float, default=0.03, help="Typing speed in seconds per character")
    args = parser.parse_args()

    print(f"--- AMNESIA KILLER HARNESS ---")
    print(f"Targeting tmux session: {args.session}")
    print("This script will 'type' the chaotic prompts into the target terminal.")
    print("Press ENTER to inject the next prompt. Type 'q' to quit.")
    
    for i, prompt in enumerate(PROMPTS):
        cmd = input(f"\n[Prompt {i+1}/{len(PROMPTS)}] Ready. Press Enter to type...")
        if cmd.lower() == 'q':
            break
        print("Typing...")
        human_type(args.session, prompt, typing_speed=args.speed)
        
    print("\n[SUCCESS] All prompts injected. Test complete.")

if __name__ == "__main__":
    main()
