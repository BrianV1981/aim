#!/usr/bin/env python3
import json

def main():
    print(json.dumps({"status": "documentation_only", "message": "This is a declarative skill for aim-google CLI. Run aim-google directly."}))

if __name__ == "__main__":
    main()