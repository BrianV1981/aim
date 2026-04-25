#!/bin/bash
# A.I.M. - Actual Intelligent Memory Setup Script
# Automates venv creation and dependency installation.

set -e

echo "--- A.I.M. Installation & Setup ---"

# 1. Determine Root Directory (PORTABLE)
AIM_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$AIM_ROOT"

# Check if we are in the Core Framework Repo or an Exoskeleton Target Project
IS_CORE=false
if git config --get remote.origin.url | grep -qi "BrianV1981/aim"; then
    IS_CORE=true
fi

if [ "$IS_CORE" = true ]; then
    echo "  Core A.I.M. framework repository detected."
    # If the user wishes, they could move it, but for now we keep it here.
    # To fully support decoupling, the engine can be synced globally.
    GLOBAL_AIM_DIR="$HOME/.local/share/aim"
    if [ "$AIM_ROOT" != "$GLOBAL_AIM_DIR" ]; then
        echo "  (Optional) For full Exoskeleton deployment, consider cloning this repo to $GLOBAL_AIM_DIR."
    fi
else
    echo "  Target project repository detected (Exoskeleton deployment)."
    GLOBAL_AIM_DIR="$HOME/.local/share/aim"
    if [ -d "$GLOBAL_AIM_DIR" ]; then
        echo "  Global Engine found at $GLOBAL_AIM_DIR. Linking..."
        AIM_ROOT="$GLOBAL_AIM_DIR"
    else
        echo "  [WARNING] Global Engine not found at $GLOBAL_AIM_DIR."
        echo "  Running Engine locally from this repository."
    fi
fi

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
cd "$AIM_ROOT"
if [ -d "venv" ]; then
    echo "Found existing venv in $AIM_ROOT. Refreshing dependencies..."
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
chmod +x aim_core/*.py aim_core/*.sh 2>/dev/null || true

# 6. DYNAMIC ALIAS GENERATION (The Matrix Swarm Protocol)
echo "[4/5] Configuring Dynamic CLI Alias..."
# The alias name dynamically adapts to the original folder name where setup.sh was executed
if [ "$IS_CORE" = true ]; then
    FOLDER_NAME="aim"
else
    # In a target project, alias matches the project folder name
    # We must grab it from where setup.sh was run originally
    ORIGINAL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    FOLDER_NAME=$(basename "$ORIGINAL_DIR")
fi

NEW_ALIAS="alias $FOLDER_NAME='$AIM_ROOT/aim_core/aim_cli.py'"

update_shell() {
    local conf=$1
    if [ -f "$conf" ]; then
        local appended=false
        
        if ! grep -q "export NODE_OPTIONS=\"--max-old-space-size=16384\"" "$conf"; then
            echo "" >> "$conf"
            echo "# V8 Memory Patch for A.I.M." >> "$conf"
            echo "export NODE_OPTIONS=\"--max-old-space-size=16384\"" >> "$conf"
            appended=true
        fi
        
        if ! grep -q "alias $FOLDER_NAME=" "$conf"; then
            if [ "$appended" = false ]; then
                echo "" >> "$conf"
            fi
            echo "# A.I.M. CLI Alias ($FOLDER_NAME)" >> "$conf"
            echo "$NEW_ALIAS" >> "$conf"
            appended=true
        fi
        
        if [ "$appended" = true ]; then
            echo "[OK] Alias '$FOLDER_NAME' and/or V8 Patch added to $(basename "$conf")"
        else
            echo "[OK] Alias '$FOLDER_NAME' and V8 Patch already exist in $(basename "$conf")"
        fi
    fi
}

update_shell "$HOME/.bashrc"
update_shell "$HOME/.zshrc"
update_shell "$HOME/.profile"

echo "[5/5] Checking Skill Sandbox dependencies..."
command -v bwrap >/dev/null || echo "  ⚠️  RECOMMENDED: sudo apt install bubblewrap (for skill sandboxing)"

echo ""
echo "--- SETUP COMPLETE ---"
echo "CRITICAL: You MUST run this command now to load the alias:"
echo "  source ~/.bashrc"
echo ""
echo "Then type '$FOLDER_NAME init' to start onboarding."
echo ""
