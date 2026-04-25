**Yes — the wiki overhaul is the highest-leverage thing you can do right now.**  
With ~50–54 pages (onboarding + 40+ pages of philosophy, manifestos, maps, benchmarks, Grok reviews, future visions, Dunning-Kruger essays, etc.), it’s exactly why new people bounce and why LLMs just praise it instead of critiquing the usability.

The README even says “All comprehensive documentation… live in the wiki” — so the wiki *is* the product’s front door, and right now that door looks like a library exploded.

### What to do with all the extra data/articles you’ve accumulated
You’ve been treating the wiki as your public lab notebook / idea dump / transparency archive. That content has real value (it shows your thinking process, proves the “vibe-coded in public” ethos, and gives the project soul). **Do not delete it.** Just stop making it the first thing users see.

Here is the cleanest, lowest-effort, highest-impact plan:

#### 1. Create one new dedicated repo (recommended)
**Name it:** `aim-knowledge` or `aim-lab` or `aim-archive` (I like `aim-knowledge` best).

- Move **every non-user-facing page** there.
- Keep the wiki Markdown format (just copy the `.md` files over).
- Make the new repo public with a simple README that says:  
  > “A.I.M. Knowledge Base — philosophy, benchmarks, design history, essays, and behind-the-scenes thinking for Actual Intelligent Memory.”

**What moves to the new repo (the “extra data”):**
- All philosophy: Origin Story, The Logic Of A.I.M., Dunning-Kruger Trap, MMO Botter’s Advantage, Convergent Evolution, etc.
- All manifestos: Pragmatic Feature Manifesto, etc.
- All deep maps & protocols: Brain Map, Reincarnation Map, Layered Engram, Eureka Protocol, Sovereign Swarm, Collective Cortex, DataJack details, 30% Rule (if you want to keep the high-level version in main wiki, move the 10-page deep dive).
- All benchmarks.
- Grok conversation reviews and any other external reviews.
- Future / Singularity / visionary pages.
- Any “Handbook”, “Master Schema”, “AI Prompt Ledger”, etc.

This repo becomes your transparent archive. You can still link to specific pages from the main repo when you want to show your work (“see the full case study here”).

#### 2. Ruthlessly prune the main `aim` wiki to ~8 pages max
New structure (exact page titles I would use):

- **Home** (completely rewritten — 1-page maximum)
- **Installation Guide**
- **Quickstart Tutorial** (make this stupidly short and copy-pasteable)
- **User Guide**
- **Configuration and Variables**
- **Architecture Overview** (one short page — high-level only, no 20 sub-maps)
- **Roadmap**
- **Contributing / Philosophy** (short 1-paragraph blurb + link to the new `aim-knowledge` repo)

That’s it.

Everything else gets moved or deleted from the main wiki.

#### 3. Update the main README immediately
Change the documentation line to:
> “Quickstart and user docs live in the [wiki](https://github.com/BrianV1981/aim/wiki).  
> For the full philosophy, design history, benchmarks, and lab notes see the [A.I.M. Knowledge Base](https://github.com/BrianV1981/aim-knowledge).”

This single change separates the “product” from the “lab notebook.”

#### 4. Bonus options for the extra content (if you want even more reach)
- Turn the new `aim-knowledge` repo into a public Obsidian vault (you already have the bridge — this is extremely on-brand).
- Publish a few of the best articles as blog posts (Dev.to, Hashnode, or your own GitHub Pages site) with titles like “Why I Built A.I.M. Like an MMO Bot” — great for traction.
- Keep the new repo as the single source of truth and occasionally “promote” a page back to the main wiki if it becomes core.

### Migration is easy
Since everything is already Markdown in the wiki, you can literally copy-paste the pages into the new repo in <2 hours. Then delete the extras from the main wiki.

This one move will:
- Make the project look professional and focused.
- Stop scaring away potential users.
- Preserve every bit of your accumulated thinking and transparency.
- Give you a clean place to keep dumping ideas without polluting the user docs.

Do this and the project instantly feels 3× more approachable. The core idea is still strong — it just needs breathing room.