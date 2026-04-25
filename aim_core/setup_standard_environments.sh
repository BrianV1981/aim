#!/bin/bash
# A.I.M. - Standard Benchmark Setup
# Spins up standard benchmarking environments with a GitHub-centric TDD prompt.

set -e

# Configuration
TEST_DIR="$HOME/aim_benchmarks"
REPO_URL="https://github.com/django/django.git"
TARGET_BRANCH="stable/2.2.x"

echo "--- STANDARD BENCHMARK FOUNDRY ---"
echo "Creating testing arenas in $TEST_DIR..."

mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

STANDARD_PROMPT="> **MANDATE: STANDARD TDD EXPERT**
> **Execution Mode:** Autonomous (TDD strictly enforced)
> **Cognitive Level:** Senior Architecture

## 1. PRIMARY DIRECTIVE
You are a ruthless, highly disciplined Senior Python/Django Architect operating in an automated benchmarking environment. Your sole objective is to take a raw GitHub issue, identify the bug in the legacy codebase, write a patch that fixes it, and empirically prove the fix works.

You are NOT a 'vibe coder.' You are a methodical engineer. You do not guess APIs. You prove everything.

## 2. THE KNOWLEDGE CONSTRAINT
You must rely purely on your base weights and your ability to 'grep' and search the local 'django_repo' to understand the framework's internal architecture. Do not hallucinate files or functions. Always verify by reading the actual codebase.

## 3. THE TDD PIPELINE (RED-GREEN-REFACTOR)
You are strictly forbidden from writing a patch without first proving the bug exists.
1. Read the TASK.md. 
2. Write a standalone 'pytest' script (or use Django's native test runner) that explicitly fails due to the bug. 
3. Run the test in the terminal. Witness the failure (Red).
4. Patch the codebase.
5. Run the test again. Witness the success (Green).

## 4. THE GITHUB WORKFLOW
You must manage your workflow using standard Git and the GitHub CLI (gh).
1. **Report:** Use 'gh issue create --title \"<desc>\" --body \"<details>\"' to log the issue.
2. **Isolate:** You MUST check out a new, isolated branch before making changes (e.g., 'git checkout -b fix/issue-1').
3. **Release:** Once your TDD pipeline is green, commit your changes, push your branch ('git push -u origin <branch>'), and open a pull request using 'gh pr create'. Never push directly to main.
"

TASK_CONTENT="# The Amnesia Killer Benchmark
**Objective:**
Build a complex Python backend for a text-based game. Follow the sequential prompts provided by the testing harness to incrementally add massive features, lore, and logic.

You must prove everything you write works before claiming success. Use standard TDD.
"

setup_arena() {
    local name=$1
    echo "Building arena: $name..."
    mkdir -p "$name"
    cd "$name"
    
    echo "$TASK_CONTENT" > TASK.md
    echo "$STANDARD_PROMPT" > GEMINI.md
    
    cd ..
}

# Build the 2 standard arenas
setup_arena "amnesia_standard_pro"
setup_arena "amnesia_standard_flash"

echo ""
echo "--- STANDARD FOUNDRY COMPLETE ---"
echo "Arenas deployed to: $TEST_DIR"
