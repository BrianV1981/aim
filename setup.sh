#!/bin/bash
# A.I.M. - Actual Intelligent Memory Setup Script
# Automates venv creation and dependency installation.

set -e

echo "--- A.I.M. Installation & Setup ---"

# 1. Determine Root Directory
AIM_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$AIM_ROOT"

# 2. Pre-flight Checks
echo "[1/5] Checking System Dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

# 3. Python Environment Setup
echo "[2/5] Creating Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv || {
        echo "Error: Failed to create virtual environment."
        echo "Tip: You may need to install the venv module: sudo apt install python3-venv"
        exit 1
    }
fi

# Verify venv structure
if [ ! -f "./venv/bin/pip" ]; then
    echo "Error: Virtual environment is broken (missing bin/pip)."
    echo "Action: Deleting broken venv and retrying..."
    rm -rf venv
    python3 -m venv venv || {
        echo "Fatal: Could not create venv. Please install python3-venv."
        exit 1
    }
fi

# 4. Dependency Installation
echo "[3/5] Installing Dependencies..."
./venv/bin/python3 -m pip install --upgrade pip
./venv/bin/python3 -m pip install -r requirements.txt

# 5. Permissions Hardening
echo "[4/5] Hardening Script Permissions..."
chmod +x scripts/*.py src/*.py scripts/*.sh 2>/dev/null || true

# 6. Alias Configuration
echo "[5/5] Configuring CLI Alias..."
ALIAS_CMD="alias aim='$AIM_ROOT/scripts/aim_cli.py'"

add_alias() {
    local shell_config=$1
    if [ ! -f "$shell_config" ]; then
        case "$(basename "$shell_config")" in
            .bashrc|.zshrc|.profile)
                touch "$shell_config"
                echo "[INFO] Created missing $shell_config"
                ;;
            *)
                return
                ;;
        esac
    fi

    if ! grep -q "alias aim=" "$shell_config"; then
        echo "" >> "$shell_config"
        echo "# A.I.M. CLI Alias" >> "$shell_config"
        echo "$ALIAS_CMD" >> "$shell_config"
        echo "[OK] Alias added to $(basename "$shell_config")"
    else
        echo "[SKIP] Alias already exists in $(basename "$shell_config")"
    fi
}

add_alias "$HOME/.bashrc"
add_alias "$HOME/.zshrc"
add_alias "$HOME/.profile"

echo ""
echo "--- SETUP COMPLETE ---"
echo "To activate the CLI immediately, run: source ~/.bashrc (or your shell config)"
echo "Then type 'aim init' to scaffold your workspace."
echo ""
