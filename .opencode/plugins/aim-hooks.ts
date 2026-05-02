import type { Plugin } from "@opencode-ai/plugin"
import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync, statSync } from "node:fs"
import { join, basename, dirname } from "node:path"

/**
 * A.I.M. Hook Plugin — replaces aim_router.py for OpenCode.
 *
 * Subscribes to three OpenCode events:
 *   1. session.idle          →  Trigger session summarizer
 *   2. tool.execute.after    →  Cognitive Mantra counter + injection
 *   3. experimental.session.compacting →  Inject AIM continuity context
 */

// ─── Constants ────────────────────────────────────────────────────────
const CONTINUITY_DIR = "continuity"
const MANTRA_PULSE_FILE = join(CONTINUITY_DIR, "MANTRA_PULSE.md")
const STATE_DIR = join(".opencode", "plugins", ".state")
const MANTRA_STATE_FILE = join(STATE_DIR, "mantra_state.json")
const DEFAULT_MANTRA_INTERVAL = 50

interface MantraState {
  last_mantra: number
  session_id: string
}

// ─── Helpers ──────────────────────────────────────────────────────────

function findAimRoot(directory: string): string | null {
  let current = directory
  while (current !== "/") {
    if (
      existsSync(join(current, "core", "CONFIG.json")) ||
      existsSync(join(current, "setup.sh"))
    ) {
      return current
    }
    current = dirname(current)
  }
  return null
}

function findLatestTranscript(historyDir: string): string | null {
  if (!existsSync(historyDir)) return null

  const files = readdirSync(historyDir)
    .filter((f) => f.endsWith(".md"))
    .map((f) => join(historyDir, f))
    .map((f) => ({ path: f, mtime: statSync(f).mtimeMs }))
    .sort((a, b) => b.mtime - a.mtime)

  return files[0]?.path ?? null
}

function readMantraState(): MantraState {
  try {
    if (existsSync(MANTRA_STATE_FILE)) {
      const raw = readFileSync(MANTRA_STATE_FILE, "utf-8")
      return JSON.parse(raw) as MantraState
    }
  } catch {
    // corrupted state, reset
  }
  return { last_mantra: 0, session_id: "" }
}

function writeMantraState(state: MantraState): void {
  mkdirSync(STATE_DIR, { recursive: true })
  const tmp = MANTRA_STATE_FILE + ".tmp"
  writeFileSync(tmp, JSON.stringify(state, null, 2), "utf-8")
  Bun.write(MANTRA_STATE_FILE, Bun.file(tmp)) // atomic-ish via Bun
}

// ─── Plugin Entry ─────────────────────────────────────────────────────

