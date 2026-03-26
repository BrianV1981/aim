#!/bin/bash
# A.I.M. - Actual Intelligent Memory Setup Script
# Automates venv creation and dependency installation.

set -e

echo "--- A.I.M. Installation & Setup ---"

# 1. Determine Root Directory (PORTABLE)
# This gets the absolute path of the directory where setup.sh is located
AIM_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$AIM_ROOT"

# 2. System Dependencies (Phase 26 Hardening)
echo "[1/5] Checking OS-level dependencies for SecretStorage/keyring..."
if command -v apt-get >/dev/null; then
    echo "  Debian/Ubuntu detected. Installing dbus-x11 and libdbus-1-dev (requires sudo)..."
    sudo apt-get update -qq
    sudo apt-get install -y dbus-x11 pkg-config libdbus-1-dev >/dev/null 2>&1
    echo "  System dependencies verified."
else
    echo "  Non-Debian OS detected. Skipping apt-get dependencies."
fi

# 3. Python Environment Setup
echo "[2/5] Creating Python Virtual Environment..."
if [ -d "venv" ]; then
    echo "Found existing venv. Refreshing dependencies..."
else
    python3 -m venv venv || {
        echo "Error: Failed to create venv. Run: sudo apt install python3-venv"
        exit 1
    }
fi

# 4. Dependency Installation
echo "[3/5] Installing Dependencies..."
./venv/bin/python3 -m pip install --upgrade pip
./venv/bin/python3 -m pip install -r requirements.txt

# 5. Permissions
chmod +x scripts/*.py src/*.py scripts/*.sh 2>/dev/null || true

# 6. DYNAMIC ALIAS GENERATION (The Matrix Swarm Protocol)
echo "[4/5] Configuring Dynamic CLI Alias..."
# The alias name dynamically adapts to the folder name (e.g. 'aim-crypto' -> alias aim-crypto)
FOLDER_NAME=$(basename "$AIM_ROOT")
# For backward compatibility and simplicity, if the folder is named 'aim', the alias is 'aim'
# If the folder is named 'django-test', the alias is 'django-test'
NEW_ALIAS="alias $FOLDER_NAME='$AIM_ROOT/scripts/aim_cli.py'"

update_shell() {
    local conf=$1
    if [ -f "$conf" ]; then
        # Force-remove ANY line containing 'alias <FOLDER_NAME>=' to clear old paths
        sed -i "/alias $FOLDER_NAME=/d" "$conf"
        # Append the fresh, correct one
        echo "" >> "$conf"
        echo "# A.I.M. CLI Alias ($FOLDER_NAME)" >> "$conf"
        echo "$NEW_ALIAS" >> "$conf"
        echo "[OK] Alias '$FOLDER_NAME' configured in $(basename $conf)"
    fi
}

update_shell "$HOME/.bashrc"
update_shell "$HOME/.zshrc"
update_shell "$HOME/.profile"

echo "[5/5] Checking Skill Sandbox dependencies..."
command -v bwrap >/dev/null || echo "  ⚠️  RECOMMENDED: sudo apt install bubblewrap (for skill sandboxing)"

echo ""
echo "--- SETUP COMPLETE ---"
echo "CRITICAL: To clear the old path, you MUST run this command now:"
echo "  unalias $FOLDER_NAME 2>/dev/null; source ~/.bashrc; hash -r"
echo ""
echo "Then type '$FOLDER_NAME init' to start onboarding."
echo ""
