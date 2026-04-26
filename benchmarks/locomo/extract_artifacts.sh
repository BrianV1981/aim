#!/bin/bash
echo "👀 Watching locomo embedding progress..."
while ! grep -q "Finished embedding" benchmarks/locomo/build_cartridge.log; do
    sleep 5
done

echo "✅ Embedding complete! Forging cartridge..."
../../venv/bin/python benchmarks/locomo/pack_locomo_cartridge.py

echo "📦 Securing artifacts to permanent project root..."
# 1. Create persistent folders in the project root
mkdir -p ../../datasets/locomo/md
mkdir -p ../../engrams

# 2. Extract the .md flight recorders
cp -r benchmarks/locomo/data/flight_recorders/* ../../datasets/locomo/md/

# 3. Extract the final .engram cartridge
cp benchmarks/locomo/data/locomo.engram ../../engrams/

echo "🔒 DATA SECURED SUCCESSFULLY. It is now safe to clean up the worktree."
