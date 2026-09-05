"""Private isolated HTTP worker; stdout contains only bounded response bytes.

Executed as a file with Python ``-I`` so importing this worker does not load the
PLACE package, and caller PYTHONPATH/user-site customizations are ignored.
The worker never starts another process. Its parent owns the wall-clock limit.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import math
import sys
import time
from urllib.parse import urlsplit

import requests

_MAX_BYTES = 20 * 1024 * 1024


def _validate_request(url: str, deadline: float, remaining_bytes: int) -> None:
    if type(remaining_bytes) is not int or not 1 <= remaining_bytes <= _MAX_BYTES:
        raise ValueError(
            "Regional data exceeds 20 MiB budget or has an invalid byte limit"
        )
    try:
        finite_deadline = type(deadline) in (int, float) and math.isfinite(deadline)
    except OverflowError:
        finite_deadline = False
    if not finite_deadline:
        raise ValueError("Download deadline must be finite")
    if not isinstance(url, str):
        raise ValueError("Source URL must be a string")
    parts = urlsplit(url)
    if (
        not parts.hostname
        or parts.username is not None
        or parts.password is not None
        or parts.fragment
    ):
        raise ValueError("Source URL must have a host and no credentials or fragment")
    if parts.port is not None and not 1 <= parts.port <= 65535:
        raise ValueError("Source URL has an invalid port")
    if parts.scheme != "https":
        try:
            loopback = ipaddress.ip_address(parts.hostname).is_loopback
        except ValueError:
            loopback = False
        if parts.scheme != "http" or not loopback:
            raise ValueError(
                "Source requires HTTPS; HTTP is limited to literal loopback addresses"
            )


def _fetch_bytes(url: str, deadline: float, remaining_bytes: int) -> bytes:
    """Stream under a byte cap; cooperative checks supplement parent supervision."""
    _validate_request(url, deadline, remaining_bytes)
    remaining_seconds = deadline - time.monotonic()
    if remaining_seconds <= 0:
        raise TimeoutError("Regional request batch exceeded its cooperative deadline")
    chunks: list[bytes] = []
    total = 0
    with requests.get(
        url,
        stream=True,
        timeout=(min(10, remaining_seconds), min(30, remaining_seconds)),
        allow_redirects=False,
    ) as response:
        if time.monotonic() >= deadline:
            raise TimeoutError(
                "Regional request batch exceeded its cooperative deadline"
            )
        response.raise_for_status()
        if response.is_redirect or 300 <= response.status_code < 400:
            raise ValueError("Unexpected source redirect")
        for chunk in response.iter_content(64 * 1024):
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    "Regional request batch exceeded its cooperative deadline"
                )
            total += len(chunk)
            if total > remaining_bytes:
                raise ValueError("Regional data exceeds 20 MiB budget")
            chunks.append(chunk)
        if time.monotonic() >= deadline:
            raise TimeoutError(
                "Regional request batch exceeded its cooperative deadline"
            )
    return b"".join(chunks)


def _main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("deadline", type=float)
    parser.add_argument("remaining_bytes", type=int)
    args = parser.parse_args()
    try:
        raw = _fetch_bytes(args.url, args.deadline, args.remaining_bytes)
    except (TimeoutError, requests.Timeout):
        error, code = "Source request exceeded its deadline or inactivity timeout", 4
    except ValueError as exc:
        error, code = str(exc), 2
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        error, code = f"Source returned HTTP status {status}", 3
    except requests.RequestException:
        error, code = "Source network request failed", 3
    except Exception as exc:
        error, code = f"Regional worker failed: {type(exc).__name__}", 3
    else:
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return 0
    # No response body, proxy configuration, or credentials enter error output.
    sys.stderr.write(json.dumps({"error": error[:512]}) + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(_main())
