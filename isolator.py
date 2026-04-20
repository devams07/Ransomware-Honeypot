#!/usr/bin/env python3
"""
Isolator script: called by monitor.py with a PID argument.
Attempts to stop/kill the process and prints & logs the result.
If the process is successfully terminated, automatically runs restore.py
to restore honeypot files from backups.

Safe demo notes:
 - restore.py will only be called after a confirmed process termination.
 - This script assumes restore.py is in the same folder and that running it is safe.
"""
import os
import sys
import signal
import platform
import subprocess
import time
from activity_logger import get_logger

logger = get_logger(__name__)

def _process_exists(pid: int) -> bool:
    """Return True if a process with pid exists (best-effort)."""
    try:
        # On POSIX this will raise OSError if no such process
        os.kill(pid, 0)
    except OSError:
        return False
    except PermissionError:
        # Process exists but we don't have permission to signal it
        return True
    return True

def isolate_pid(pid: int) -> bool:
    """
    Attempt to terminate the process identified by pid.
    Returns True if the process was confirmed terminated, False otherwise.
    """
    system = platform.system()
    msg = f"[Isolator] Attempting to isolate PID {pid} on {system}"
    print(msg)
    logger.info(msg)

    try:
        if system == "Windows":
            # Try taskkill /F (force). taskkill returns non-zero on failure.
            try:
                res = subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=False,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                logger.info("taskkill stdout: %s", res.stdout.strip())
                if res.returncode == 0:
                    # confirm process gone (best-effort)
                    time.sleep(0.5)
                    if not _process_exists(pid):
                        msg_ok = f"[Isolator] PID {pid} terminated via taskkill."
                        print(msg_ok)
                        logger.info(msg_ok)
                        return True
                    else:
                        msg_fail = f"[Isolator] taskkill reported success but PID {pid} still exists."
                        print(msg_fail)
                        logger.warning(msg_fail)
                        return False
                else:
                    msg_err = f"[Isolator] taskkill failed (returncode={res.returncode}): {res.stderr.strip()}"
                    print(msg_err)
                    logger.error(msg_err)
                    return False
            except FileNotFoundError:
                # taskkill not available? unlikely on Windows, but handle gracefully
                err = "[Isolator] taskkill not found on system."
                print(err)
                logger.error(err)
                return False

        else:
            # POSIX flow: SIGTERM, wait, then SIGKILL if needed
            try:
                os.kill(pid, signal.SIGTERM)
                msg = f"[Isolator] Sent SIGTERM to PID {pid}"
                print(msg)
                logger.info(msg)
            except PermissionError as pe:
                msg = f"[Isolator] Permission error sending SIGTERM to PID {pid}: {pe}"
                print(msg)
                logger.error(msg)
                return False
            except OSError as oe:
                # No such process or other error
                msg = f"[Isolator] Error sending SIGTERM to PID {pid}: {oe}"
                print(msg)
                logger.error(msg)
                # If process doesn't exist already, consider it terminated
                if not _process_exists(pid):
                    logger.info("[Isolator] Process already absent; treating as terminated.")
                    return True
                return False

            # give process a moment to exit
            for _ in range(10):  # ~1 second (10 * 0.1)
                time.sleep(0.1)
                if not _process_exists(pid):
                    msg_ok = f"[Isolator] PID {pid} terminated after SIGTERM."
                    print(msg_ok)
                    logger.info(msg_ok)
                    return True

            # still alive — escalate to SIGKILL
            try:
                msg_warn = f"[Isolator] PID {pid} still alive, sending SIGKILL"
                print(msg_warn)
                logger.warning(msg_warn)
                os.kill(pid, signal.SIGKILL)
            except PermissionError as pe:
                msg = f"[Isolator] Permission error sending SIGKILL to PID {pid}: {pe}"
                print(msg)
                logger.error(msg)
                return False
            except OSError as oe:
                msg = f"[Isolator] Error sending SIGKILL to PID {pid}: {oe}"
                print(msg)
                logger.error(msg)
                # If process is gone now, treat as success
                if not _process_exists(pid):
                    logger.info("[Isolator] Process absent after attempted SIGKILL; treating as terminated.")
                    return True
                return False

            # wait a short time then confirm
            time.sleep(0.2)
            if not _process_exists(pid):
                msg_ok2 = f"[Isolator] PID {pid} terminated after SIGKILL."
                print(msg_ok2)
                logger.info(msg_ok2)
                return True
            else:
                msg_fail2 = f"[Isolator] PID {pid} still exists after SIGKILL."
                print(msg_fail2)
                logger.error(msg_fail2)
                return False

    except Exception as e:
        msg_exc = f"[Isolator] Unexpected error while isolating PID {pid}: {e}"
        print(msg_exc)
        logger.exception(msg_exc)
        return False

def run_restore_after_success():
    """Run restore.py using the same python interpreter and log outcome."""
    try:
        logger.info("Invoking restore.py to restore honeypot files.")
        print("[Isolator] Invoking restore.py to restore honeypot files.")
        res = subprocess.run([sys.executable, "restore.py"], check=False)
        logger.info("restore.py finished with returncode %s", res.returncode)
        print(f"[Isolator] restore.py finished (returncode={res.returncode})")
    except Exception as e:
        msg = f"[Isolator] Failed to run restore.py: {e}"
        print(msg)
        logger.error(msg)

def main():
    if len(sys.argv) < 2:
        msg = "Usage: python isolator.py <pid>"
        print(msg)
        logger.error(msg)
        sys.exit(2)
    try:
        pid = int(sys.argv[1])
    except ValueError:
        msg = "Invalid PID."
        print(msg)
        logger.error(msg)
        sys.exit(2)

    logger.info("Isolator invoked for PID %s", pid)
    success = isolate_pid(pid)

    if success:
        msg = f"[Isolator] Isolation successful for PID {pid}. Proceeding to restore."
        print(msg)
        logger.info(msg)
        # run restore.py (safe: restore script will remove attacker.pid and STOP_ATTACKER)
        run_restore_after_success()
    else:
        msg = f"[Isolator] Isolation failed for PID {pid}. Not running restore.py."
        print(msg)
        logger.warning(msg)

if __name__ == "__main__":
    main()
