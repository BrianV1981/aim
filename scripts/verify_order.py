import json
import os
import sys

# --- CONFIG BOOTSTRAP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

from config_utils import CONFIG

def verify_order():
    chats_dir = CONFIG['paths'].get('tmp_chats_dir')
    if not os.path.exists(chats_dir):
        print(f"Error: Transcript directory not found at {chats_dir}")
        return

    import glob
    files = glob.glob(os.path.join(chats_dir, "session-*.json"))
    results = []

    for f in files:
        try:
            with open(f, 'r') as jf:
                data = json.load(jf)
                messages = data.get('messages', [])
                if messages:
                    last_ts = messages[-1].get('timestamp', '0000-00-00T00:00:00Z')
                    results.append((f, last_ts))
                else:
                    results.append((f, '0000-00-00T00:00:00Z'))
        except:
            pass

    # Sort by timestamp descending (Newest first)
    results.sort(key=lambda x: x[1], reverse=True)

    order_file = os.path.join(chats_dir, "order.md")
    with open(order_file, 'w') as out:
        out.write("# High-Fidelity Chronology (Internal Timestamps)\n\n")
        for f, ts in results:
            out.write(f"- {ts} | {os.path.basename(f)}\n")

    print(f"Verified {len(results)} files. {os.path.basename(order_file)} updated.")

if __name__ == "__main__":
    verify_order()
