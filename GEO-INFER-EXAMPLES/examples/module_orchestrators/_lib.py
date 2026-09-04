"""Shared engine for the GEO-INFER module orchestrator examples.

Every module's ``scripts/run_orchestrator.py`` defines one real, documented
end-to-end operation on synthetic data using that module's primary public API
and hands it to :func:`run_module_orchestrator`. The engine executes the
operation, prints structured JSON results on stdout, and maps failures to
deterministic exit codes so shell pipelines and CI can rely on them:

- ``0``: the operation completed and returned a result dict.
- ``2``: the module's dependencies are missing (``ImportError``); the output
  names the exact extra to install (graceful degradation, not a no-op).
- ``1``: the operation itself failed; the output carries the traceback.
"""

from __future__ import annotations

import json
import sys
import time
import traceback
from typing import Any, Callable, Dict

#: Exit code used when a module's dependencies are not installed.
EXIT_DEPENDENCY_MISSING = 2

#: Exit code used when the orchestrated operation raised.
EXIT_OPERATION_FAILED = 1


def run_module_orchestrator(
    module_name: str,
    operation: Callable[[], Dict[str, Any]],
    requires_extra: str = "full",
) -> int:
    """Execute one module operation and report it as structured JSON.

    Args:
        module_name: GEO-INFER module short name (e.g. ``"SPACE"``).
        operation: Zero-argument callable running the module's real
            end-to-end operation on synthetic data. Must return a
            JSON-serializable dict of structured results.
        requires_extra: The ``geo-infer-<module>`` optional-dependencies
            group to install when dependencies are missing.

    Returns:
        The process exit code: ``0`` on success, ``2`` on missing
        dependencies, ``1`` when the operation raised any other error.
    """
    started = time.perf_counter()
    try:
        result = operation()
    except (ImportError, ModuleNotFoundError) as exc:
        payload = {
            "module": module_name,
            "status": "missing-dependency",
            "requires": f"geo-infer-{module_name.lower()}[{requires_extra}]",
            "error": str(exc),
        }
        print(json.dumps(payload, indent=2))
        return EXIT_DEPENDENCY_MISSING
    except Exception as exc:  # noqa: BLE001 - orchestrator boundary
        payload = {
            "module": module_name,
            "status": "error",
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        }
        print(json.dumps(payload, indent=2))
        return EXIT_OPERATION_FAILED

    if not isinstance(result, dict):
        print(
            json.dumps(
                {
                    "module": module_name,
                    "status": "error",
                    "error": (
                        "orchestrator operation must return a dict, got "
                        f"{type(result).__name__}"
                    ),
                },
                indent=2,
            )
        )
        return EXIT_OPERATION_FAILED

    payload = {
        "module": module_name,
        "status": "ok",
        "duration_seconds": round(time.perf_counter() - started, 3),
        "result": result,
    }
    print(json.dumps(payload, indent=2, default=str))
    return 0
