#!/usr/bin/env python3
import json
import subprocess
import sys
import time
import hashlib
from pathlib import Path

INBOX = Path.home() / "sovereign_vault" / "torrent_inbox"
LOG   = Path.home() / "sovereign_vault" / "logs" / "torrent_events.jsonl"

def classify(name: str):
    return ["generic"]

def fractal_id(name: str) -> str:
    h = hashlib.sha256(name.encode()).hexdigest()[:12]
    return "TOR-" + h

def write_event(ev: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(ev)
    with LOG.open("a") as f:
        f.write(line)
        f.write("
")
    print(line)

def pull(magnet: str) -> dict:
    INBOX.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["aria2c", "--dir", str(INBOX), magnet],
        capture_output=True,
        text=True,
    )
    return {
        "ts": int(time.time()),
        "event": "download_complete",
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout.splitlines()[-5:],
        "stderr_tail": proc.stderr.splitlines()[-5:],
    }

def main() -> None:
    if len(sys.argv) < 3:
        print("usage: torrent_pull.py '<name>' '<magnet>'", file=sys.stderr)
        sys.exit(1)

    name   = sys.argv[1]
    magnet = sys.argv[2]

    first = {
        "ts": int(time.time()),
        "event": "queued",
        "name": name,
        "tags": classify(name),
        "fractal_id": fractal_id(name),
        "magnet_prefix": magnet[:120],
    }
    write_event(first)

    result = pull(magnet)
    result["name"] = name
    result["fractal_id"] = first["fractal_id"]
    write_event(result)

if __name__ == "__main__":
    main()
