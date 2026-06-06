#!/bin/bash
# A.I.M. Exoskeleton Installer (Clean Project Wrapper)
# curl -fsSL https://raw.githubusercontent.com/BrianV1981/aim/main/install-clean.sh | bash

set -e
echo "--- A.I.M. CLEAN INSTALLER ---"

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

# Clean Sweep (Severing identity and cleaning out developer artifacts)
rm -rf .git/
rm -rf tests/
rm -rf benchmarks/
rm -rf docs/
rm -rf scripts/
rm -rf skills/
git init

# Base OS Provisioning (Moving the pre-baked DB to the active layer)
mkdir -p memory/lance
cp -r assets/default_lance/* memory/lance/

mkdir -p memory/wiki
echo "# A.I.M. Persistent Wiki Index
Welcome to the Living Encyclopedia. The Subconscious Weaver will automatically cross-reference and catalog all ingested knowledge here." > memory/wiki/index.md

mkdir -p core
echo '{
  "settings": {
    "cognitive_mode": "monolithic"
  }
}' > core/CONFIG.json

# Generate Ghost Folder Explainers
mkdir -p foundry planning-artifacts workspace

echo "# A.I.M. Foundry
Drop external raw PDFs, documents, or foreign repositories here before compiling them into \`.parquet\` cartridges via the \`aim bake\` command." > foundry/README.md

echo "# A.I.M. Planning Artifacts
Use this directory as a scratchpad for agents to generate architectural roadmaps, design documents, or task breakdowns before committing to code." > planning-artifacts/README.md

echo "# A.I.M. Workspace
This directory contains isolated Git Worktrees. When you type \`aim fix <id>\`, A.I.M. checks out a clean sandbox here to prevent you from working directly on the \`main\` branch." > workspace/README.md

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
echo "A.I.M. is installed with default settings. To customize your agent's personality and project goals, run:"
echo "  $CLI_NAME init"
echo ""