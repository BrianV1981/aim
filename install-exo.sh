#!/bin/bash
# A.I.M. Exoskeleton Installer (Project Wrapper)
# curl -fsSL https://raw.githubusercontent.com/BrianV1981/aim/main/install-exo.sh | bash

set -e
echo "--- A.I.M. EXOSKELETON INSTALLER ---"

TARGET_DIR="$HOME/.local/share/aim"
CURRENT_DIR=$(pwd)
CLI_NAME=$(basename "$CURRENT_DIR")

echo "[*] Step 1: Provisioning Global Engine..."
if [ -d "$TARGET_DIR" ]; then
    echo "    [OK] Engine found at $TARGET_DIR. Pulling latest..."
    cd "$TARGET_DIR"
    git pull origin main
else
    echo "    [!] Cloning Engine to $TARGET_DIR..."
    git clone https://github.com/BrianV1981/aim.git "$TARGET_DIR"
    cd "$TARGET_DIR"
fi

echo "    [*] Building Engine Virtual Environment..."
./setup.sh

echo ""
echo "[*] Step 2: Scaffolding Local Project ($CLI_NAME)..."
cd "$CURRENT_DIR"

# Clean Sweep (Severing identity)
rm -rf docs/ foundry/ workspace/ memory-wiki/ .git/
git init

# The 3-Layer Architecture Scaffolding
mkdir -p .aim_core
mkdir -p .continuity
mkdir -p .archive/raw
mkdir -p .archive/sync
mkdir -p .archive/cartridges

mkdir -p aim_os
mkdir -p memory/wiki/_ingest
mkdir -p memory/lance
mkdir -p memory/cartridges

mkdir -p workspace
mkdir -p planning-artifacts
mkdir -p foundry

# Base OS Provisioning
cp "$TARGET_DIR/assets/default_engrams/aim_os.parquet" "memory/cartridges/"

echo "    [*] Linking Local Alias ($CLI_NAME)..."
RC_FILE="$HOME/.bashrc"
if [ -f "$HOME/.zshrc" ]; then RC_FILE="$HOME/.zshrc"; fi

SED_ALIAS="alias $CLI_NAME='NODE_OPTIONS=\"--max-old-space-size=16384\" $TARGET_DIR/venv/bin/python3 $TARGET_DIR/.aim_core/aim_cli.py'"

if ! grep -q "alias $CLI_NAME=" "$RC_FILE"; then
    echo "" >> "$RC_FILE"
    echo "$SED_ALIAS" >> "$RC_FILE"
    echo "    [SUCCESS] Alias added to $RC_FILE"
else
    echo "    [OK] Alias already exists."
fi

# The Bootstrap Payload
cp "$TARGET_DIR/BOOTSTRAP.md" "$CURRENT_DIR/BOOTSTRAP.md"

echo ""
echo "--- INSTALLATION COMPLETE ---"
echo "CRITICAL: You MUST run this command now to load the alias:"
echo "  source $RC_FILE"
echo ""
echo "Then type '$CLI_NAME init' to begin your Agentic Interview."
echo ""
