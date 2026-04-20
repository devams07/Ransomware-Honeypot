#!/usr/bin/env python3
import os
import time
import signal
from pathlib import Path
import shutil

# ✅ import the logger utility
from activity_logger import get_logger
logger = get_logger(__name__)

HONEYPOT_DIR = Path("honeypot")
BACKUP_DIR = HONEYPOT_DIR / "backups"
SLEEP_BETWEEN = 1.2
PID_FILE = Path("attacker.pid")

def graceful_exit(signum, frame):
    msg = "Attacker simulator received termination signal, exiting cleanly."
    print(msg)
    logger.info(msg)
    if PID_FILE.exists():
        PID_FILE.unlink(missing_ok=True)
        logger.info("PID file removed on graceful exit.")
    raise SystemExit(0)

def main():
    signal.signal(signal.SIGTERM, graceful_exit)
    signal.signal(signal.SIGINT, graceful_exit)

    if not HONEYPOT_DIR.exists():
        msg = "Honeypot directory not found. Run honeypot_setup.py first."
        print(msg)
        logger.error(msg)
        return

    # publish PID so monitor can find & isolate us
    PID_FILE.write_text(str(os.getpid()))
    msg = f"Attacker simulator starting. PID: {os.getpid()}"
    print(msg)
    logger.info(msg)

    BACKUP_DIR.mkdir(exist_ok=True)
    txt_files = sorted([p for p in HONEYPOT_DIR.glob("*.txt")])
    if not txt_files:
        msg = "No files to 'encrypt'. Create honeypot files first."
        print(msg)
        logger.warning(msg)
        return

    for p in txt_files:
        # Check for STOP_ATTACKER file created by monitor
        if (HONEYPOT_DIR / "STOP_ATTACKER").exists():
            msg = "STOP_ATTACKER file detected — attacker stopping gracefully."
            print(msg)
            logger.info(msg)
            break

        # Backup original file
        backup_path = BACKUP_DIR / (p.name + ".bak")
        shutil.copy2(p, backup_path)
        msg = f"Backed up {p.name} -> {backup_path.name}"
        print(msg)
        logger.info(msg)

        # Simulate encryption
        try:
            p.write_text("<<ENCRYPTED>>\nThis is a simulation marker. Original in backups.")
            locked = p.with_suffix(p.suffix + ".locked")
            p.rename(locked)
            msg = f"Simulated encrypt: {p.name} -> {locked.name}"
            print(msg)
            logger.warning(msg)
        except Exception as e:
            msg = f"Error simulating encrypt for {p.name}: {e}"
            print(msg)
            logger.error(msg)

        time.sleep(SLEEP_BETWEEN)

    # cleanup pid file on normal finish
    if PID_FILE.exists():
        PID_FILE.unlink(missing_ok=True)
        logger.info("PID file removed on normal finish.")

    msg = "Attacker simulator finished."
    print(msg)
    logger.info(msg)

    time.sleep(2)

if __name__ == "__main__":
    main()
