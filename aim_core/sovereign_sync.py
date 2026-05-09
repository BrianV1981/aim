#!/usr/bin/env python3
import sys

def export_to_sync():
    print("[NOTICE] Sovereign Sync JSONL export is deprecated in RAG 5.2.")
    print("         Please use `aim bake` to export native Parquet cartridges instead.")
    
def import_from_sync():
    print("[NOTICE] Sovereign Sync JSONL import is deprecated in RAG 5.2.")
    print("         Please use `aim jack-in` to mount native Parquet cartridges instead.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        export_to_sync()
    elif len(sys.argv) > 1 and sys.argv[1] == "import":
        import_from_sync()
