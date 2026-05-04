#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# aim-opencode Scaffolding Script
# Bootstraps a new project from the aim-opencode OS WITHOUT sudo.
# Run this ONCE after cloning to create a clean, isolated project.
#
# Usage:
#   git clone https://github.com/d3c12yp7012/aim-opencode.git my-project
#   cd my-project
#   bash scaffold.sh
#   source ~/.bashrc
#   my-project init --headless
# ─────────────────────────────────────────────────────────────────
set -e

AIM_ROOT="$(cd "$(dirname "$0")" && pwd)"
FOLDER_NAME="$(basename "$AIM_ROOT")"

echo "============================================================"
echo " aim-opencode Scaffolding: $FOLDER_NAME"
echo "============================================================"

# ── Step 1: Fresh Git History ──────────────────────────────────
echo "[1/6] Creating fresh git history..."
rm -rf "$AIM_ROOT/.git"
git -C "$AIM_ROOT" init -b main > /dev/null 2>&1 || git -C "$AIM_ROOT" init > /dev/null 2>&1
git -C "$AIM_ROOT" add -A > /dev/null 2>&1
git -C "$AIM_ROOT" commit -m "Initial scaffold: aim-opencode OS for $FOLDER_NAME" > /dev/null 2>&1
echo "      Fresh commit created on main branch."

# ── Step 2: Python Virtual Environment ─────────────────────────
echo "[2/6] Creating Python virtual environment..."
if [ ! -d "$AIM_ROOT/venv" ]; then
    python3 -m venv "$AIM_ROOT/venv"
fi
echo "      Installing dependencies..."
"$AIM_ROOT/venv/bin/pip" install -r "$AIM_ROOT/requirements.txt" -q 2>&1 | tail -1
echo "      Dependencies installed."

# ── Step 3: Project Directories ────────────────────────────────
echo "[3/6] Creating project directories..."
mkdir -p "$AIM_ROOT/archive/history"
mkdir -p "$AIM_ROOT/archive/raw"
mkdir -p "$AIM_ROOT/archive/flashrank_cache"
mkdir -p "$AIM_ROOT/archive/sync"
mkdir -p "$AIM_ROOT/memory-wiki/_ingest"
mkdir -p "$AIM_ROOT/memory_lance"
mkdir -p "$AIM_ROOT/continuity"
echo "      archive/, memory-wiki/, memory_lance/, continuity/ ready."

# ── Step 4: Clean Workspace ────────────────────────────────────
echo "[4/6] Cleaning workspace artifacts..."
rm -rf "$AIM_ROOT/workspace"
echo "      workspace/ removed."

# ── Step 5: CLI Alias ──────────────────────────────────────────
echo "[5/6] Installing CLI alias..."
ALIAS_LINE="alias $FOLDER_NAME='$AIM_ROOT/venv/bin/python $AIM_ROOT/aim_core/aim_cli.py'"

for conf in "$HOME/.bashrc" "$HOME/.bash_aliases" "$HOME/.zshrc"; do
    if [ -f "$conf" ]; then
        if ! grep -q "alias $FOLDER_NAME=" "$conf" 2>/dev/null; then
            echo "" >> "$conf"
            echo "# A.I.M. OpenCode CLI ($FOLDER_NAME)" >> "$conf"
            echo "$ALIAS_LINE" >> "$conf"
            echo "      Added to $(basename "$conf")"
        else
            echo "      Already in $(basename "$conf")"
        fi
    fi
done

# ── Step 6: Verify ─────────────────────────────────────────────
echo "[6/6] Verifying..."
"$AIM_ROOT/venv/bin/python" -c "import lancedb, aim_core" 2>/dev/null && echo "      Core imports OK" || echo "      [WARN] Some imports failed — check requirements.txt"

echo ""
echo "============================================================"
echo " Scaffolding complete!"
echo ""
echo "  Project:  $FOLDER_NAME"
echo "  Python:   $AIM_ROOT/venv/bin/python"
echo "  Alias:    $FOLDER_NAME <command>"
echo ""
echo "  Next steps:"
echo "    source ~/.bashrc"
echo "    $FOLDER_NAME init --headless"
echo "============================================================"
