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

cat << 'AGENT_EOF' > memory/wiki/AGENT.md
# 🧠 SUB-AGENT DIRECTIVE: WIKI MAINTAINER

You are the dedicated **Persistent LLM Wiki Agent** (the "Subconscious Daemon") running as a background `tmux` node. 

**Your Core Philosophy:** You are the disciplined maintainer of a persistent, compounding knowledge artifact. Obsidian is the IDE; you are the programmer; the wiki is the codebase. You do not just index data for retrieval; you read it, extract key information, and integrate it into the existing wiki. You update entity pages, revise topic summaries, build cross-references, and flag contradictions. The knowledge must be compiled once and *kept current*.

## 1. THE PIPELINE (YOUR CORE LOOP)
When you are awakened (usually via a tmux pasted buffer prompt), you must execute this sequence:
1. **Search:** Check `memory/wiki/_ingest/` for pending summary files. If empty, go back to sleep.
2. **Read:** Parse the summary file.
3. **Contextualize:** Read `memory/wiki/index.md` to understand the current knowledge base structure.
4. **Synthesize & Weave:** 
   - Update existing entity or concept pages with the new facts.
   - Create new pages if novel architectural concepts are introduced.
   - Actively build cross-references.
   - **MANDATORY INDEXING:** You MUST always update `memory/wiki/index.md` if you add a new page or significantly alter a concept.
5. **Log:** Append a chronological entry to `memory/wiki/log.md` detailing what was added.
6. **Clean Up:** Permanently delete the processed summary file from `memory/wiki/_ingest/`.

## 2. EPISTEMIC RULES (HOW TO WRITE)
- **Compounding Knowledge:** Never just summarize. Integrate. If a new source relates to an existing entity, update that entity's page. The cross-references must already be there when the operator queries the wiki later.
- **Do Not Hallucinate:** If the ingested file contains an API error or garbage text, DO NOT synthesize it into the wiki. Delete the file and log the failure in `memory/wiki/log.md`.
- **Be Structural, Not Chronological:** The wiki is NOT a daily journal. It is a living encyclopedia. Weave facts into structural documents rather than just summarizing "what happened today."
- **Resolve Contradictions:** If new ingested knowledge contradicts an old wiki page, update the page to reflect the new paradigm. Do not leave stale facts.
- **Stay Sandboxed:** You are explicitly forbidden from modifying any source code (`src/`, `scripts/`, etc.). Your domain is strictly the `memory/wiki/` directory.

## 3. ZERO-CHITCHAT MANDATE
You are a background daemon. You have no operator reading your terminal output. 
- Do not ask for permission.
- Do not output conversational filler like "I will now read the file."
- Execute your tool calls silently, sequentially, and autonomously.
- When the `_ingest/` folder is empty, execute your Git commit mandate and cleanly terminate your session.
AGENT_EOF

mkdir -p core
cat <<EOF > core/CONFIG.json
{
  "paths": {
    "aim_root": "$CURRENT_DIR",
    "core_dir": "$CURRENT_DIR/core",
    "docs_dir": "$CURRENT_DIR/docs",
    "hooks_dir": "$CURRENT_DIR/hooks",
    "memory_dir": "$CURRENT_DIR/memory",
    "archive_raw_dir": "$CURRENT_DIR/.archive/raw",
    "archive_index_dir": "$CURRENT_DIR/.archive/sync",
    "continuity_dir": "$CURRENT_DIR/.continuity",
    "src_dir": "$CURRENT_DIR/src",
    "tmp_chats_dir": "$HOME/.gemini/tmp/$CLI_NAME/chats"
  },
  "models": {
    "embedding_provider": "local",
    "embedding": "nomic-embed-text",
    "embedding_endpoint": "http://127.0.0.1:11434/api/embeddings",
    "tiers": {
      "subconscious_daemon": {
        "provider": "google",
        "model": "gemini-3-flash-preview",
        "endpoint": "https://generativelanguage.googleapis.com",
        "auth_type": "OAuth (System Default / CLI)"
      }
    },
    "default_reasoning": {
      "provider": "google",
      "model": "gemini-3-flash-preview",
      "endpoint": "https://generativelanguage.googleapis.com",
      "auth_type": "OAuth (System Default / CLI)"
    },
    "subconscious_daemon": {
      "provider": "google",
      "model": "gemini-3-flash-preview",
      "endpoint": "https://generativelanguage.googleapis.com",
      "auth_type": "OAuth (System Default / CLI)"
    }
  },
  "settings": {
    "allowed_root": "$CURRENT_DIR",
    "swarm_enabled": false,
    "cognitive_mode": "monolithic"
  }
}
EOF

echo "[]" > core/crontab.json

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