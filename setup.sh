#!/bin/bash
# A.I.M. - Actual Intelligent Memory Setup Script
# Automates venv creation and dependency installation.

set -e

echo "--- A.I.M. Installation & Setup ---"

# 1. Determine Root Directory (PORTABLE)
# This gets the absolute path of the directory where setup.sh is located
AIM_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$AIM_ROOT"

# 2. Python Environment Setup
echo "[1/4] Creating Python Virtual Environment..."
if [ -d "venv" ]; then
    echo "Found existing venv. Refreshing dependencies..."
else
    python3 -m venv venv || {
        echo "Error: Failed to create venv. Run: sudo apt install python3-venv"
        exit 1
    }
fi

# 3. Dependency Installation
echo "[2/4] Installing Dependencies..."
./venv/bin/python3 -m pip install --upgrade pip
./venv/bin/python3 -m pip install -r requirements.txt

# 4. Permissions
chmod +x scripts/*.py src/*.py scripts/*.sh 2>/dev/null || true

# 5. THE NUCLEAR ALIAS RESET
echo "[3/4] Resetting CLI Alias..."
# The alias now points to the SPECIFIC aim_cli.py in THIS folder
NEW_ALIAS="alias aim='$AIM_ROOT/scripts/aim_cli.py'"

update_shell() {
    local conf=$1
    if [ -f "$conf" ]; then
        # Force-remove ANY line containing 'alias aim=' to clear old paths
        sed -i '/alias aim=/d' "$conf"
        # Append the fresh, correct one
        echo "" >> "$conf"
        echo "# A.I.M. CLI Alias (Auto-generated)" >> "$conf"
        echo "$NEW_ALIAS" >> "$conf"
        echo "[OK] Alias updated in $(basename $conf)"
    fi
}

update_shell "$HOME/.bashrc"
update_shell "$HOME/.zshrc"
update_shell "$HOME/.profile"

echo ""
echo "--- SETUP COMPLETE ---"
echo "CRITICAL: To clear the old path, you MUST run this command now:"
echo "  unalias aim; source ~/.bashrc; hash -r"
echo ""
echo "Then type 'aim init' to start onboarding."
echo ""
