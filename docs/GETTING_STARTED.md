# Getting Started with A.I.M. (Native Linux)

Welcome to **Actual Intelligent Memory**, your sovereign context layer for the Gemini CLI.

## 🚀 The Sovereign Deployment Manual

### 1. Environment Hardening
Remove restricted "Snap" utilities and install native tools to ensure full system permissions.
```bash
sudo snap remove curl
sudo apt update && sudo apt install -y curl git python3-venv libfuse2t64 xdg-utils
```

### 2. Node.js & Gemini CLI
We use `nvm` to manage Node.js versions, ensuring we stay on **v20+**.
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install 20 && nvm use 20
npm install -g @google/gemini-cli
```

**OAuth Troubleshooting:**
If `gemini login` fails to open a browser, use the direct API key method:
1. Get a key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Run `gemini --auth` and select "Use a Gemini API key".

### 3. Sovereign Infrastructure
```bash
# Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text

# Obsidian
chmod +x Obsidian-*.AppImage
./Obsidian-*.AppImage --no-sandbox
```

### 4. A.I.M. Installation
```bash
git clone https://github.com/BrianV1981/aim.git
cd aim
./setup.sh
source ~/.bashrc
aim init
```

### 5. Final Configuration
Launch the interactive dashboard to set your AI providers and secure your vault.
```bash
aim tui
```

---

## 🏗️ Provider Pre-requisites
*   **Google (Cloud):** A valid Gemini API Key stored in your System Vault.
*   **Local (Ollama):** [Ollama](https://ollama.com/) installed and running locally with the `nomic-embed-text` model.
*   **Codex (CLI):** `codex-cli` installed via NPM and authenticated via `codex login`.
*   **OpenAI-Compat:** A valid endpoint URL and API Key.

"I believe I've made my point." — **A.I.M.**
