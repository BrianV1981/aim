#!/usr/bin/env python3
import time
import subprocess
import argparse

# The 60-Turn "Vibe Coding" sequence designed to cause structural Context Collapse
PROMPTS = [
    # Phase 1: Foundation (Turns 1-10)
    "I want to build a local algorithmic trading dashboard. Let's start with the backend. Create a FastAPI app in `main.py` with a basic health check endpoint.",
    "Add Pydantic models for an `Order`. An order needs an ID, symbol (like 'BTC'), side ('BUY' or 'SELL'), price, and quantity.",
    "Add a POST endpoint `/orders` to accept a new order and store it in an in-memory Python list for now.",
    "Add a GET endpoint `/orders` that returns all active orders.",
    "Write a pytest file `test_api.py` to prove both endpoints work correctly.",
    "Actually, an in-memory list is bad. Let's add SQLite. Install SQLAlchemy and create a `database.py` file with a local SQLite setup.",
    "Convert our Pydantic `Order` model into a SQLAlchemy DB model.",
    "Update the POST `/orders` endpoint to save the order directly to the SQLite database.",
    "Update the GET `/orders` endpoint to fetch from the SQLite database instead of the list.",
    "Update `test_api.py` to use a temporary in-memory SQLite database for testing, and prove the CRUD operations still work.",
    
    # Phase 2: Business Logic & Matching Engine (Turns 11-25)
    "We need a matching engine. Create `engine.py`. Write a function that takes a new order and checks the database to see if it can be matched with an existing order of the opposite side.",
    "Update the matching engine: A BUY order should match with a SELL order if the BUY price is greater than or equal to the SELL price.",
    "Update the matching engine to handle partial fills. If a BUY is for 10 BTC and a SELL is for 4 BTC, the SELL is filled and the BUY remains open with 6 BTC.",
    "Create a new SQLAlchemy model for `Trade`. When an order is matched, record a `Trade` in the database with the matched price and quantity.",
    "Update the POST `/orders` endpoint so it automatically runs the matching engine before returning the response.",
    "Write exhaustive tests in `test_engine.py` to prove the partial fill math is 100% accurate.",
    "Add a fee structure. Every time a `Trade` is executed, the system should deduct a 0.5% fee from the trade value. Store this fee in the `Trade` model.",
    "Write a GET endpoint `/pnl` that calculates the total volume traded and the total fees collected by the system.",
    "Add a 'Status' field to the `Order` model ('OPEN', 'PARTIAL', 'FILLED', 'CANCELED').",
    "Update the matching engine to correctly change the order status when partial or full fills occur.",
    "Add a DELETE endpoint `/orders/{id}` to cancel an open order.",
    "Update the tests to prove that canceled orders cannot be matched.",
    "Add a feature to the matching engine: if an order is older than 24 hours, it should automatically expire and be canceled.",
    "Wait, we don't have timestamps. Add a `created_at` field to both `Order` and `Trade` models.",
    "Write a test to prove the 24-hour expiration logic works.",

    # Phase 3: The Pivot - Frontend & Static Files (Turns 26-40)
    "Let's pivot to the UI. Configure FastAPI to serve a static `index.html` file from a `static` folder.",
    "Create `static/index.html`. Scaffold a clean, modern, dark-themed dashboard using Vanilla CSS. No Tailwind.",
    "Add a JavaScript file `static/app.js` and link it to the HTML.",
    "In `app.js`, write a function to fetch all open orders from `/orders` and render them in a HTML table.",
    "Add a simple HTML form to the dashboard to let me submit new BUY or SELL orders directly from the UI.",
    "Wire up the HTML form in `app.js` to send a POST request to `/orders`.",
    "Add a second HTML table to the dashboard that displays the history of executed `Trades`.",
    "Write a JS function to fetch the `/pnl` endpoint and display the total collected fees at the top of the dashboard.",
    "Add a 'Cancel' button next to every open order in the UI table that triggers the DELETE endpoint.",
    "The UI needs to refresh automatically. Set up a `setInterval` in JS to poll the `/orders` and `/pnl` endpoints every 5 seconds.",
    "Actually, polling is inefficient. Remove the `setInterval`. We need to upgrade the backend to use WebSockets.",
    "In `main.py`, add a FastAPI WebSocket endpoint `/ws`.",
    "Create a `ConnectionManager` class in Python to handle multiple active WebSocket clients.",
    "Update the POST `/orders` endpoint: whenever a new order is created, broadcast a message to all WebSocket clients.",
    "Update the matching engine: whenever a `Trade` executes, broadcast a 'TRADE_EXECUTED' message to all WebSocket clients.",

    # Phase 4: WebSockets & Complex Integration (Turns 41-50)
    "Go back to `app.js`. Remove the standard fetch calls and establish a WebSocket connection to the `/ws` endpoint.",
    "Update the JS to listen for the 'TRADE_EXECUTED' message and dynamically append the new trade to the HTML table without reloading the page.",
    "Make sure the WebSocket connection auto-reconnects if the server restarts.",
    "Add a visual 'ping' indicator to the HTML. Every time a WebSocket message is received, flash a green dot in the corner.",
    "Write a Python script `bot.py` that simulates a market. It should randomly generate and send 5 API POST requests per second to create random BTC orders.",
    "Run `bot.py` in the background and verify the UI tables are updating live via WebSockets.",
    "The UI is lagging because of too many DOM updates. Refactor the JS to batch WebSocket messages and only update the DOM once per second.",
    "Add a 'Clear Database' button to the UI that hits a new DELETE `/wipe` endpoint to reset the system.",
    "Add Python tests to ensure the WebSocket manager doesn't crash if a client disconnects unexpectedly.",
    "Update `bot.py` to occasionally send highly illogical orders (like a negative price) to ensure our API validation rejects them safely.",

    # Phase 5: The Context Crushers / Vibe Reversals (Turns 51-60)
    "Okay, big architectural change. Rename the `Order` database table to `Ledger_Entries`. You must update all SQLAlchemy models, endpoints, and the matching engine.",
    "Remember the fee structure? 0.5% is too high. Change it to a flat $2.00 fee per trade, regardless of the asset quantity.",
    "Update the `test_engine.py` math tests to prove the flat $2.00 fee works correctly.",
    "I hate the dark theme. Rewrite the `index.html` and CSS to use a bright 'Cyberpunk Neon' theme with bright pinks and yellows.",
    "The partial fill logic is broken when dealing with floating point numbers. Refactor the matching engine to use Python's `Decimal` library instead of `float`.",
    "Update all Pydantic models to strictly enforce `Decimal` for price and quantity.",
    "Our SQLite database is getting locked because `bot.py` is hitting it too fast. Refactor the database connection in `database.py` to use SQLAlchemy's async engine (aiosqlite).",
    "Because the DB is now async, you must refactor every single API endpoint in `main.py` to use `await` for database calls.",
    "Refactor the matching engine `engine.py` to be fully asynchronous.",
    "Run the entire `pytest` suite. Fix any cascading errors caused by the Asyncio database refactoring and the Decimal updates."
]

