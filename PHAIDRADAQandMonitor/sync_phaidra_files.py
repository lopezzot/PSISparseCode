#!/usr/bin/env python3
"""Synchronize closed Phaidra DAQ files from the local folder to the network drive."""

import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

LOCAL_DIR = Path.cwd()
BACKUP_DIR = Path(
    "/psi.ch/.cifs-server/fs02.psi.ch/ea_messdaten/phaidra/2026/"
)
FILE_PREFIX = "phaidra_data"
ACTIVE_FILE_MARKER = LOCAL_DIR / ".phaidra_active_file"


def timestamp():
    """Return the current local time for terminal messages."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def check_backup_drive():
    """Return (available, error) after checking whether the drive is writable."""
    try:
        with tempfile.NamedTemporaryFile(dir=BACKUP_DIR):
            pass
        return True, None
    except OSError as error:
        return False, error


def mark_active_file(file_path):
    """Record the current output filename so synchronization can skip it."""
    temp_marker = ACTIVE_FILE_MARKER.with_name(
        f"{ACTIVE_FILE_MARKER.name}.{os.getpid()}.tmp"
    )
    try:
        temp_marker.write_text(f"{os.getpid()}\n{file_path.name}\n", encoding="utf-8")
        temp_marker.replace(ACTIVE_FILE_MARKER)
    except OSError as error:
        print(f"[{timestamp()}] WARNING: Cannot update active-file marker: {error}")
        try:
            temp_marker.unlink(missing_ok=True)
        except OSError:
            pass


def clear_active_file_marker():
    """Remove this process's active-file marker after acquisition ends."""
    try:
        lines = ACTIVE_FILE_MARKER.read_text(encoding="utf-8").splitlines()
        if lines and int(lines[0]) == os.getpid():
            ACTIVE_FILE_MARKER.unlink(missing_ok=True)
    except FileNotFoundError:
        pass
    except (OSError, ValueError) as error:
        print(f"[{timestamp()}] WARNING: Cannot remove active-file marker: {error}")


def _active_filename():
    """Return the active filename, clearing a marker left by a dead process."""
    try:
        lines = ACTIVE_FILE_MARKER.read_text(encoding="utf-8").splitlines()
        pid, filename = int(lines[0]), lines[1]
    except (OSError, ValueError, IndexError):
        return None

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        try:
            ACTIVE_FILE_MARKER.unlink(missing_ok=True)
        except OSError:
            pass
        return None
    except PermissionError:
        # The process exists, but this process cannot signal it.
        pass
    except OSError:
        # Be conservative: if process status is uncertain, skip the marked file.
        return filename

    return filename


def copy_file_atomically(source, destination):
    """Copy to a temporary file first, then replace the destination on success."""
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)

        shutil.copy2(source, temp_path)
        temp_path.replace(destination)
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def sync_closed_files():
    """Copy local closed DAQ files that are missing or incomplete on the drive.

    Returns True if the scan completes successfully, otherwise False.
    """
    available, error = check_backup_drive()
    if not available:
        print(f"[{timestamp()}] WARNING: Network drive unavailable: {error}")
        return False

    try:
        local_files = sorted(LOCAL_DIR.glob(f"{FILE_PREFIX}*.txt"))
        for source in local_files:
            # Recheck the marker before every copy in case acquisition rotated files.
            if not source.is_file() or source.name == _active_filename():
                continue

            destination = BACKUP_DIR / source.name
            try:
                if destination.exists() and destination.stat().st_size == source.stat().st_size:
                    continue
                copy_file_atomically(source, destination)
                print(f"[{timestamp()}] Synced {source.name} to network drive.")
            except OSError as error:
                print(f"[{timestamp()}] WARNING: Could not sync {source.name}: {error}")
                return False
    except OSError as error:
        print(f"[{timestamp()}] WARNING: Could not scan local DAQ files: {error}")
        return False

    return True


if __name__ == "__main__":
    raise SystemExit(0 if sync_closed_files() else 1)
