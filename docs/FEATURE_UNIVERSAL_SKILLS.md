# Key Feature: The Universal Skills Framework (MCP-Driven Actions)

**The Problem:** Every AI coding agent handles "tools" or "skills" differently. OpenClaw uses its own skill system, Gemini CLI uses TypeScript hooks, Codex uses a `skills/` folder, and Claude Code relies on standard system prompts. If you write a brilliant Python script to query your company's Jira board, you have to rewrite the wrapper logic 4 different times to get it working across all 4 CLIs.

**The Solution:** The A.I.M. Universal Skills Framework. A "Write Once, Run Anywhere" tool execution layer powered entirely by the **Model Context Protocol (MCP)**.

---

## 1. The Logic (Why MCP?)
Instead of building a proprietary "A.I.M. Plugin System" that only works with our exoskeleton, A.I.M. turns the entire problem sideways. 

A.I.M. already runs a persistent background `fastmcp` server (`src/mcp_server.py`) to expose the Engram DB to external applications. 

The Universal Skills Framework simply extends that existing server. Rather than teaching the *agent* how to run a tool, A.I.M. teaches the *MCP Server* how to run the tool. Because Cursor, VS Code, Claude Code, and Gemini all speak MCP natively, they automatically inherit every skill you write.

## 2. How it Works (The Execution)

### Step 1: Drop the Script
You create a simple executable script (Python, Bash, Node) that does a specific job (e.g., `deploy_to_aws.py` or `fetch_jira_ticket.sh`). 
You drop it into the `skills/` directory.

### Step 2: Write the Manifest
You place a tiny `SKILL.md` or `skill.json` file next to it. This file tells the MCP server:
- **The Name:** `fetch_jira`
- **The Description:** "Fetches a Jira ticket by ID."
- **The Arguments:** `ticket_id (string)`

### Step 3: The Translation Layer
When A.I.M.'s MCP server starts up, it recursively scans the `skills/` directory. For every valid script it finds, it dynamically registers a new tool endpoint on the MCP server.

### Step 4: The Execution
When you type `aim tui` and assign Claude Code to your Frontal Lobe, Claude connects to the A.I.M. MCP server. It instantly sees the `fetch_jira` tool. 
1. Claude decides to call the tool.
2. It sends the JSON payload to the MCP Server.
3. The MCP Server executes your `fetch_jira.sh` script on the local machine.
4. The MCP Server returns the `stdout` back to Claude.

## 3. The Ultimate Value Proposition
**Total CLI Agnosticism.**
If you hate the Gemini CLI tomorrow and decide to switch entirely to the new Anthropic Claude Code CLI, you do not lose a single custom tool. You don't have to rewrite any wrappers. 

Because A.I.M. acts as the central nervous system (The MCP Host), any agent you plug into it instantly inherits your entire arsenal of custom actions. You build your toolkit for the *environment*, not for the *agent*.