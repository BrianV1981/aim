# The 100-Turn Amnesia Killer: Video Demo Runbook

This document is the official execution playbook for recording the "Amnesia Killer" hero demo. It provides the exact setup, scripts, and shot list required to produce a highly professional, repeatable side-by-side terminal screencast demonstrating A.I.M.'s Reincarnation Protocol against a standard CLI agent.

## 1. The Concept (The Hook)
Standard LLM agents (like vanilla `gemini-cli`) suffer from "Context Rot." As you ask them to write code, change their minds, revert changes, and add complex lore over 50+ turns, their context window fills up with junk. They begin to hallucinate variables, overwrite good code, and eventually crash with `FATAL ERROR: JavaScript heap out of memory`.

A.I.M. survives this via the **Reincarnation Protocol**. When A.I.M. gets heavy, it autonomously spawns a new terminal (`tmux`), passes a mathematically compressed context delta (`LAST_SESSION_CLEAN.md`), and kills the original process to clear the RAM, creating an infinite autonomous loop.

## 2. The Setup & The Harness

To make this test 100% fair and repeatable for the video, we do not type manually. We use the **Amnesia Killer Harness** (`scripts/benchmarks/run_amnesia_killer.py`). This script uses `tmux send-keys` to simulate human typing perfectly.

### Prerequisites
1. Ensure `tmux` is installed: `sudo apt install tmux`
2. You will need a screen recording software (OBS Studio, Camtasia, or simple Windows Game Bar/macOS Screen Recording).

### The Dual-Terminal Layout
For the video, you want a side-by-side layout (or two sequential clips edited together).
1. **Left Terminal (Vanilla):** Open a `tmux` session named `demo_vanilla`. Run standard `gemini` in it.
2. **Right Terminal (A.I.M.):** Open a `tmux` session named `demo_aim`. Run `aim init` and launch `gemini`.

## 3. The Execution Script (How to record)

**Step 1: Start the Harness (Off-Screen)**
In a third, hidden terminal (perhaps on a second monitor), run the Python harness:
```bash
python3 scripts/benchmarks/run_amnesia_killer.py demo_vanilla
```
*(When you are ready to record the A.I.M. run, you will change the target to `demo_aim`)*

**Step 2: Hit Record**
Start your screen recording software, capturing just the terminal window(s).

**Step 3: Inject the Chaos**
In your hidden harness terminal, press `ENTER`. The python script will take over the visible `tmux` window and start typing the prompt character-by-character, perfectly simulating a human developer. 

Wait for the agent to finish writing code. When it stops, press `ENTER` on the harness again. 

### The Prompts
The harness automatically feeds a list of 15 chaotic, contradictory prompts designed to induce Context Rot:
1. Scaffold a Flask app with a Player class.
2. Add a massive dictionary of 50 weapons.
3. Write combat logic based on elemental damage.
4. *Contradiction:* Delete the Flask app, make it a terminal game.
5. Add an inventory limit.
6. Write a 100-line lore backstory in a comment.
7. *Contradiction:* Change elemental logic (Fire heals Water).
8. Create an Enemy class with random drops.
9. Add duplicate weapon prevention.
10. *Lore Check:* Change the villain's name in the comment.
11. Write a massive simulation loop.
12. *Contradiction:* Revert the elemental logic back to the original way.
13. Add durability drain.
14. *Amnesia Check:* Ask it what the villain's name is. (Vanilla usually fails here).
15. Refactor everything to Asyncio.

## 4. The Storyboard (Editing the Video)

When you edit the footage, follow this exact flow:

**0:00 - 0:15 | The Hook**
*   **Visual:** Show the vanilla agent failing/hallucinating on Prompt #14 or crashing completely.
*   **Overlay Text:** "This is what every agent does after 50 turns. Context collapse. Hallucinations. Death."

**0:15 - 0:30 | The Reset**
*   **Visual:** Wipe the screen. Run `aim init`. Launch A.I.M.
*   **Overlay Text:** "Enter A.I.M. (Actual Intelligent Memory)."

**0:30 - 1:30 | The Time-Lapse**
*   **Visual:** Fast-forward (400% speed) through the harness typing Prompts 1 through 10. Show the code generating flawlessly.

**1:30 - 2:00 | The Climax (The Reincarnation)**
*   **Visual:** Return to normal 1x speed. The agent realizes its context window is full (or you manually trigger it for the demo).
*   **Visual:** The viewer watches the agent run `aim reincarnate`. The terminal splits open. A brand new `tmux` window appears. 
*   **Visual:** The new agent wakes up, reads the `LAST_SESSION_CLEAN.md` movie script, and the old terminal vanishes.
*   **Overlay Text:** "The Reincarnation Protocol. Spawns a new vessel. Passes the context. Kills the original to clear RAM."

**2:00 - 2:15 | The Victory**
*   **Visual:** The harness types Prompt #14 ("What is the villain's name?"). The reincarnated agent answers flawlessly, despite not being the original process that wrote the lore.
*   **Overlay Text:** "Zero Context Rot. Infinite Autonomous Loops."

**2:15 - 2:20 | Outro**
*   **Visual:** Final CTA screen.
*   **Overlay Text:** "If this just saved you tokens or headaches → Buy Me a Coffee or sponsor on GitHub. Lifetime Delta Founder tier is open. Built by a gamer, for the trenches."

## 5. Sharing the Benchmark
Upload `scripts/benchmarks/run_amnesia_killer.py` to your repository so other developers can download it and test their own agent frameworks against the A.I.M. standard.