def human_type(session_name, text, typing_speed=0.03):
    """Types text character by character into a tmux session to simulate a human."""
    for char in text:
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
    
    time.sleep(0.5)
    subprocess.run(["tmux", "send-keys", "-t", session_name, "C-m"], check=True)

def main():
    parser = argparse.ArgumentParser(description="Vibe Killer 60-Turn Demo Harness")
    parser.add_argument("session", help="Name of the target tmux session (e.g., 'pro_standard')")
    parser.add_argument("--speed", type=float, default=0.03, help="Typing speed in seconds per character")
    args = parser.parse_args()

    print(f"--- VIBE KILLER 60-TURN HARNESS ---")
    print(f"Targeting tmux session: {args.session}")
    print("This script will 'type' the 60 vibe-coding prompts into the target terminal.")
    print("Press ENTER to inject the next prompt. Type 'q' to quit.")
    
    for i, prompt in enumerate(PROMPTS):
        cmd = input(f"\n[Prompt {i+1}/{len(PROMPTS)}] Ready. Press Enter to type...")
        if cmd.lower() == 'q':
            break
        print("Typing...")
        human_type(args.session, prompt, typing_speed=args.speed)
        
    print("\n[SUCCESS] All 60 prompts injected. Benchmark complete.")

if __name__ == "__main__":
    main()