export const AimHooks: Plugin = async ({ project, client, $, directory, worktree }) => {
  const aimRoot = findAimRoot(directory)
  if (!aimRoot) {
    console.warn("[AIM-HOOKS] Not inside an A.I.M. workspace — plugin inactive.")
    return {}
  }

  const venvPython = join(aimRoot, "venv", "bin", "python3")
  const summarizerScript = join(aimRoot, "hooks", "session_summarizer.py")
  const historyDir = join(aimRoot, "archive", "history")
  const agentsPath = join(aimRoot, "AGENTS.md")

  return {
    // ── 1. Session Idle → Session Summarizer ────────────────
    "session.idle": async () => {
      const transcript = findLatestTranscript(historyDir)
      if (!transcript) {
        await client.app.log({
          body: {
            service: "aim-hooks",
            level: "warn",
            message: "No transcript found for session summarizer",
          },
        })
        return
      }

      const python = existsSync(venvPython) ? venvPython : "python3"
      try {
        $`${python} ${summarizerScript} ${transcript}`
          .quiet()
          .nothrow()
        await client.app.log({
          body: {
            service: "aim-hooks",
            level: "info",
            message: `Triggered session summarizer for ${basename(transcript)}`,
          },
        })
      } catch (err) {
        await client.app.log({
          body: {
            service: "aim-hooks",
            level: "error",
            message: `Session summarizer failed: ${String(err)}`,
          },
        })
      }
    },

    // ── 2. Tool Execute → Cognitive Mantra Counter ───────
    "tool.execute.after": async (input, output) => {
      const state = readMantraState()
      const currentId = project?.id ?? ""

      // Reset counter on new session
      if (state.session_id !== currentId) {
        state.session_id = currentId
        state.last_mantra = 0
      }

      state.last_mantra += 1

      // Mantra threshold (configurable via CONFIG.json in the future)
      const mantraInterval = DEFAULT_MANTRA_INTERVAL
      const triggered = state.last_mantra >= mantraInterval

      writeMantraState(state)

      if (!triggered) return

      // Write mantra pulse for agent to read
      const agentsContent = existsSync(agentsPath)
        ? readFileSync(agentsPath, "utf-8")
        : ""

      const mantra = `# 🧠 A.I.M. Cognitive Mantra Protocol

**Triggered at:** ${state.last_mantra} autonomous tool calls.
**Session:** ${currentId}

> You MUST halt your current task immediately. In your very next response,
> output a \\\`<MANTRA>\\\` block reciting the ENTIRETY of the system instructions
> below. Do NOT split the recitation into multiple parts. Output the entire
> mantra in a single, continuous block. Only after reciting the full mantra
> may you continue working.

---

${agentsContent}
`

      const mantraFilePath = join(aimRoot, MANTRA_PULSE_FILE)
      mkdirSync(dirname(mantraFilePath), { recursive: true })

      const tmp = mantraFilePath + ".tmp"
      writeFileSync(tmp, mantra, "utf-8")
      Bun.write(mantraFilePath, Bun.file(tmp))

      await client.app.log({
        body: {
          service: "aim-hooks",
          level: "info",
          message: `Mantra triggered at ${state.last_mantra} tool calls`,
        },
      })
    },

    // ── 3. Session Compaction → Inject Continuity Context ──
    "experimental.session.compacting": async (input, output) => {
      const continuity: string[] = []

      // Inject REINCARNATION_GAMEPLAN.md if recent
      const gameplanPath = join(aimRoot, CONTINUITY_DIR, "REINCARNATION_GAMEPLAN.md")
      if (existsSync(gameplanPath)) {
        try {
          const content = readFileSync(gameplanPath, "utf-8")
            .split("\n")
            .slice(0, 80) // limit to first 80 lines to avoid bloat
            .join("\n")
          continuity.push(`## Continuity: Reincarnation Gameplan\n${content}`)
        } catch { /* skip */ }
      }

      // Inject issue tracker summary
      const issuePath = join(aimRoot, CONTINUITY_DIR, "ISSUE_TRACKER.md")
      if (existsSync(issuePath)) {
        try {
          const content = readFileSync(issuePath, "utf-8")
            .split("\n")
            .filter((line) => line.startsWith("* **#") || line.startsWith("* #"))
            .slice(0, 15) // top 15 open issues only
            .join("\n")
          if (content.trim()) {
            continuity.push(`## Continuity: Active Issues\n${content}`)
          }
        } catch { /* skip */ }
      }

      // Inject current pulse
      const pulsePath = join(aimRoot, CONTINUITY_DIR, "CURRENT_PULSE.md")
      if (existsSync(pulsePath)) {
        try {
          const content = readFileSync(pulsePath, "utf-8").slice(0, 2000)
          continuity.push(`## Continuity: Current Pulse\n${content}`)
        } catch { /* skip */ }
      }

      if (continuity.length > 0) {
        output.context.push(continuity.join("\n\n---\n\n"))
        await client.app.log({
          body: {
            service: "aim-hooks",
            level: "debug",
            message: `Injected ${continuity.length} continuity blocks into compaction`,
          },
        })
      }

      // Reset mantra counter on compaction to prevent false triggers
      mkdirSync(STATE_DIR, { recursive: true })
      writeFileSync(MANTRA_STATE_FILE, JSON.stringify({ last_mantra: 0, session_id: project?.id ?? "" }, null, 2), "utf-8")
    },
  }
}
