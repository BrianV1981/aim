# A.I.M. Complete Installation Guide (Linux & WSL)

This guide provides a comprehensive, step-by-step walkthrough for installing A.I.M. and all its dependencies from scratch on a Linux or WSL (Ubuntu) environment.

---

## 1. System Prerequisites

### Install Git
```bash
sudo apt update
sudo apt install git -y
git --version
```

### Install Python Virtual Environment
On Debian/Ubuntu systems, the `venv` package is not included by default.
```bash
sudo apt install python3-venv -y
```
*(Note: If you ever need to uninstall it due to a corrupted directory, use `sudo apt purge python3-venv`).*

### Fix the "Snap" Curl Issue (Ubuntu 24.04+)
Ubuntu often defaults to a restricted "Snap" version of `curl` which causes permission issues during NVM and Ollama installations. Remove it and install the native version:
```bash
sudo snap remove curl
sudo apt update && sudo apt install curl -y
```

---

## 2. Node.js & The Gemini CLI

The Gemini CLI requires Node.js v18 or higher. We highly recommend using **NVM** (Node Version Manager) to install Node v20 to avoid syntax errors.

### Install NVM
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
```

### Install Node 20
```bash
nvm install 20
nvm use 20
node -v # Should output v20.x.x
```

### Install the Gemini CLI
Install it globally so the `gemini` command is available everywhere:
```bash
npm install -g @google/gemini-cli
```
*(macOS users can alternatively use `brew install gemini-cli`)*

---

## 3. Local AI Models (Ollama)

A.I.M. relies on Nomic for local vector embeddings to keep your data private and free.

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text
```
*(Optional: You can pull any other model you want for local reasoning, e.g., `ollama pull qwen3.5:cloud`)*

---

## 4. Obsidian (The Memory Vault)

If you plan to use Obsidian to visualize A.I.M.'s `.md` memory files:
1. Download the `.AppImage` from [obsidian.md](https://obsidian.md/).
2. Move it to your Home folder.

### The FUSE 2 Fix (Ubuntu 22.04 / 24.04)
Modern Ubuntu no longer includes the FUSE 2 library by default, which AppImages require.
⚠️ **Important Warning:** Do *not* run `sudo apt install fuse`. This installs FUSE 3 and can remove critical desktop components.

**For Ubuntu 24.04 (Noble) or newer:**
```bash
sudo apt update
sudo apt install libfuse2t64
```
**For Ubuntu 22.04 (Jammy):**
```bash
sudo apt update
sudo apt install libfuse2
```

### Run Obsidian
Grant the file execution permissions and launch it:
```bash
chmod +x Obsidian-*.AppImage
./Obsidian-*.AppImage --no-sandbox
```
*Create a vault in your preferred directory. A.I.M. will ask for this path during initialization.*

---

## 5. Clone & Bootstrap A.I.M.

With all dependencies installed, you are ready to construct the exoskeleton.

```bash
git clone https://github.com/BrianV1981/aim.git
cd aim
./setup.sh
source ~/.bashrc
aim init
```

---

## 6. GitHub Integration (GitOps Bridge)

To fully utilize A.I.M.'s automated GitOps commands (`aim push`, `aim bug`), you need a Personal Access Token (PAT).

1. Log into GitHub on your browser.
2. Go to **Settings** > Scroll down to **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
3. Click **Generate new token (classic)**.
4. Name the token (e.g., "AIM Bot").
5. Check all applicable permissions (Select everything if you are running in YOLO mode).
6. Click **Generate token**.
7. **Copy the key** and leave the browser open (or save it temporarily to a local password manager).

You are now fully operational. Run `aim tui` to configure your LLM providers, and enter the Matrix.