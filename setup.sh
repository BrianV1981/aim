#!/bin/bash
# A.I.M. Venv Builder

set -e
echo "--- A.I.M. VENV BOOTSTRAP ---"

AIM_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$AIM_ROOT"

# OS Detection
OS_NAME=$(uname -s)
if [ "$OS_NAME" = "Linux" ]; then
    echo "[*] Ensuring Linux dependencies..."
    sudo apt-get update -qq && sudo apt-get install -y -qq dbus-x11 libdbus-1-dev
fi

# Python Venv
if [ ! -d "venv" ]; then
    echo "[*] Creating Python Virtual Environment..."
    python3 -m venv venv
fi

echo "[*] Installing Python dependencies..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
deactivate

echo "[SUCCESS] A.I.M. Backend Built."
