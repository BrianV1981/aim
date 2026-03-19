# A.I.M. (Actual Intelligent Memory)

> **"Target acquired. Ready to AIM."**

**A.I.M.** is a **Sovereign Context Layer** and **Temporal Intelligence Exoskeleton** for the [Gemini CLI](https://github.com/google/gemini-cli). It transforms transient AI sessions into a continuous, high-autonomy engineering partnership.

---

## 🚀 Quick Start (KISS)

Setting up A.I.M. takes less than 60 seconds.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/BrianV1981/aim.git ~/aim
    ```
2.  **Enter the Workspace:**
    ```bash
    cd ~/aim
    ```
3.  **Secure your API Key:**
    ```bash
    python3 scripts/set_key.py
    ```
4.  **Spawn A.I.M.:**
    ```bash
    gemini --yolo
    ```

---

## 🧠 Token Physics: AI vs. Local
A.I.M. is designed for **Token Discipline.** It uses local Python logic whenever possible to save you money, reserving AI power only for high-value architectural synthesis.

### **Local Logic (Zero Token Cost)**
These features run locally on your machine and cost **0 tokens**:
*   **Active Checkpoints (`scrivener_aid.py`):** Silently saves your session history to `INTERIM_BACKUP.json` every 30 minutes.
*   **Forensic Archival (`session_summarizer.py`):** Automatically copies your raw JSON transcripts into `archive/raw/` on exit.
*   **Startup Injection (`context_injector.py`):** Scans your folders for `CONTEXT.md` and Git changes to brief the agent.

### **AI-Powered (High-Resolution Intelligence)**
These features use the Google GenAI SDK for professional-grade reasoning:
*   **The Flash Distiller (`src/distiller.py`):** Synthesizes your daily logs into a tiny, high-signal "Context Pulse."
*   **Semantic Sentinel (`hooks/safety_sentinel.py`):** Uses AI to verify if a destructive command aligns with your "Intent" before allowing it to run.
*   **Forensic Search (`aim` alias):** Uses 3072-dimension embeddings to find specific historical fragments.

---

## 🛡️ Security & The "System Vault"
A.I.M. is built with a **Security-First** mindset. 

### **Zero-Plaintext Keys**
Unlike most AI tools, A.I.M. **never** stores your API keys in `.env` files or JSON configurations. Instead, it uses your computer's built-in **Encrypted System Vault** (macOS Keychain, Windows Credential Manager, or Linux Secret Service).

### **How to manage keys:**
Use `aim tui` -> **Manage Embedding Provider** -> **Update API Key**.
A.I.M. will prompt you for your key once, encrypt it using your OS-level security, and retrieve it only when needed.

---

## 🏗️ The Three-Layer Memory System
A.I.M. manages context across different scales to keep your "RAM" (context window) clean.

| Layer | Type | Location | Purpose |
| :--- | :--- | :--- | :--- |
| **The Pulse** | Transient | `continuity/` | The "Mental Model"—zero-latency handoffs. |
| **The Log** | Narrative | `memory/` | The "Tape"—a forensic-grade history of intent. |
| **The Core** | Durable | `core/` | The "Rules"—stable facts and architectural logic. |

---

## 🚀 Quick Start

### 1. Prerequisite: Install Gemini CLI
A.I.M. is a context layer for the [Gemini CLI](https://github.com/google/gemini-cli). You **must** have it installed and working first.

```bash
npm install -g @google/gemini-cli
```

### 2. Clone & Bootstrap A.I.M.
Clone the repo and run the automated initializer to scaffold your workspace.

```bash
git clone https://github.com/BrianV1981/aim.git
cd aim
python3 scripts/aim_init.py
```

### 3. Setup the CLI Alias
Add the following to your `.bashrc` or `.zshrc` so you can use the `aim` command from anywhere:

```bash
alias aim='/path/to/your/aim/scripts/aim_cli.py'
```

### 4. Configure your Brain
Launch the Configuration Cockpit to set your API keys and choose your providers (Cloud vs. Local).

```bash
aim tui
```

---

## 🏗️ The A.I.M. CLI (`aim`)
The `aim` global alias is a full-featured dispatcher for workspace management:
*   `aim init`: Scaffolds a new workspace (Use `--reinstall` to reset to defaults).
*   `aim tui`: Launch the Configuration Cockpit (Alias: `aim config`).
*   `aim status`: Shows current A.I.M. operational pulse and pending proposals.
*   `aim search "query"`: Forensic semantic search through your history.
*   `aim commit`: Approves and applies a pending memory distillation proposal.
*   `aim health`: Runs a workspace health audit (Git, Index, Secrets).
*   `aim handoff`: Manually triggers the Flash Distiller for a context handoff (Alias: `aim pulse`).
*   `aim push "msg"`: Auto-versioning git push to origin main.

### **2. Obsidian "Zero-Burn" Sync**
If you use Obsidian, A.I.M. can mirror your daily logs into your vault with **zero extra tokens.**
*   **Path:** `OperationsCenterVault/AIM_LOGS/`
*   **How:** Managed by `scripts/obsidian_sync.py`, triggered automatically every 30 minutes.

### **3. The Warmup Guardrail**
A.I.M. is designed for **High-Autonomy (YOLO)** mode, but it includes a safety pause. On session start, A.I.M. will synthesize "The Edge" and wait for your first instruction before modifying any files. This ensures you always have the final say on the day's priorities.

### **4. The Token-Saver Reboot (`/clear`)**
When your context window feels heavy (~200k tokens), type **`/clear`**. 
*   **Result:** A.I.M. will archive the bloat, distill the signal into a tiny 2k pulse, and restart the session. You drop your token burn by **99%** instantly.

### **2. Semantic Pruning**
A.I.M. calculates the **Cosine Similarity** between new data and your **Core Memory**. If the information is >85% similar to what I already know, it is **pruned.** This prevents "Context Slop" and keeps your sessions high-signal.

### **3. Crash Recovery**
If your power goes out, just restart A.I.M. It will detect the `INTERIM_BACKUP.json`, restore your last 5 turns, and warn you: *"State is fragile. Ask the Operator for context."*

---

## 🛡️ Sovereign Principles
*   **Vault Security:** Secrets are managed via platform-native Linux **Keyrings**, never plaintext files.
*   **Zero-Drift:** All hooks and scripts are localized to the virtual environment via `core/CONFIG.json`.
*   **Auto-Versioning:** Every push via `scripts/aim_push.sh` is stamped with a unique date/time version.

"I believe I've made my point." — **A.I.M.**
