#!/usr/bin/env python3
"""
Create a honeypot folder with a set of dummy files to protect.
Run once before starting the monitor/attacker.
"""
import os
from pathlib import Path
import textwrap

# logging integration
from activity_logger import get_logger
logger = get_logger(__name__)

HONEYPOT_DIR = Path("honeypot")
SAMPLE_COUNT = 6

def main():
    HONEYPOT_DIR.mkdir(exist_ok=True)
    (HONEYPOT_DIR / "backups").mkdir(exist_ok=True)
    logger.info("Ensured honeypot directories exist at %s", HONEYPOT_DIR.resolve())

    created = []
    for i in range(1, SAMPLE_COUNT + 1):
        p = HONEYPOT_DIR / f"document_{i}.txt"
        if not p.exists():
            p.write_text(textwrap.dedent(f"""\
                This is sample file {i} inside the honeypot.
                Treat as disposable test data.
                """))
            created.append(p.name)
    msg = f"Honeypot prepared at: {HONEYPOT_DIR.resolve()}"
    print(msg)
    logger.info(msg)

    print("Sample files:")
    for p in sorted(HONEYPOT_DIR.glob("*.txt")):
        print(" -", p.name)
    logger.debug("Sample files present: %s", ", ".join(p.name for p in sorted(HONEYPOT_DIR.glob("*.txt"))))

    if created:
        logger.info("Created new sample files: %s", ", ".join(created))
    else:
        logger.info("No new sample files created (already existed).")

    print("\nBackups will be kept in honeypot/backups/ when attacker runs.")
    logger.debug("Backups directory is: %s", (HONEYPOT_DIR / "backups").resolve())

if __name__ == "__main__":
    main()
