import json
import os
import glob
from datetime import datetime

chats_dir = "/home/kingb/.gemini/tmp/aim/chats"
files = glob.glob(os.path.join(chats_dir, "session-*.json"))
results = []

for f in files:
    try:
        with open(f, 'r') as jf:
            data = json.load(jf)
            messages = data.get('messages', [])
            if messages:
                # Get timestamp from last message
                last_ts = messages[-1].get('timestamp', '0000-00-00T00:00:00Z')
                results.append((f, last_ts))
            else:
                results.append((f, '0000-00-00T00:00:00Z'))
    except:
        pass

# Sort by timestamp descending (Newest first)
results.sort(key=lambda x: x[1], reverse=True)

with open(os.path.join(chats_dir, "order.md"), 'w') as out:
    out.write("# High-Fidelity Chronology (Internal Timestamps)\n\n")
    for f, ts in results:
        out.write(f"- {ts} | {os.path.basename(f)}\n")

print(f"Verified {len(results)} files. order.md updated.")
