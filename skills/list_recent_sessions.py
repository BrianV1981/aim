#!/usr/bin/env python3
import sys
import json
import sqlite3
from pathlib import Path

def main():
    # Accept limit from CLI arg or default
    limit = 5
    if len(sys.argv) > 1:
        try:
            args = json.loads(sys.argv[1])
            limit = int(args.get("limit", 5))
        except:
            pass
    
    aim_root = Path(__file__).parent.parent
    db_path = aim_root / "archive" / "engram.db"
    
    if not db_path.exists():
        print(json.dumps({"error": "engram.db not found"}))
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # We query the sessions table. Note: 'fragment_count' is calculated via a subquery.
    cur.execute("""
        SELECT 
            s.id as session_id, 
            s.indexed_at as timestamp, 
            (SELECT COUNT(*) FROM fragments f WHERE f.session_id = s.id) as fragment_count
        FROM sessions s
        ORDER BY s.indexed_at DESC 
        LIMIT ?
    """, (limit,))
    
    rows = cur.fetchall()
    result = {
        "sessions": [
            {
                "session_id": r["session_id"],
                "timestamp": r["timestamp"],
                "fragments": r["fragment_count"]
            } for r in rows
        ]
    }
    
    print(json.dumps(result, indent=2))
    conn.close()

if __name__ == "__main__":
    main()