import time
import subprocess
import argparse

def ping(session, message):
    hint = f"User hint: [PLAN PINGER] {message}"
    subprocess.run(["tmux", "send-keys", "-t", session, hint, "Enter"])
    print(f"Pinged session {session} at {time.strftime('%H:%M:%S')}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", required=True, help="Target tmux session")
    parser.add_argument("--interval", type=int, help="Interval in seconds for time-based pings")
    parser.add_argument("--tail", help="File to watch for log changes")
    parser.add_argument("--pattern", help="Log pattern to trigger ping")
    parser.add_argument("--msg", required=True, help="The reminder message")
    
    args = parser.parse_args()

    print(f"Pinger started for session: {args.session}")

    if args.interval:
        while True:
            time.sleep(args.interval)
            ping(args.session, args.msg)
    elif args.tail and args.pattern:
        process = subprocess.Popen(['tail', '-f', args.tail], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in iter(process.stdout.readline, b''):
            if args.pattern in line.decode():
                ping(args.session, args.msg)

if __name__ == "__main__":
    main()
