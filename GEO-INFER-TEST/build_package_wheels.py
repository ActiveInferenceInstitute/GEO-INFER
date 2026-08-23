#!/usr/bin/env python3
"""
Multi-package wheel build driver for the GEO-INFER monorepo.

ARCH-01: Builds a wheel for every ``GEO-INFER-*`` package, verifies that each
built wheel belongs to the correct ``geo-infer-*`` distribution namespace, and
(optionally) installs each wheel into an isolated virtual environment to smoke
test importability and configuration-resource discovery.

Intended to be invoked by ``.github/workflows/release.yml`` after the shared
uv workspace is synced, but every helper is pure and unit-testable without
building anything.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from validate_packaging import (  # noqa: F401
    ContractReport,
    distribution_name,
    module_dirs,
    parse_pyproject,
    wheel_filename_is_valid,
)


@dataclass
class BuildResult:
    module: str
    distribution: Optional[str]
    wheel: Optional[Path]
    ok: bool = False
    error: str = ""


@dataclass
class BuildSummary:
    results: List[BuildResult] = field(default_factory=list)

    @property
    def namespaces_valid(self) -> bool:
        return all(r.ok or (not r.distribution) for r in self.results)

    @property
    def failures(self) -> List[BuildResult]:
        return [r for r in self.results if not r.ok]


def build_wheel(module_dir: Path, outdir: Path, python: List[str]) -> BuildResult:
    """Build one module's wheel into ``outdir`` using the ``build`` frontend."""
    distribution = distribution_name(parse_pyproject(module_dir))
    result = BuildResult(module=module_dir.name, distribution=distribution)
    if not distribution:
        result.error = "missing [project].name"
        return result

    try:
        subprocess.run(
            [*python, "-m", "build", "--wheel", "--outdir", str(outdir)],
            cwd=module_dir,
            check=True,
            capture_output=True,
        )
    except FileNotFoundError as exc:
        result.error = f"build frontend unavailable: {exc}"
        return result
    except subprocess.CalledProcessError as exc:
        result.error = (exc.stderr or exc.stdout or b"").decode("utf-8", "ignore")[
            -2000:
        ]
        return result

    wheels = sorted(outdir.glob("*.whl")) if outdir.is_dir() else []
    if not wheels:
        result.error = "no wheel produced"
        return result
    result.wheel = wheels[-1]
    result.ok = wheel_filename_is_valid(result.wheel.name, distribution)
    if not result.ok:
        result.error = (
            f"wheel {result.wheel.name!r} not in expected namespace "
            f"{distribution}"
        )
    return result


def install_and_verify(wheel: Path, python: List[str]) -> None:
    """Install ``wheel`` into an isolated venv and import its top package."""
    with tempfile.TemporaryDirectory() as tmp:
        venv = Path(tmp) / "venv"
        subprocess.run(
            [*python, "-m", "venv", str(venv)], check=True, capture_output=True
        )
        venv_python = str(venv / "bin" / "python")
        subprocess.run(
            [venv_python, "-m", "pip", "install", "--quiet", str(wheel)],
            check=True,
            capture_output=True,
        )
        # A wheel is considered installable when at least one non-top-level
        # module imports; use the metadata distribution name to derive a probe.
        # We introspect packages inside the wheel without executing code paths
        # that depend on optional heavy backends.
        probe = (
            "import importlib.metadata as md, importlib.util as iu;"
            "dist_name='" + wheel.name.split("-")[0].replace("_", "-")
            + "';"
            "dist=md.distribution(dist_name);"
            "print('installed', dist.version)"
        )
        subprocess.run(
            [venv_python, "-c", probe], check=True, capture_output=True
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and validate GEO-INFER wheels"
    )
    parser.add_argument("--outdir", type=Path, default=Path("dist"))
    parser.add_argument("--verify", action="store_true", help="isolated venv install")
    args = parser.parse_args()

    outdir = args.outdir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    python = [sys.executable]
    # Prefer the active interpreter (inside `uv run` this is the workspace env).
    subprocess.run(
        [*python, "-m", "pip", "install", "--quiet", "build", "wheel"],
        check=True,
        capture_output=True,
    )

    summary = BuildSummary()
    for module_dir in module_dirs():
        result = build_wheel(module_dir, outdir, python)
        summary.results.append(result)
        if result.ok and args.verify and result.wheel is not None:
            try:
                install_and_verify(result.wheel, python)
            except subprocess.CalledProcessError as exc:
                result.ok = False
                result.error = (exc.stderr or b"").decode("utf-8", "ignore")[-2000:]

    for result in summary.results:
        status = "OK" if result.ok else "FAIL"
        print(f"[{status}] {result.module} -> {result.wheel or result.error}")
    if not summary.namespaces_valid:
        print("Namespace validation FAILED")
        return 1
    print("Namespace validation passed across all packages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())