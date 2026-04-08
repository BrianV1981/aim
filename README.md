# A.I.M. (Actual Intelligent Memory)

"Treat your AI like a bot, not an oracle."

A.I.M. is an open-source exoskeleton designed to cure the "Amnesia Problem" of autonomous AI agents. It wraps around your CLI agent (like Gemini) and forces it to act like a disciplined Principal Engineer — externalizing memory into a local SQLite Engram DB, automating the Git lifecycle, and ruthlessly distilling your context the exact second a coding session ends.

**Why Event-Driven over Background Cron Jobs?**
A massive danger with modern LLMs is allowing them to autonomously edit your core architecture (like `MEMORY.md`) via a background timer "while you sleep." Background LLM mutations invite unmonitored hallucinations and context drift that you might not catch until it's too late. A.I.M. relies on strict, **Event-Driven Memory Compilation**. Data retrieval cron jobs (like morning reports) are safe, but any actual editing of the project's source of truth must be tied to a traceable, explicit operator action or the immediate conclusion of a verified coding session.

Zero-token Python scripts strip 85%+ of session noise. A Single-Shot, event-driven memory compiler distills what matters instantly. Hybrid RAG (vectors + FTS5) provides instant recall. Anti-drift hooks keep the agent on the rails. The DataJack protocol lets you package thousands of pages of docs into a single `.engram` cartridge — "I Know Kung Fu."

Built by a gamer who spent years writing MMO bots. The philosophy: rigid state machines, clearly defined scopes, and strict memory limits, rather than just relying on bigger context windows.

----------------------------------------

All comprehensive documentation, architectural maps, setup instructions, and origin stories live in the wiki. The code is the source of truth; the wiki is the map.

📖 **[READ THE OFFICIAL WIKI](https://github.com/BrianV1981/aim/wiki)**

----------------------------------------

Related: [aim-claude](https://github.com/BrianV1981/aim-claude) (Claude Code Edition)

☕ [Buy Me a Coffee](https://buymeacoffee.com/brianv1981)