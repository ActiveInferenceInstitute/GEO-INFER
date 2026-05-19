"""Shared helper for legacy script wrappers."""

from __future__ import annotations

import json
import sys
from typing import Iterable, Optional

from geo_infer_act.runners.cli import build_parser, config_from_args
from geo_infer_act.runners.scenarios import run_all_scenarios, run_scenario


def run_wrapper(
    default_scenario: str,
    argv: Optional[Iterable[str]] = None,
    program: Optional[str] = None,
) -> int:
    """Run a legacy wrapper with a package-owned scenario implementation."""
    args_list = list(argv) if argv is not None else sys.argv[1:]
    parser = build_parser(default_all=default_scenario == "all")
    parser.set_defaults(scenario=default_scenario)
    args = parser.parse_args(args_list)
    config = config_from_args(args)
    if "--scenario" not in args_list:
        config.scenario = default_scenario
    command = [program or "geo-infer-act-run", *args_list]

    if config.scenario == "all":
        result = run_all_scenarios(
            output_dir=config.output_dir,
            scenarios=["simple", "spatial"] if args.quick else None,
            seed=config.seed,
            timesteps=config.timesteps,
            deterministic=config.deterministic,
            visualizations=config.visualizations,
            command=command,
        )
        manifest_path = result.manifest_path
    else:
        result = run_scenario(config, command=command)
        manifest_path = result.manifest_path

    payload = {"manifest": str(manifest_path)}
    print(json.dumps(payload) if args.json else f"Manifest: {manifest_path}")
    return 0
