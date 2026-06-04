#!/bin/bash
# A.I.M. Core Contributor Installer
# curl -fsSL https://raw.githubusercontent.com/BrianV1981/aim/main/install-core.sh | bash

set -e
echo "--- A.I.M. CORE CONTRIBUTOR INSTALLER ---"

TARGET_DIR="$HOME/aim"

if [ -d "$TARGET_DIR" ]; then
    echo "[!] Directory $TARGET_DIR already exists. Pulling latest..."
    cd "$TARGET_DIR"
    git pull origin main
else
    echo "[*] Cloning A.I.M. repository..."
    git clone https://github.com/BrianV1981/aim.git "$TARGET_DIR"
    cd "$TARGET_DIR"
fi

echo "[*] Building Python Virtual Environment..."
./setup.sh

echo "[*] Linking Global Alias..."
RC_FILE="$HOME/.bashrc"
if [ -f "$HOME/.zshrc" ]; then RC_FILE="$HOME/.zshrc"; fi

# V8 Memory patch and alias
SED_ALIAS="alias aim='NODE_OPTIONS=\"--max-old-space-size=16384\" $TARGET_DIR/venv/bin/python3 $TARGET_DIR/.aim_core/aim_cli.py'"

if ! grep -q "alias aim=" "$RC_FILE"; then
    echo "" >> "$RC_FILE"
    echo "$SED_ALIAS" >> "$RC_FILE"
    echo "[SUCCESS] Alias added to $RC_FILE"
else
    echo "[OK] Alias already exists in $RC_FILE"
fi

echo ""
echo "--- INSTALLATION COMPLETE ---"
echo "CRITICAL: You MUST run this command now to load the alias:"
echo "  source $RC_FILE"
echo ""
echo "Then type 'aim init' to begin the Agentic Interview."
echo ""
