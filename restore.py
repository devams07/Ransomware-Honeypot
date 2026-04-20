#!/usr/bin/env python3
"""
Restore script for honeypot demo.

Copies all backup files (*.bak) from honeypot/backups/ back to honeypot/,
removes .locked files, attacker.pid, and STOP_ATTACKER if present.

Usage:
    python restore.py        # safe restore (skip if file exists)
    python restore.py --force  # overwrite existing files
"""

import sys
import shutil
from pathlib import Path
from activity_logger import get_logger

logger = get_logger(__name__)

HONEYPOT_DIR = Path("honeypot")
BACKUP_DIR = HONEYPOT_DIR / "backups"

def restore_files(force=False):
    restored = 0
    skipped = 0
    removed_locked = 0

    if not BACKUP_DIR.exists():
        msg = f"No backup directory found at: {BACKUP_DIR}"
        print(msg)
        logger.error(msg)
        return

    # Restore backups
    for bak in BACKUP_DIR.glob("*.bak"):
        original_name = bak.stem  # remove .bak suffix
        target = HONEYPOT_DIR / original_name

        if target.exists() and not force:
            skipped += 1
            msg = f"Skipped existing file: {target.name} (use --force to overwrite)"
            print(msg)
            logger.warning(msg)
            continue

        try:
            shutil.copy2(bak, target)
            restored += 1
            msg = f"Restored: {target.name} (from {bak.name})"
            print(msg)
            logger.info(msg)
        except Exception as e:
            msg = f"Error restoring {bak.name}: {e}"
            print(msg)
            logger.error(msg)

    # Remove .locked files (simulated encrypted files)
    for locked in HONEYPOT_DIR.glob("*.locked"):
        try:
            locked.unlink()
            removed_locked += 1
            msg = f"Removed simulated encrypted file: {locked.name}"
            print(msg)
            logger.info(msg)
        except Exception as e:
            msg = f"Failed to remove {locked.name}: {e}"
            print(msg)
            logger.error(msg)

    # Cleanup control files
    pid_file = Path("attacker.pid")
    stop_file = HONEYPOT_DIR / "STOP_ATTACKER"

    for f in [pid_file, stop_file]:
        if f.exists():
            try:
                f.unlink()
                msg = f"Removed {f}"
                print(msg)
                logger.info(msg)
            except Exception as e:
                msg = f"Failed to remove {f}: {e}"
                print(msg)
                logger.error(msg)

    summary = (
        f"\nSummary:\n"
        f" Restored files: {restored}\n"
        f" Skipped (existing, not forced): {skipped}\n"
        f" Removed .locked files: {removed_locked}\n"
    )
    print(summary)
    logger.info("Restore summary - Restored: %d, Skipped: %d, Removed locked: %d",
                restored, skipped, removed_locked)

def main():
    force = "--force" in sys.argv
    logger.info("Starting restore process (force=%s)", force)
    restore_files(force)
    logger.info("Restore process completed successfully.")

if __name__ == "__main__":
    main()
