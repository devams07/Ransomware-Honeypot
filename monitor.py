#!/usr/bin/env python3
"""
Simple polling monitor that watches the honeypot folder for suspicious changes.
If it sees > threshold suspicious events within a sliding window, it:
 - prints an alert,
 - tries to isolate the attacker by invoking isolator.py with the attacker's PID.

Detection heuristic (simple & configurable):
 - a suspicious event = a filename ending with '.locked' OR file content contains '<<ENCRYPTED>>'
 - if we see >= SUSPICIOUS_THRESHOLD suspicious events within POLL_WINDOW seconds, trigger isolation.

This is intentionally simple for demonstration.
"""
import os
import time
import subprocess
from pathlib import Path
from collections import deque
import sys
import signal
from activity_logger import get_logger

logger = get_logger(__name__)

HONEYPOT_DIR = Path("honeypot")
POLL_INTERVAL = 0.8  # seconds
POLL_WINDOW = 8      # seconds: sliding window length to count suspicious events
SUSPICIOUS_THRESHOLD = 3  # number of suspicious events in sliding window to trigger

# How monitor will locate an attacker process for isolation:
# Option A: attacker writes its PID to a file "attacker.pid" (simple). We read that file.
ATTACKER_PID_FILE = Path("attacker.pid")  # attacker_sim writes this (we'll add a small helper below)

def read_files_snapshot():
    files = {}
    for p in HONEYPOT_DIR.glob("*"):
        if p.is_file():
            try:
                files[p.name] = p.stat().st_mtime
            except Exception:
                files[p.name] = None
    return files

def is_suspicious(p: Path):
    # suspicious if filename endswith .locked or content contains our marker
    try:
        if p.name.endswith(".locked"):
            return True
        # only examine small files for speed
        if p.stat().st_size < 10_000:
            content = p.read_text(errors="ignore")
            if "<<ENCRYPTED>>" in content:
                return True
    except Exception:
        return False
    return False

def get_attacker_pid():
    # If attacker.pid present, return int PID, else None
    try:
        if ATTACKER_PID_FILE.exists():
            t = ATTACKER_PID_FILE.read_text().strip()
            if t:
                return int(t)
    except Exception as e:
        logger.error("Error reading attacker PID file: %s", e)
    return None

def call_isolator(pid):
    # Call isolator.py as a separate process
    msg = f"[Monitor] Invoking isolator for PID {pid} ..."
    print(msg)
    logger.info("Invoking isolator for PID %s", pid)
    try:
        # use same python executable
        subprocess.run([sys.executable, "isolator.py", str(pid)], check=False)
    except Exception as e:
        err = f"Failed to run isolator: {e}"
        print(err)
        logger.error(err)

def main():
    if not HONEYPOT_DIR.exists():
        msg = "Honeypot folder not found. Run honeypot_setup.py first."
        print(msg)
        logger.error(msg)
        return

    start_msg = f"Monitor started. Watching: {HONEYPOT_DIR.resolve()}"
    print(start_msg)
    logger.info(start_msg)

    # maintain deque of event timestamps
    events = deque()
    last_snapshot = read_files_snapshot()

    try:
        while True:
            time.sleep(POLL_INTERVAL)
            snapshot = read_files_snapshot()

            # compare to previous snapshot for new/modified files
            suspicious_found = 0
            for name, mtime in snapshot.items():
                prev = last_snapshot.get(name)
                if prev is None or (mtime is not None and prev is not None and mtime > prev):
                    # file is new or modified
                    p = HONEYPOT_DIR / name
                    if is_suspicious(p):
                        suspicious_found += 1
                        events.append(time.time())
                        msg = f"[Monitor] Suspicious event detected on {name}"
                        print(msg)
                        logger.warning("Suspicious event detected on %s", name)

            # Also check for files that were renamed to .locked (present now but not before)
            for name in list(snapshot.keys()):
                if name.endswith(".locked") and name not in last_snapshot:
                    events.append(time.time())
                    msg = f"[Monitor] Detected new .locked file: {name}"
                    print(msg)
                    logger.warning("Detected new .locked file: %s", name)

            # prune events older than window
            cutoff = time.time() - POLL_WINDOW
            while events and events[0] < cutoff:
                events.popleft()

            if len(events) >= SUSPICIOUS_THRESHOLD:
                alert_msg = "\n!!! ALERT: Suspicious activity threshold reached !!!"
                print(alert_msg)
                logger.critical("ALERT: %d suspicious events within %ds - triggering isolation", len(events), POLL_WINDOW)
                summary_msg = f"Suspicious events in last {POLL_WINDOW}s: {len(events)}"
                print(summary_msg)
                logger.info(summary_msg)

                # try to isolate attacker
                pid = get_attacker_pid()
                if pid:
                    info_msg = f"[Monitor] Found attacker PID file: {pid}"
                    print(info_msg)
                    logger.info(info_msg)
                    call_isolator(pid)
                else:
                    fallback_msg = "[Monitor] No attacker PID file found. As a fallback, creating STOP_ATTACKER control file."
                    print(fallback_msg)
                    logger.warning("No attacker PID found; writing STOP_ATTACKER to request graceful stop.")
                    # create a STOP_ATTACKER file in honeypot to tell attacker to stop
                    try:
                        (HONEYPOT_DIR / "STOP_ATTACKER").write_text("monitor requested stop\n")
                        logger.info("STOP_ATTACKER file written to honeypot to request graceful stop.")
                    except Exception as e:
                        logger.error("Failed to write STOP_ATTACKER file: %s", e)

                # clear events after action to avoid repeated calls
                events.clear()
                cont_msg = "[Monitor] Action taken; monitoring will continue.\n"
                print(cont_msg)
                logger.info("Action taken; monitoring continues.")

            last_snapshot = snapshot

    except KeyboardInterrupt:
        exit_msg = "Monitor exiting (KeyboardInterrupt)."
        print(exit_msg)
        logger.info(exit_msg)

if __name__ == "__main__":
    main()
