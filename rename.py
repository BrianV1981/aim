import os
import re

for root, dirs, files in os.walk("."):
    if ".git" in root or "venv" in root or "__pycache__" in root or "aim.wiki" in root or "aim-chalkboard" in root:
        continue
    for file in files:
        if file.endswith((".py", ".md", ".sh", ".json", ".geminiignore", ".txt")):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            new_content = re.sub(r"(?<!aim\.)\bwiki/", "memory-memory-wiki/", content)
            new_content = re.sub(r"(?<!aim\.)\bwiki\\\\", "memory-memory-wiki\\\", new_content)
            new_content = re.sub(r'\"wiki\"', '\"memory-wiki\"', new_content)
            new_content = re.sub(r"\'wiki\'", "\'memory-wiki\'", new_content)
            
            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated {path}")
