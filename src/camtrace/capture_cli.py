# src/camtrace/capture_cli.py
from __future__ import annotations

import logging
import os
import stat
import subprocess  # nosec B404: required to invoke packaged script; shell=False below
import sys
from collections.abc import Sequence
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def run_capture(script_path: str | os.PathLike[str], argv: Sequence[str]) -> int:
    """
    Run the packaged capture script with explicit args.

    Security notes:
    - Script path is controlled by our package, not user input.
    - We do NOT use shell=True.
    - Lightly sanitize argv to avoid empty/NULL args.
    """
    script = Path(script_path)

    # Ensure the script exists
    try:
        resolved = script.resolve(strict=True)
    except FileNotFoundError as e:
        LOGGER.error("Capture script missing: %s", e)
        return 2

    # Ensure it's executable for the current user (best-effort)
    try:
        st = os.stat(resolved)
        os.chmod(resolved, st.st_mode | stat.S_IXUSR)
    except (OSError, PermissionError) as e:
        LOGGER.warning("Could not set +x on %s: %s", resolved, e)

    # Light argv sanitation
    sanitized_argv = [a for a in argv if a and "\x00" not in a]

    try:
        # Inputs are controlled; shell=False is intentional.
        completed = subprocess.run(  # nosec B603
            [str(resolved), *sanitized_argv],
            check=False,
        )
        return completed.returncode
    except OSError as e:
        LOGGER.error("Failed to execute capture script: %s", e)
        return 3


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    from importlib.resources import files

    script_path = files("camtrace").joinpath("bin/pcap_to_camtrace.sh")
    return run_capture(str(script_path), argv)


if __name__ == "__main__":
    raise SystemExit(main())
