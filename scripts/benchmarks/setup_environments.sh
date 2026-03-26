#!/bin/bash
# A.I.M. - Automated 4-Way Benchmark Setup
# Spins up perfectly isolated control and matrix environments targeting a specific codebase.

set -e

# Configuration
TEST_DIR="$HOME/aim_benchmarks"
REPO_URL="https://github.com/django/django.git"
TARGET_BRANCH="stable/2.2.x"  # Checking out an old, vulnerable branch
AIM_SOURCE="$HOME/aim"

echo "--- A.I.M. BENCHMARK FOUNDRY ---"
echo "Creating testing arenas in $TEST_DIR..."

mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Define Prompts
CONTROL_PROMPT="> **MANDATE: PURE PROMPTOLOGY (CONTROL)**
> **Execution Mode:** Autonomous (TDD strictly enforced)
> **Cognitive Level:** Senior Architecture

## 1. PRIMARY DIRECTIVE
You are a ruthless, highly disciplined Senior Python/Django Architect operating in an automated benchmarking environment. Your sole objective is to take a raw GitHub issue, identify the bug in the legacy codebase, write a patch that fixes it, and empirically prove the fix works.

You are NOT a 'vibe coder.' You are a methodical engineer. You do not guess APIs. You prove everything.

## 2. THE KNOWLEDGE CONSTRAINT
You do not have access to external search engines or documentation. You must rely purely on your base weights and your ability to 'grep' and search the local 'django_repo' to understand the framework's internal architecture.

## 3. THE TDD PIPELINE (RED-GREEN-REFACTOR)
You are strictly forbidden from writing a patch without first proving the bug exists.
1. Read the TASK.md. 
2. Write a standalone 'pytest' script (or use Django's native test runner) that explicitly fails due to the bug. 
3. Run the test in the terminal. Witness the failure (Red).
4. Patch the codebase.
5. Run the test again. Witness the success (Green).
"

MATRIX_PROMPT="> **MANDATE: THE DJANGO / PYTHON MATRIX EXPERT**
> **Execution Mode:** Autonomous (TDD strictly enforced)
> **Cognitive Level:** Senior Architecture

## 1. PRIMARY DIRECTIVE
You are a ruthless, highly disciplined Senior Python/Django Architect operating in an automated benchmarking environment. Your sole objective is to take a raw GitHub issue, identify the bug in the legacy codebase, write a patch that fixes it, and empirically prove the fix works.

You are NOT a 'vibe coder.' You are a methodical engineer. You do not guess APIs. You prove everything.

## 2. THE KNOWLEDGE MATRIX (DO NOT GUESS)
You have been injected with highly specialized knowledge cartridges. Before proposing a plan or writing code, you MUST use 'aim_os search \"<concept>\"' to pull the definitive architectural rules from your Engram DB. Never hallucinate APIs.

## 3. THE TDD PIPELINE (RED-GREEN-REFACTOR)
You are strictly forbidden from writing a patch without first proving the bug exists.
1. Read the TASK.md. 
2. Write a standalone 'pytest' script (or use Django's native test runner) that explicitly fails due to the bug. 
3. Run the test in the terminal. Witness the failure (Red).
4. Patch the codebase.
5. Run the test again. Witness the success (Green).

## 4. THE GITOPS MANDATE
1. **Report:** Use 'aim_os bug \"desc\"' to log the issue.
2. **Isolate:** You MUST use 'aim_os fix <id>' to check out an isolated branch.
3. **Release:** Use 'aim_os push \"msg\"' only when the TDD pipeline is green.
"

TASK_CONTENT="# SWE-Bench Target (Proxy)
**Title:** URLValidator rejects valid IPv6 addresses when they contain mixed-case hex digits.
**Objective:**
1. Locate the URLValidator in the django_repo codebase.
2. Fix the regex pattern to correctly support mixed-case IPv6 literals (A-F).
3. Prove your fix works using your mandated TDD workflow.
"

# --- ARCHITECTURAL MANDATES ---
# 1. The Universal Hook Router: A.I.M. relies on a global '~/.gemini/aim_router.py' to manage background loops (Mantra, Memory). 
#    This router dynamically detects the active workspace. This allows us to run 4 concurrent benchmark arenas simultaneously 
#    without them cross-contaminating each other's databases.
# 2. Directory Naming: The A.I.M. clone MUST be named 'aim_os' (or similar) to prevent the agent from getting confused 
#    between the A.I.M. framework code and the target test code.
# 3. The Workstation: The actual test codebase (e.g. django_repo) and the TASK.md MUST be placed inside an 'aim_os/workspace' folder. 
#    The AI is instructed to operate *from* this workspace directory. The router will walk up the tree to find the engram.db.

# Setup Function
setup_arena() {
    local name=$1
    local type=$2
    
    echo "Building arena: $name..."
    mkdir -p "$name"
    cd "$name"
    
    if [ "$type" == "control" ]; then
        # Control arenas just get the raw code and the prompt at the root
        echo "$TASK_CONTENT" > TASK.md
        echo "$CONTROL_PROMPT" > GEMINI.md
        
        if [ ! -d "django_repo" ]; then
            git clone --depth 1 --branch "$TARGET_BRANCH" "$REPO_URL" django_repo >/dev/null 2>&1
            rm -rf django_repo/.git
            git init >/dev/null 2>&1
            git add . >/dev/null 2>&1
            git commit -m "Baseline: Vulnerable codebase" >/dev/null 2>&1
        fi
        cd ..

    elif [ "$type" == "matrix" ]; then
        # Matrix arenas require the strict aim_os -> workspace structural mandate
        git clone "$AIM_SOURCE" aim_os >/dev/null 2>&1
        cd aim_os
        
        # Initialize the exoskeleton
        ./setup.sh >/dev/null 2>&1
        cp "$AIM_SOURCE"/*.engram . 2>/dev/null || true
        printf "1\n1\n" | ./venv/bin/python3 scripts/aim_cli.py init >/dev/null 2>&1
        ./venv/bin/python3 scripts/aim_cli.py jack-in django.engram >/dev/null 2>&1
        
        # Inject the specialized prompt
        echo "$MATRIX_PROMPT" > GEMINI.md
        
        # Build the isolated workspace *inside* aim_os
        mkdir -p workspace
        cd workspace
        echo "$TASK_CONTENT" > TASK.md
        
        git clone --depth 1 --branch "$TARGET_BRANCH" "$REPO_URL" django_repo >/dev/null 2>&1
        rm -rf django_repo/.git
        git init >/dev/null 2>&1
        git add . >/dev/null 2>&1
        git commit -m "Baseline: Vulnerable codebase" >/dev/null 2>&1
        
        # Return to the arena root
        cd ../..
    fi
}

# Build the 4 arenas
setup_arena "django_control_pro" "control"
setup_arena "django_control_flash" "control"
setup_arena "django_matrix_pro" "matrix"
setup_arena "django_matrix_flash" "matrix"

echo ""
echo "--- FOUNDRY COMPLETE ---"
echo "Arenas deployed to: $TEST_DIR"
echo "To test a Matrix Agent, remember to 'cd aim_os', 'source ~/.bashrc', and use 'aim_os status'!"