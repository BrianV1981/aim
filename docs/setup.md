# Setup & Installation

## Prerequisites

- **Python 3.12+** with venv
- **Git** with remotes configured
- **OpenCode CLI** installed and authenticated
- **Ollama** (optional, for local embeddings and reasoning)
- **LanceDB** (auto-installed via requirements.txt)
- **DeepSeek API key** (for cloud reasoning; stored in system keyring)

## Clone & Configure

```bash
git clone https://github.com/d3c12yp7012/aim-opencode.git
cd aim-opencode

# Add upstream remote for syncing
git remote add upstream https://github.com/BrianV1981/aim.git

# Checkout the active branch
git checkout opencode
```

## Install

```bash
# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run initialization (seeds opencode.json, plugins, skills)
venv/bin/python aim_core/aim_init.py
```

## Configure

### OpenCode CLI

Ensure OpenCode is installed and configured:

```bash
opencode connect   # Authenticate
opencode status    # Verify connection
```

The initialization seeds `opencode.json` with agent and plugin definitions. The plugins directory at `.opencode/plugins/aim-hooks.ts` provides three hooks:

- `session.idle` — triggers session summarizer
- `tool.execute.after` — cognitive mantra counter
- `experimental.session.compacting` — injects continuity context

### Models

**Embedding:** `nomic-embed-text` via Ollama (default, local)

**Reasoning:** `deepseek-chat` via DeepSeek API (default)

Run `aim tui` to configure model routing interactively, or edit `core/CONFIG.json`:

```json
{
  "models": {
    "embedding": "nomic-embed-text",
    "embedding_provider": "local",
    "embedding_endpoint": "http://127.0.0.1:11434/api/embeddings",
    "default_reasoning": {
      "provider": "openai-compat",
      "model": "deepseek-chat",
      "endpoint": "https://api.deepseek.com/v1/chat/completions",
      "auth_type": "API Key"
    }
  }
}
```

### API Keys

Store API keys in the system keyring (not in config files):

```bash
# DeepSeek API key
python -c "import keyring; keyring.set_password('aim-system', 'reasoning-api-key', 'sk-...')"

# Google API key (optional, for Gemini fallback)
python -c "import keyring; keyring.set_password('aim-system', 'google-api-key', '...')"
```

## Ollama (Local AI)

```bash
# Install and start Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &

# Pull required models
ollama pull nomic-embed-text    # Embeddings (768-dim)
ollama pull qwen3.5:4b          # Local reasoning / coreference rewriting
```

## Verify Installation

```bash
# Check everything is wired up
venv/bin/python aim_core/aim_cli.py doctor

# Run the test suite
venv/bin/python -m pytest tests/ -x -q
```

## Migrate from SQLite to LanceDB

After first install, migrate existing SQLite vectors to LanceDB:

```bash
venv/bin/python -c "from aim_core.lance_backend import VectorBackend; VectorBackend().migrate_from_sqlite()"
```

This reads pre-computed nomic vectors from the federated SQLite databases and writes them into `memory_lance/` with a Tantivy FTS index. Zero re-embedding required.
