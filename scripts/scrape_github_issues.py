#!/usr/bin/env python3
import os
import subprocess
import json
import argparse
from datetime import datetime

def run_gh_command(cmd_list):
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {' '.join(cmd_list)}")
        print(f"Error output: {e.stderr}")
        return None

def fetch_closed_issues(repo, limit=20):
    print(f"Fetching up to {limit} completed (solved) issues from {repo}...")
    # Fetch issues in JSON format including title, body, number, labels, stateReason
    cmd = [
        "gh", "issue", "list", 
        "--repo", repo, 
        "--state", "closed", 
        "--limit", str(limit * 3), # Fetch extra to account for discarded NOT_PLANNED issues
        "--json", "number,title,body,labels,url,stateReason"
    ]
    
    output = run_gh_command(cmd)
    if output:
        all_closed = json.loads(output)
        # Filter for genuinely solved issues (COMPLETED) rather than wontfix/duplicates (NOT_PLANNED)
        completed_issues = [i for i in all_closed if i.get("stateReason") == "COMPLETED"]
        return completed_issues[:limit]
    return []

def fetch_issue_comments(repo, issue_number):
    # Fetch comments for a specific issue
    cmd = [
        "gh", "issue", "view", str(issue_number),
        "--repo", repo,
        "--json", "comments"
    ]
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
    
    # Filter for useful comments (skip empty or very short ones)
    useful_comments = [c['body'] for c in comments if len(c['body'].strip()) > 20]
    
    if not useful_comments:
        return False # Skip issues with no answers/comments
        
    filename = f"issue_{number}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Format as a "User Prompt -> Resolution" Eureka pattern
    content = f"# Q: {title}\n"
    content += f"**Source:** {url}\n\n"
    
    content += "## The Problem / Request\n"
    content += f"{body}\n\n"
    
    content += "## The Solution / Discussion\n"
    for idx, comment in enumerate(useful_comments):
        content += f"### Response {idx + 1}\n"
        content += f"{comment}\n\n"
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return True

def main():
    parser = argparse.ArgumentParser(description="Scrape GitHub Issues into Synapse Markdown docs.")
    parser.add_argument("--repo", required=True, help="Target repository (e.g., google/gemini-cli)")
    parser.add_argument("--limit", type=int, default=10, help="Number of issues to fetch")
    parser.add_argument("--outdir", default="synapse/scraped_docs", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    
    issues = fetch_closed_issues(args.repo, args.limit)
    if not issues:
        print("No issues found or command failed.")
        return
        
    success_count = 0
    for issue in issues:
        print(f"Processing Issue #{issue['number']}: {issue['title']}...")
        comments = fetch_issue_comments(args.repo, issue['number'])
        
        if format_issue_as_markdown(issue, comments, args.outdir):
            success_count += 1
            
    print(f"\n[SUCCESS] Formatted {success_count} resolved issues as markdown in {args.outdir}/")

if __name__ == "__main__":
    main()