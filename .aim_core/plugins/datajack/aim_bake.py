#!/usr/bin/env python3
import os
import sys
import argparse
import json
from pathlib import Path

# Fix python path for local imports
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if aim_root not in sys.path:
    sys.path.append(aim_root)
src_dir = os.path.join(aim_root, ".aim_core")
if src_dir not in sys.path:
    sys.path.append(src_dir)

def bake_cartridge(target_dir, output_file, author="Unknown", version="1.0.0", description="No description provided."):
    print(f"\n--- A.I.M. DATAJACK FOUNDRY (Native Parquet ROM) ---")

    import urllib.request
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/", timeout=2)
    except Exception:
        print("[ERROR] Ollama is not running or unreachable at http://127.0.0.1:11434/")
        print("        You must start Ollama before baking a cartridge to generate embeddings.")
        print("        Run `ollama serve` in a separate terminal and try again.")
        sys.exit(1)

    if not os.path.isdir(target_dir):
        print(f"[ERROR] Target directory not found: {target_dir}")
        sys.exit(1)

    if output_file.endswith(".engram"):
        output_file = output_file.replace(".engram", ".parquet")
    elif not output_file.endswith(".parquet"):
        output_file += ".parquet"

    output_path = os.path.abspath(output_file)

    from forensic_utils import chunk_text, get_embedding
    import pyarrow as pa
    import pyarrow.parquet as pq
    from datetime import datetime

    print(f"[*] Ingesting raw materials from: {target_dir}")
    fragments_added = 0
    records = []
    
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.md', '.markdown', '.txt', '.py', '.rs', '.js', '.ts', '.rst')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                except Exception as e:
                    continue
                
                if not text.strip(): continue
                
                chunks = chunk_text(text)
                filename = os.path.basename(file_path)
                
                session_id = f"factory-{filename}"
                
                for chunk in chunks:
                    vec = get_embedding(chunk)
                    if vec and len(vec) == 768:
                        records.append({
                            "fragment_id": fragments_added + 1,
                            "session_id": session_id,
                            "type": "factory_export",
                            "content": chunk,
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "metadata": json.dumps({"author": author, "version": version, "description": description}),
                            "parent_id": None,
                            "source_db": os.path.basename(output_path),
                            "vector": vec
                        })
                        fragments_added += 1
                        
    if fragments_added == 0:
        print("[ERROR] No valid documentation files found in target directory.")
        sys.exit(1)
        
    print(f"[*] Calculated embeddings for {fragments_added} semantic chunks.")
    print(f"[*] Compiling Native Parquet ROM...")
    try:
        schema = pa.schema([
            pa.field("fragment_id", pa.int64()),
            pa.field("session_id", pa.string()),
            pa.field("type", pa.string()),
            pa.field("content", pa.string()),
            pa.field("timestamp", pa.string()),
            pa.field("metadata", pa.string()),
            pa.field("parent_id", pa.int64()),
            pa.field("source_db", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), 768))
        ])
        
        table = pa.Table.from_pylist(records, schema=schema)
        pq.write_table(table, output_path)
        print(f"[SUCCESS] Native Parquet ROM forged successfully: {output_path}")
    except Exception as e:
        print(f"[ERROR] Failed to compile cartridge: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Bake an isolated atomic .parquet ROM cartridge.")
    parser.add_argument("directory", help="The raw documentation directory to vectorize")
    parser.add_argument("output", help="The name of the resulting .parquet file (e.g. pytest.parquet)")
    parser.add_argument("--author", help="Author of the cartridge", default="Unknown")
    parser.add_argument("--version", help="Version of the cartridge", default="1.0.0")
    parser.add_argument("--description", help="Description of the cartridge", default="No description provided.")
    args = parser.parse_args()
    bake_cartridge(args.directory, args.output, args.author, args.version, args.description)

if __name__ == "__main__":
    main()
