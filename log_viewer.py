# log_viewer.py
import time
from pathlib import Path

LOG = Path("activity.log")
if not LOG.exists():
    print("No log file yet. Run some actions first.")
    raise SystemExit(1)

with LOG.open("r", encoding="utf-8") as f:
    # go to end
    f.seek(0, 2)
    try:
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.3)
                continue
            print(line, end="")
    except KeyboardInterrupt:
        print("\nStopped tailing.")
