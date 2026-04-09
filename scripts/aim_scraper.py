#!/usr/bin/env python3
import os
import subprocess
import json
import argparse
from datetime import datetime
import requests
import re
import html
import hashlib

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return html.unescape(cleantext)

def run_gh_command(cmd_list):
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {' '.join(cmd_list)}")
        print(f"Error output: {e.stderr}")
        return None

def fetch_closed_issues(repo=None, limit=20):
    repo_msg = repo if repo else "current repository"
    print(f"Fetching up to {limit} completed (solved) issues from {repo_msg}...")
    
    cmd = ["gh", "issue", "list", "--state", "closed", "--limit", str(limit * 3), "--json", "number,title,body,labels,url,stateReason"]
    if repo:
        cmd.extend(["--repo", repo])
        
    output = run_gh_command(cmd)
    if output:
        all_closed = json.loads(output)
        completed_issues = [i for i in all_closed if i.get("stateReason") == "COMPLETED"]
        return completed_issues[:limit]
    return []

def fetch_issue_comments(issue_number, repo=None):
    cmd = ["gh", "issue", "view", str(issue_number), "--json", "comments"]
    if repo:
        cmd.extend(["--repo", repo])
        
    output = run_gh_command(cmd)
    if output:
        data = json.loads(output)
        return data.get("comments", [])
    return []

def format_issue_as_markdown(issue, comments, output_dir):
    number = issue['number']
    title = issue['title']
    url = issue['url']
    body = issue['body']
    
    useful_comments = [c['body'] for c in comments if len(c['body'].strip()) > 20]
    if not useful_comments:
        return False
        
    filename = f"issue_{number}.md"
    filepath = os.path.join(output_dir, filename)
    
    content = f"# Q: {title}\n"
    content += f"**Source:** {url}\n\n"
    content += "## The Problem / Request\n"
    content += f"{body}\n\n"
    content += "## The Solution / Discussion\n"
    for idx, comment in enumerate(useful_comments):
        content += f"### Response {idx + 1}\n"
        content += f"{comment}\n\n"
        
    c_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            if f"content_hash: {c_hash}" in f.read():
                return False
                
    frontmatter = f"---\ntype: community_knowledge\nsource: github#{number}\ncontent_hash: {c_hash}\n---\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter + content)
    return True

def fetch_stackoverflow_threads(query, limit=10):
    print(f"Fetching up to {limit} resolved threads from StackOverflow for query: '{query}'...")
    url = "https://api.stackexchange.com/2.3/search/advanced"
    params = {
        "order": "desc",
        "sort": "relevance",
        "q": query,
        "site": "stackoverflow",
        "filter": "withbody",
        "accepted": "True",
        "pagesize": limit
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("items", [])
    except Exception as e:
        print(f"[ERROR] Failed to fetch from StackOverflow: {e}")
        return []

def fetch_stackoverflow_answers(question_id):
    url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
    params = {
        "order": "desc",
        "sort": "votes",
        "site": "stackoverflow",
        "filter": "withbody"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("items", [])
    except Exception as e:
        print(f"[ERROR] Failed to fetch answers for {question_id}: {e}")
        return []

def format_so_as_markdown(item, answers, output_dir):
    number = item['question_id']
    title = html.unescape(item['title'])
    url = item['link']
    body = clean_html(item['body'])
    
    filename = f"so_{number}.md"
    filepath = os.path.join(output_dir, filename)
    
    content = f"# Q: {title}\n"
    content += f"**Source:** {url}\n\n"
    content += "## The Problem / Request\n"
    content += f"{body}\n\n"
    content += "## The Solution / Discussion\n"
    
    for idx, answer in enumerate(answers):
        ans_body = clean_html(answer['body'])
        if len(ans_body.strip()) > 20:
            is_accepted = " (Accepted Answer)" if answer.get('is_accepted') else ""
            content += f"### Response {idx + 1}{is_accepted}\n"
            content += f"{ans_body}\n\n"
            
    c_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            if f"content_hash: {c_hash}" in f.read():
                return False
                
    frontmatter = f"---\ntype: community_knowledge\nsource: github#{number}\ncontent_hash: {c_hash}\n---\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter + content)
    return True

def main():
    parser = argparse.ArgumentParser(description="Scrape Forum/Issues into Synapse Markdown docs.")
    parser.add_argument("--source", choices=["github", "stackoverflow"], default="github", help="Source to scrape from")
    parser.add_argument("--repo", default=None, help="Target repository for github source")
    parser.add_argument("--query", default=None, help="Search query for stackoverflow source")
    parser.add_argument("--limit", type=int, default=10, help="Number of threads to fetch")
    parser.add_argument("--outdir", default="synapse", help="Output directory")
    args = parser.parse_args()

    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): break
        if os.path.exists(os.path.join(current, "setup.sh")): break
        current = os.path.dirname(current)
    aim_root = current if current != '/' else os.getcwd()
    
    outdir_path = os.path.join(aim_root, args.outdir)
    os.makedirs(outdir_path, exist_ok=True)
    
    success_count = 0
    if args.source == "github":
        issues = fetch_closed_issues(args.repo, args.limit)
        if not issues:
            print("No issues found or command failed.")
            return
        for issue in issues:
            print(f"Processing Issue #{issue['number']}: {issue['title']}...")
            comments = fetch_issue_comments(issue['number'], args.repo)
            if format_issue_as_markdown(issue, comments, outdir_path):
                success_count += 1
    elif args.source == "stackoverflow":
        if not args.query:
            print("[ERROR] --query is required for stackoverflow source")
            return
        threads = fetch_stackoverflow_threads(args.query, args.limit)
        if not threads:
            print("No threads found.")
            return
        for thread in threads:
            print(f"Processing SO Question {thread['question_id']}: {html.unescape(thread['title'])}...")
            answers = fetch_stackoverflow_answers(thread['question_id'])
            if format_so_as_markdown(thread, answers, outdir_path):
                success_count += 1
            
    if success_count > 0:
        print(f"\n[SUCCESS] Formatted {success_count} resolved threads as markdown in {args.outdir}/")
        print(f"\nNext step — bake into an engram cartridge:")
        print(f"  aim bake {args.outdir}/ community-issues.engram")
        print(f"\nThen load it:")
        print(f"  aim jack-in community-issues.engram\n")
    else:
        print(f"\n[SUCCESS] No new threads to format in {args.outdir}/")

if __name__ == "__main__":
    main()
