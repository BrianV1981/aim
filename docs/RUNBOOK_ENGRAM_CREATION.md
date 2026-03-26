# Runbook: How to Forge an `.engram` Cartridge

*The DataJack Protocol allows you to share pre-vectorized, mathematical semantic memory with other A.I.M. agents without wasting API tokens or GPU cycles. This runbook walks you through the exact process of creating (baking) a new `.engram` file.*

---

## Step 1: Gather Your Raw Materials
Before you can forge a cartridge, you need raw text data. 

1. Create a temporary ingestion folder inside the `synapse/` directory. 
   *(Note: The `synapse` folder is `.gitignore`'d, meaning anything you drop in here won't accidentally bloat the main A.I.M. repository).*
   
   ```bash
   mkdir -p synapse/my-new-plugin
   ```

2. Download your target documentation. The DataJack Foundry automatically parses the following file types:
   *   `.md` / `.markdown` (Standard Docs)
   *   `.txt` (Raw Text / Standard Python Docs)
   *   `.rst` (reStructuredText / Sphinx Docs)
   *   `.py`, `.ts`, `.rs`, `.js` (Raw source code files)

3. Drop all the files into `synapse/my-new-plugin/`.

## Step 2: The "Factory Floor" Protocol (`aim bake`)
You do not need to pollute your active `archive/engram.db` to create a new cartridge. A.I.M. features an isolated "Factory Floor" protocol that spins up a sterile database in your `/tmp/` directory just for this process.

Run the `aim bake` command. It requires two arguments: the target directory, and the output filename.

```bash
aim bake synapse/my-new-plugin my_custom.engram
```

### What Happens in the Background:
1. **Isolation:** A.I.M. spins up `/tmp/aim_factory_xyz/factory.db`.
2. **Chunking:** It reads all your raw files and chunks them into semantic blocks.
3. **Embedding:** It spins up your local Ollama/Nomic engine and mathematically embeds every chunk (this may take a few minutes depending on the size of the documentation).
4. **Compression:** It zips the resulting `.jsonl` math files into a flat binary archive.
5. **Self-Cleaning:** It instantly deletes the `/tmp/` database so zero cross-contamination occurs with your active workflow.

## Step 3: Test Your Cartridge
Your new `my_custom.engram` file is now sitting in the root of your A.I.M. workspace! 

Before you share it, test it locally to ensure it works. 

1. Move the new cartridge into the dedicated `engrams/` directory:
   ```bash
   mv my_custom.engram engrams/
   ```
2. Jack it into your active subconscious:
   ```bash
   aim jack-in engrams/my_custom.engram
   ```
3. Run a test search to verify the hybrid FTS5 and Vector indices caught the data:
   ```bash
   aim search "something from my custom docs"
   ```

## Step 4: Share It with the World
Because `.engram` files are heavy SQLite binaries (ranging from 500KB to 30MB), **do not commit them directly to Git.** 

To share them:
1. **GitHub Releases:** If you maintain a public repository, upload the `.engram` file as an Asset to a GitHub Release.
2. **Direct Transfer:** You can literally email the file, drop it in Slack/Discord, or put it on a USB drive. 
3. **The DataJack Torrent Swarm (Phase 38):** *(Coming Soon)* You will eventually be able to use `aim jack-in "magnet:?xt=..."` to seed and download cartridges peer-to-peer. 

---
*If you are looking for the automated "Self-Farming" engram protocol (where A.I.M. automatically scrapes GitHub issues and generates its own engrams), please refer to `docs/CARTRIDGE_FARMING_ECOSYSTEM.md`.*