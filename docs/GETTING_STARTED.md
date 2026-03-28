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
We use `nvm` to manage Node.js versions, ensuring we stay on v20+.

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install 20 && nvm use 20
npm install -g @google/gemini-cli
```

**🚨 CRITICAL: Log into GEMINI CLI before going any further 🚨**

```bash
gemini login
```
*OAuth Troubleshooting:* If `gemini login` fails to open a browser (common in WSL/Headless), use the direct API key method:
1. Get a key from [Google AI Studio](https://aistudio.google.com/).
2. Run `gemini --auth` and select "Use a Gemini API key".

### 3. Sovereign Infrastructure

**Ollama (Local Embeddings)**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text
```

**Obsidian (The Vault)**
1. Download the Obsidian `.AppImage` to your Home (`~`) folder from [obsidian.md](https://obsidian.md/).
2. Grant execution permissions and launch:
```bash
chmod +x ~/Obsidian-*.AppImage
~/Obsidian-*.AppImage --no-sandbox
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

### 6. Known Issues / First Run
- **Command Not Found:** After running `./setup.sh`, if you type `aim init` (or your dynamic alias like `openclaw-aim init`) and get a `command not found` error, it is because your current terminal window has not reloaded its configuration. You must run `source ~/.bashrc` to refresh your terminal session before the newly created alias will work.
- **TUI Sensitivity:** The `aim tui` (built with Textual/Questionary) is highly sensitive to the exact JSON structure returned by upstream providers. If you select an OpenRouter or OpenAI-Compatible endpoint that returns a malformed response during the "Cognitive Health Check", the TUI may crash. If this happens, you can manually fix your providers by editing `core/CONFIG.json`.
- **Keyring Errors:** In headless Linux environments (like WSL or Docker without a desktop bus), the Python `keyring` library may fail to find a secure backend to store API keys. If you see a `keyring.errors.NoKeyringError`, you may need to install a plain-text fallback backend or export your keys directly via environment variables (`export GEMINI_API_KEY=...`).

---

## 🏗️ Provider Pre-requisites
*   **Google (Cloud):** A valid Gemini API Key stored in your System Vault.
*   **Local (Ollama):** Ollama installed and running locally with the `nomic-embed-text` model.
*   **Codex (CLI):** `codex-cli` installed via NPM and authenticated via `codex login`.
*   **OpenAI-Compat:** A valid endpoint URL and API Key.

---

"I believe I've made my point." — **A.I.M.**