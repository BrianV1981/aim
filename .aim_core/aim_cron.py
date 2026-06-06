#!/usr/bin/env python3
import os
import json
import time
import subprocess
import signal
from datetime import datetime
try:
    from croniter import croniter
except ImportError:
    print("[ERROR] croniter not found. Please run ./setup.sh to update dependencies.")
    import sys; sys.exit(1)

def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core", "CONFIG.json")) or os.path.exists(os.path.join(current, "setup.sh")):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
CRONTAB_PATH = os.path.join(AIM_ROOT, "core", "crontab.json")

# Global flag for signal interruption
INTERRUPTED = False

def handle_sighup(signum, frame):
    """Signal handler for SIGHUP. Forces the engine to wake up and recalculate schedules."""
    global INTERRUPTED
    log("SIGHUP received: Wake event triggered (Registry updated). Recalculating timers...")
    INTERRUPTED = True

def load_crontab():
    if not os.path.exists(CRONTAB_PATH):
        return []
    try:
        with open(CRONTAB_PATH, 'r') as f:
            return json.load(f)
    except:
        return []

def save_crontab(data):
    os.makedirs(os.path.dirname(CRONTAB_PATH), exist_ok=True)
    with open(CRONTAB_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [CRON] {msg}", flush=True)

def execute_task(task):
    session_name = f"cron_worker_{task['task_id']}"
    
    check_cmd = subprocess.run(["tmux", "has-session", "-t", session_name], capture_output=True)
    if check_cmd.returncode == 0:
        log(f"Task {task['task_id']} is already running. Skipping execution.")
        return

    log(f"Spawning worker for task: {task['task_id']}")
    try:
        subprocess.run(["tmux", "new-session", "-d", "-s", session_name, "-c", AIM_ROOT, "gemini --yolo"], check=True)
        time.sleep(5) 
        
        prompt = f"Wake up. You are a Background Cron Worker executing task {task['task_id']}. \nDIRECTIVE: {task['prompt']} \nOnce you have completed this directive, you MUST execute `tmux kill-session -t {session_name}` to terminate."
        subprocess.run(["tmux", "set-buffer", prompt], check=True)
        subprocess.run(["tmux", "paste-buffer", "-t", session_name], check=True)
        time.sleep(1)
        subprocess.run(["tmux", "send-keys", "-t", session_name, "Enter"], check=True)
    except Exception as e:
        log(f"Failed to spawn worker {task['task_id']}: {e}")

def get_next_sleep_time(tasks, now):
    """Calculates the exact number of seconds until the absolute closest scheduled task."""
    min_sleep = None
    
    for task in tasks:
        if 'last_run' not in task:
            task['last_run'] = now.timestamp() - 60 

        try:
            base_time = datetime.fromtimestamp(task['last_run'])
            iter = croniter(task['cron_expression'], base_time)
            next_run = iter.get_next(datetime)
            
            diff = (next_run - now).total_seconds()
            
            # If a task is due exactly now or in the past, return 0 for immediate execution
            if diff <= 0:
                return 0
                
            if min_sleep is None or diff < min_sleep:
                min_sleep = diff
        except Exception as e:
            log(f"Cron expression error for {task.get('task_id')}: {e}")
            
    return min_sleep

def run_loop():
    global INTERRUPTED
    # Register the wake-up signal handler
    signal.signal(signal.SIGHUP, handle_sighup)
    
    log("A.I.M. Intelligent Cron Engine Started.")
    
    while True:
        try:
            INTERRUPTED = False
            now = datetime.now()
            tasks = load_crontab()
            
            if not tasks:
                log("Crontab is empty. Entering Deep Sleep (24h standby).")
                # Sleep in small chunks so we can be interrupted gracefully
                for _ in range(86400):
                    if INTERRUPTED: break
                    time.sleep(1)
                continue

            updated_tasks = []
            tasks_executed = False
            
            # 1. Execute any tasks that are currently due
            for task in tasks:
                if 'last_run' not in task:
                    task['last_run'] = now.timestamp() - 60

                try:
                    base_time = datetime.fromtimestamp(task['last_run'])
                    iter = croniter(task['cron_expression'], base_time)
                    next_run = iter.get_next(datetime)
                    
                    if next_run <= now:
                        execute_task(task)
                        task['last_run'] = now.timestamp()
                        tasks_executed = True
                        
                        if 'max_iterations' in task and task['max_iterations'] > 0:
                            task['current_iterations'] = task.get('current_iterations', 0) + 1
                            if task['current_iterations'] >= task['max_iterations']:
                                log(f"Task {task['task_id']} reached max iterations. Removing from registry.")
                                continue 
                except Exception:
                    pass
                    
                updated_tasks.append(task)
                
            if tasks_executed:
                save_crontab(updated_tasks)
                now = datetime.now() # Update time after executions
                
            # 2. Calculate the exact time until the next scheduled task
            sleep_time = get_next_sleep_time(updated_tasks, now)
            
            if sleep_time is None:
                log("No valid upcoming schedules. Entering Deep Sleep (24h standby).")
                sleep_time = 86400
            elif sleep_time == 0:
                # Catch edge cases where a task is due immediately
                sleep_time = 60 - now.second

            log(f"Calculated next execution. Engine going to sleep for {sleep_time:.1f} seconds...")
            
            # 3. Intelligent Sleep (Interruptible by SIGHUP)
            # We break the sleep into 1-second chunks so the SIGHUP flag can break the loop instantly
            for _ in range(int(sleep_time)):
                if INTERRUPTED:
                    break
                time.sleep(1)
            
        except KeyboardInterrupt:
            log("Cron Engine terminated by user.")
            break
        except Exception as e:
            log(f"Fatal error in loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        run_loop()
    else:
        # Fork to background
        import subprocess
        log("Forking Cron Engine to background...")
        subprocess.Popen(["nohup", sys.executable, os.path.abspath(__file__), "run"], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)