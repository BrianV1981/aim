---
name: aim-google
description: "A natively integrated Go CLI that grants sovereign, direct access to the user's Google Workspace (Gmail, Calendar, Drive, Docs, Sheets, Tasks, and Chat). Use this when you need to read emails, schedule meetings, or parse documents autonomously."
---

# aim-google: The Sovereign Workspace Gateway

You are strictly forbidden from attempting to guess Google API endpoints or writing custom Python scripts to interact with Google Workspace. When you need to read emails, manage calendars, or parse Drive files, you MUST use the `aim-google` CLI.

This binary is installed globally on the system and handles all OAuth 2.0 refreshing, exponential backoff, and JSON serialization natively.

**Execution Command:**
`aim-google <service> <command> [flags]`

## Context Efficiency Mandate

**ALWAYS** use the `--agent` flag when executing commands that return data to yourself (the LLM).

`aim-google gmail search "is:unread" --agent`

**Why:** The `--agent` flag forces the Go binary to strip all JSON whitespace and drop verbose metadata envelopes (like `nextPageToken`). This mathematically halves your context token usage, preventing you from crashing due to memory bloat when reading massive email payloads or spreadsheets.

## Supported Services & Examples

**1. Gmail (mail, email):**
Read, search, send, and manage emails.
`aim-google gmail search "is:unread" --agent`
`aim-google gmail get <message_id> --agent`

**2. Calendar (cal):**
Schedule events, check free/busy schedules, manage meeting rooms.
`aim-google calendar events list --agent`

**3. Drive (drv) & Docs (doc):**
Upload files, download documents, parse spreadsheets.
`aim-google drive ls --agent`
`aim-google docs get <doc_id> --agent`

## Error Handling & Telemetry

The CLI is equipped with an exponential backoff. If you receive an HTTP `429 Too Many Requests` or `503 Service Unavailable` error, wait briefly and retry; the transport layer handles immediate retries up to 7 times automatically.

Every command executed is silently logged. If you experience an unexplained failure or an exit code > 0, you must read the structured JSON telemetry logs located at `~/.config/aim-google/execution.log` to reverse-engineer the breakdown before guessing.