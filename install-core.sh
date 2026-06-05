#!/bin/bash
# A.I.M. Core Contributor Installer
# curl -fsSL https://raw.githubusercontent.com/BrianV1981/aim/main/install-core.sh | bash

set -e
echo "--- A.I.M. CORE CONTRIBUTOR INSTALLER ---"

CURRENT_DIR=$(pwd)
CLI_NAME=$(basename "$CURRENT_DIR")

echo "[*] Step 1: Provisioning Local Operating System..."

# Clone the engine directly into a temporary hidden folder to avoid empty directory conflicts
git clone https://github.com/BrianV1981/aim.git .aim_temp_clone
cd .aim_temp_clone

echo "    [*] Building Engine Virtual Environment..."
./setup.sh

# Move everything out of the temp folder into the current directory
echo "[*] Step 2: Scaffolding Sovereign Environment..."
shopt -s dotglob
mv * ../
cd ..
rm -rf .aim_temp_clone
shopt -u dotglob

# Base OS Provisioning (Moving the pre-baked DB to the active layer)
mkdir -p memory/lance
cp -r assets/default_lance/* memory/lance/

echo "    [*] Linking Local Alias ($CLI_NAME)..."
RC_FILE="$HOME/.bashrc"
if [ -f "$HOME/.zshrc" ]; then RC_FILE="$HOME/.zshrc"; fi

SED_ALIAS="alias $CLI_NAME='NODE_OPTIONS=\"--max-old-space-size=16384\" $CURRENT_DIR/venv/bin/python3 $CURRENT_DIR/.aim_core/aim_cli.py'"

if ! grep -q "alias $CLI_NAME=" "$RC_FILE"; then
    echo "" >> "$RC_FILE"
    echo "$SED_ALIAS" >> "$RC_FILE"
    echo "    [SUCCESS] Alias added to $RC_FILE"
else
    echo "    [OK] Alias already exists."
fi

echo ""
echo "--- INSTALLATION COMPLETE ---"
echo "CRITICAL: You MUST run this command now to load the alias:"
echo "  source $RC_FILE"
echo ""
echo "You are a Core Contributor. The .git history and developer folders (tests/, benchmarks/) have been preserved."
echo "To set up your identity, run:"
echo "  $CLI_NAME init"
echo ""