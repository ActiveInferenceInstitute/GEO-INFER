#!/usr/bin/env bash
# GEO-INFER autoresearch benchmark: INTRA maintenance-script conformance gate.
#
# Deterministic workload: fixed path scope (GEO-INFER-INTRA/scripts/), pinned
# ruff (>=0.15.6,<0.16), no live network once the uv cache is warm, no
# time-of-day dependencies. The exit status reports harness health, not gate
# verdict; the drift level is carried exclusively by the METRIC lines.
#
# Primary metric:
#   intra_scripts_drift          files failing `ruff format --check` plus
#                                F821/F823/E721/E722 findings in the scope
#                                (lower is better; 0 = HYG-05 drift closed)
# Secondary metrics:
#   intra_scripts_format_files   format-non-canonical file count
#   intra_scripts_lint_findings  F821/F823/E721/E722 finding count
set -euo pipefail
cd "$(dirname "$0")"

RUFF_SPEC='ruff>=0.15.6,<0.16'
SCOPE=GEO-INFER-INTRA/scripts

# Keep the workspace environment current so `uv run --no-sync` below is
# hermetic and fast; this is a no-op when the environment is already synced.
uv sync --all-packages --all-extras --quiet

format_out="$(uv run --no-sync --with "$RUFF_SPEC" ruff format --check "$SCOPE" 2>&1 || true)"
format_files="$(grep -ic '^would reformat:' <<<"$format_out" || true)"

lint_out="$(uv run --no-sync --with "$RUFF_SPEC" ruff check "$SCOPE" --select F821,F823,E721,E722 --output-format=concise 2>&1 || true)"
lint_findings="$(grep -cE ':[0-9]+:[0-9]+: (F821|F823|E721|E722) ' <<<"$lint_out" || true)"
drift=$((format_files + lint_findings))

echo "METRIC intra_scripts_drift=$drift"
echo "METRIC intra_scripts_format_files=$format_files"
echo "METRIC intra_scripts_lint_findings=$lint_findings"
