"""Bound import processes and require evidence that their final checks ran."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
import secrets
import signal
import subprocess


def _terminate_tree(process: subprocess.Popen[str]) -> None:
    """Kill the probe session on POSIX; require taskkill tree cleanup on Windows."""
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        # Windows has no killpg equivalent. Surface failed tree cleanup instead
        # of claiming descendants were stopped after killing just the parent.
        try:
            result = subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                timeout=10,
                check=False,
            )
            if result.returncode:
                raise RuntimeError("Windows import-probe process-tree cleanup failed")
        finally:
            if process.poll() is None:
                process.kill()


def run_import_probe(
    command: list[str],
    *,
    package: str,
    timeout: float,
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    """Append a receipt token, run the probe, and reject incomplete zero exits.

    Probe code must print a JSON object containing ``probe_token`` (its final
    argument), ``package`` and ``status: ok`` only after completing all checks.
    Timeout errors retain captured bytes, matching subprocess.run diagnostics.
    """
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Import timeout must be finite and positive")
    token = secrets.token_hex(24)
    arguments = [*command, token]
    with subprocess.Popen(
        arguments,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=os.name == "posix",
    ) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            _terminate_tree(process)
            stdout, stderr = process.communicate(timeout=10)
            exc.output = stdout.encode()
            exc.stderr = stderr.encode()
            raise
        except BaseException:
            _terminate_tree(process)
            process.wait(timeout=10)
            raise
        result = subprocess.CompletedProcess(
            arguments, process.returncode, stdout, stderr
        )
    result.check_returncode()
    receipts = []
    for line in stdout.splitlines():
        try:
            value = json.loads(line)
        except (ValueError, TypeError):
            continue
        if isinstance(value, dict) and value.get("probe_token") == token:
            receipts.append(value)
    if (
        len(receipts) != 1
        or receipts[0].get("package") != package
        or receipts[0].get("status") != "ok"
    ):
        raise ValueError(f"Import probe for {package} omitted its completion receipt")
    return result
