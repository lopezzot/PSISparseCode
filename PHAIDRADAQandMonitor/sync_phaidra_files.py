#!/usr/bin/env python3
"""Synchronize closed Phaidra DAQ files from the local folder to the network drive."""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import psutil

LOCAL_DIR = Path.cwd()
BACKUP_DIR = Path("/psi.ch/.cifs-server/fs02.psi.ch/ea_messdaten/phaidra/2026/")
FILE_PREFIX = "phaidra_data"


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


def open_local_daq_files():
    """Return local Phaidra data filenames currently open by any process."""
    open_names = set()
    local_dir = LOCAL_DIR.resolve()

    for process in psutil.process_iter(["open_files"]):
        try:
            for opened_file in process.info["open_files"] or []:
                try:
                    path = Path(opened_file.path).resolve()

                    if (
                        path.parent == local_dir
                        and path.name.startswith(FILE_PREFIX)
                        and path.suffix == ".txt"
                    ):
                        open_names.add(path.name)

                except (OSError, RuntimeError):
                    continue

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
            OSError,
        ):
            continue

    return open_names


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


def sync_closed_files(active_file=None):
    """Copy closed local DAQ files missing or incomplete on the network drive.

    `active_file` can be supplied by phaidra.py. When this script is run alone,
    psutil is used to skip files currently open by a process.

    Returns True if the scan completes successfully, otherwise False.
    """
    available, error = check_backup_drive()

    if not available:
        print(f"[{timestamp()}] WARNING: Network drive unavailable: {error}")
        return False

    active_name = Path(active_file).name if active_file is not None else None

    try:
        local_files = sorted(LOCAL_DIR.glob(f"{FILE_PREFIX}*.txt"))
        open_names = open_local_daq_files()

        for source in local_files:
            if not source.is_file() or source.name == active_name:
                continue

            # Skip files that are currently open.
            if source.name in open_names:
                continue

            destination = BACKUP_DIR / source.name

            try:
                source_size = source.stat().st_size

                # Skip files already present with the same size.
                if destination.exists() and destination.stat().st_size == source_size:
                    continue

                # Recheck immediately before copying in case the DAQ rotated files.
                if source.name in open_local_daq_files():
                    continue

                if source.name == active_name:
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
