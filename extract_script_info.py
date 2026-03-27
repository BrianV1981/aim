import ast
import glob
import os
import json

def extract_info(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'docstring': f"Error reading: {e}", 'imports': []}

    try:
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return {'docstring': docstring, 'imports': list(set(imports))}
    except Exception as e:
        return {'docstring': None, 'imports': []}

def process_sh(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            doc_lines = []
            for line in lines:
                if line.startswith('#') and not line.startswith('#!'):
                    doc_lines.append(line.strip('# \n'))
                elif line.strip() and not line.startswith('#!'):
                    break
            return {'docstring': ' '.join(doc_lines), 'imports': []}
    except Exception as e:
        return {'docstring': None, 'imports': []}

results = {}
directories = ['hooks', 'src', 'scripts', 'skills']
all_files = []
for d in directories:
    for ext in ['*.py', '*.sh']:
        all_files.extend(glob.glob(f"{d}/**/{ext}", recursive=True))

for f in sorted(all_files):
    if f.endswith('.py'):
        info = extract_info(f)
    else:
        info = process_sh(f)
    results[f] = info

with open('script_info.json', 'w') as out:
    json.dump(results, out, indent=2)
