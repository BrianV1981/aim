import argparse
import datetime
import os

def log_heartbeat(log_path):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] [HEARTBEAT] System alive and registered."
    
    # Ensure directory exists
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    with open(log_path, "a") as f:
        f.write(message + "\n")
    print(message)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True, help="Path to daemon log file")
    args = parser.parse_args()
    
    log_heartbeat(args.log)

if __name__ == "__main__":
    main()
