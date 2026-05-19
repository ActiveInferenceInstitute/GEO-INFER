"""Canonical Active Inference scenario runners."""

from __future__ import annotations

import math
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

import matplotlib
import numpy as np
import yaml

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from geo_infer_act.core.active_inference import ActiveInferenceModel
from geo_infer_act.core.generative_model import GenerativeModel
from geo_infer_act.core.spatial_agent import SpatialActiveInferenceAgent
from geo_infer_act.runners.contracts import (
    RunConfig,
    ScenarioRunResult,
    SuiteRunResult,
    normalize_scenario_list,
)
from geo_infer_act.runners.h3 import (
    generate_realistic_environmental_observations,
    h3_cells_for_config,
    observation_dict_to_vector,
)
from geo_infer_act.runners.io import (
    ensure_output_tree,
    save_matplotlib_figure_artifact,
    write_csv,
    write_html_figure_artifact,
    write_json,
    write_run_manifest,
    write_suite_manifest,
)
from geo_infer_act.utils.analysis import ActiveInferenceAnalyzer
from geo_infer_act.utils.h3_adapter import get_h3_adapter, normalize_belief_vector


SCENARIO_PARAMETERS: Dict[str, Dict[str, Any]] = {
    "simple": {"phase": 0.0, "amplitude": 0.18, "preference": [0.1, 0.2, 0.3, 0.4]},
    "modern": {"phase": 0.6, "amplitude": 0.24, "preference": [0.2, 0.1, 0.4, 0.3]},
    "spatial": {
        "phase": 1.1,
        "amplitude": 0.22,
        "preference": [0.15, 0.25, 0.35, 0.25],
    },
    "ecological": {
        "phase": 1.7,
        "amplitude": 0.2,
        "preference": [0.05, 0.15, 0.35, 0.45],
    },
    "urban_planning": {
        "phase": 2.2,
        "amplitude": 0.16,
        "preference": [0.2, 0.35, 0.25, 0.2],
    },
    "verification": {
        "phase": 2.8,
        "amplitude": 0.12,
        "preference": [0.25, 0.25, 0.25, 0.25],
    },
    "debug": {"phase": 3.3, "amplitude": 0.1, "preference": [0.4, 0.3, 0.2, 0.1]},
}


def load_run_config(
    path: Optional[Path] = None,
    overrides: Optional[Mapping[str, Any]] = None,
) -> RunConfig:
    """Load a versioned YAML run config and apply explicit overrides."""
    data: Dict[str, Any] = {}
    if path is not None:
        with Path(path).open() as handle:
            loaded = yaml.safe_load(handle) or {}
        if not isinstance(loaded, dict):
            raise ValueError(f"Run config must be a mapping: {path}")
        data.update(loaded)
    if overrides:
        data.update(
            {key: value for key, value in overrides.items() if value is not None}
        )
    return RunConfig(**data)


def run_scenario(
    config: RunConfig, command: Optional[List[str]] = None
) -> ScenarioRunResult:
    """Run one canonical Active Inference scenario."""
    config = RunConfig(**config.__dict__)
    output_dir = ensure_output_tree(
        config.output_dir or _default_output_dir(config.scenario)
    )
    config.output_dir = output_dir

    if config.scenario == "h3":
        metrics = _run_h3_scenario(config)
    elif config.scenario == "spatial":
        metrics = _run_spatial_scenario(config)
    else:
        metrics = _run_vector_scenario(config)

    manifest = write_run_manifest(output_dir, config, metrics, command=command)
    generated_files = [
        output_dir / item["path"] for item in manifest["generated_files"]
    ]
    return ScenarioRunResult(
        scenario=config.scenario,
        output_dir=output_dir,
        manifest_path=output_dir / "manifest.json",
        manifest=manifest,
        metrics=metrics,
        generated_files=generated_files,
    )


def run_all_scenarios(
    output_dir: Optional[Path] = None,
    scenarios: Optional[Iterable[str]] = None,
    seed: int = 42,
    timesteps: int = 8,
    deterministic: bool = True,
    visualizations: bool = True,
    command: Optional[List[str]] = None,
) -> SuiteRunResult:
    """Run a suite of scenarios and write a suite manifest."""
    output_dir = ensure_output_tree(output_dir or _default_output_dir("examples"))
    selected = normalize_scenario_list(scenarios)
    results = []
    for scenario in selected:
        scenario_config = RunConfig(
            scenario=scenario,
            output_dir=output_dir / scenario,
            seed=seed,
            timesteps=timesteps,
            deterministic=deterministic,
            visualizations=visualizations,
        )
        results.append(run_scenario(scenario_config, command=command))

    manifest = write_suite_manifest(output_dir, results, command=command)
    return SuiteRunResult(
        output_dir=output_dir,
        manifest_path=output_dir / "suite_manifest.json",
        manifest=manifest,
        scenario_results=results,
    )


def _default_output_dir(scenario: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path.cwd() / "output" / f"act_{scenario}_{timestamp}"


def _run_vector_scenario(config: RunConfig) -> Dict[str, Any]:
    params = {**SCENARIO_PARAMETERS[config.scenario], **config.parameters}
    rng = np.random.default_rng(config.seed)
    analyzer = ActiveInferenceAnalyzer(str(config.output_dir))
    model = GenerativeModel(
        "categorical",
        {
            "state_dim": 4,
            "obs_dim": 4,
            "prior_precision": 1.0,
        },
    )
    active_model = ActiveInferenceModel(
        "categorical",
        preferences=list(np.asarray(params["preference"], dtype=float)),
        policy_selection_mode="deterministic" if config.deterministic else "sample",
        random_seed=config.seed,
    )
    active_model.set_generative_model(model)

    step_rows: List[Dict[str, Any]] = []
    actions = ["observe", "adapt", "coordinate", "conserve"]
    for timestep in range(config.timesteps):
        observation = _scenario_observation(config.scenario, timestep, params, rng)
        result = active_model.step(observation, actions, return_result=True)
        beliefs = _belief_vector(result.beliefs)
        entropy = float(-np.sum(beliefs * np.log(beliefs + 1e-12)))
        row = {
            "timestep": timestep,
            "scenario": config.scenario,
            "action": str(result.action),
            "free_energy": float(result.free_energy),
            "expected_free_energy": (
                float(result.expected_free_energy)
                if result.expected_free_energy is not None
                else None
            ),
            "belief_entropy": entropy,
        }
        row.update({f"belief_{idx}": float(value) for idx, value in enumerate(beliefs)})
        step_rows.append(row)
        analyzer.record_step(
            beliefs=beliefs,
            observations=observation,
            actions=result.action,
            policies={
                "selected": result.action,
                "expected_free_energy": result.expected_free_energy,
            },
            free_energy=float(result.free_energy),
            metrics=row,
            timestamp=float(timestep),
        )

    _finalize_analyzer(analyzer)
    write_csv(config.output_dir / "data" / "step_metrics.csv", step_rows)
    summary = _summary_metrics(step_rows)
    write_json(config.output_dir / "analysis" / "run_summary.json", summary)
    if config.visualizations:
        _plot_vector_summary(config, step_rows)
    return summary


def _run_h3_scenario(config: RunConfig) -> Dict[str, Any]:
    """Run H3 grid inference with full geospatial data and visualization outputs."""
    cells = h3_cells_for_config(
        resolution=config.h3_resolution,
        ring_size=config.h3_ring_size,
        cells=config.h3_cells,
    )
    model = GenerativeModel(
        "categorical",
        {"state_dim": 4, "obs_dim": 4, "spatial_mode": True},
    )
    model.spatial_mode = True
    model.h3_cells = cells
    model.spatial_graph = model._build_h3_neighbor_graph(cells)
    active_model = ActiveInferenceModel(
        "categorical",
        policy_selection_mode="deterministic" if config.deterministic else "sample",
        random_seed=config.seed,
    )
    active_model.set_generative_model(model)
    analyzer = ActiveInferenceAnalyzer(str(config.output_dir))

    step_rows: List[Dict[str, Any]] = []
    diagnostics: List[Dict[str, Any]] = []
    last_cell_results: Dict[str, Any] = {}
    for timestep in range(config.timesteps):
        env_obs = generate_realistic_environmental_observations(
            cells,
            timestep=float(timestep),
            spatial_seed=config.seed,
        )
        vector_obs = {
            cell: observation_dict_to_vector(obs) for cell, obs in env_obs.items()
        }
        belief_update = model.update_h3_beliefs(vector_obs, return_result=True)
        grid_result = active_model.infer_over_h3_grid(vector_obs, return_result=True)
        coherence = belief_update.spatial_consistency.global_coherence
        neighbor_corr = belief_update.spatial_consistency.neighbor_correlations
        row = {
            "timestep": timestep,
            "scenario": "h3",
            "free_energy": float(grid_result.aggregate_free_energy),
            "expected_free_energy": float(
                np.nanmean(
                    [
                        result.expected_free_energy
                        for result in grid_result.cell_results.values()
                        if result.expected_free_energy is not None
                    ]
                    or [0.0]
                )
            ),
            "cell_count": len(cells),
            "edge_count": belief_update.spatial_consistency.edge_count,
            "coherence": float(coherence),
            "neighbor_correlation": float(neighbor_corr),
            "belief_entropy": _average_belief_entropy(
                [result.beliefs for result in grid_result.cell_results.values()]
            ),
        }
        step_rows.append(row)
        diagnostics.append(
            {
                "scenario": "h3",
                "timestep": timestep,
                "spatial_consistency": belief_update.spatial_consistency,
                "aggregate_free_energy": grid_result.aggregate_free_energy,
                "h3_resolution": config.h3_resolution,
            }
        )
        last_cell_results = grid_result.cell_results
        analyzer.record_step(
            beliefs=belief_update.average,
            observations=np.mean(list(vector_obs.values()), axis=0),
            actions="h3_grid_inference",
            policies={
                "selected": "h3_grid_inference",
                "expected_free_energy": row["expected_free_energy"],
            },
            free_energy=row["free_energy"],
            metrics=row,
            timestamp=float(timestep),
        )

    _finalize_analyzer(analyzer)
    write_csv(config.output_dir / "data" / "step_metrics.csv", step_rows)
    cell_metrics = _cell_metrics_from_results(cells, last_cell_results)
    _write_geospatial_cell_outputs(config, cells, cell_metrics)
    write_json(config.output_dir / "data" / "h3_diagnostics.json", diagnostics)
    summary = _summary_metrics(step_rows)
    summary.update(
        {
            "cell_count": len(cells),
            "edge_count": step_rows[-1]["edge_count"],
            "coherence": step_rows[-1]["coherence"],
            "neighbor_correlation": step_rows[-1]["neighbor_correlation"],
            "mean_belief_entropy": float(
                np.mean([row["belief_entropy"] for row in step_rows])
            ),
        }
    )
    write_json(config.output_dir / "analysis" / "run_summary.json", summary)
    if config.visualizations:
        _write_geospatial_visualizations(config, step_rows, cell_metrics)
    return summary


def _run_spatial_scenario(config: RunConfig) -> Dict[str, Any]:
    """Run SpatialActiveInferenceAgent on real H3 cells with geospatial outputs."""
    cells = h3_cells_for_config(
        resolution=config.h3_resolution,
        ring_size=config.h3_ring_size,
        cells=config.h3_cells,
    )
    agent = SpatialActiveInferenceAgent(
        h3_resolution=config.h3_resolution,
        initial_cells=cells,
        state_dim=4,
        obs_dim=4,
        diffusion_rate=float(config.parameters.get("diffusion_rate", 0.15)),
        enable_logging=False,
    )
    analyzer = ActiveInferenceAnalyzer(str(config.output_dir))

    step_rows: List[Dict[str, Any]] = []
    diagnostics: List[Dict[str, Any]] = []
    last_cell_results: Dict[str, Any] = {}
    for timestep in range(config.timesteps):
        env_obs = generate_realistic_environmental_observations(
            cells,
            timestep=float(timestep),
            spatial_seed=config.seed,
        )
        vector_obs = {
            cell: observation_dict_to_vector(obs) for cell, obs in env_obs.items()
        }
        grid_result = agent.step(vector_obs, return_result=True)
        expected_free_energy = float(
            np.nanmean(
                [
                    result.expected_free_energy
                    for result in grid_result.cell_results.values()
                    if result.expected_free_energy is not None
                ]
                or [0.0]
            )
        )
        row = {
            "timestep": timestep,
            "scenario": "spatial",
            "free_energy": float(grid_result.aggregate_free_energy),
            "expected_free_energy": expected_free_energy,
            "cell_count": len(cells),
            "edge_count": grid_result.spatial_consistency.edge_count,
            "coherence": float(grid_result.spatial_consistency.global_coherence),
            "neighbor_correlation": float(
                grid_result.spatial_consistency.neighbor_correlations
            ),
            "belief_entropy": _average_belief_entropy(
                [result.beliefs for result in grid_result.cell_results.values()]
            ),
        }
        step_rows.append(row)
        diagnostics.append(
            {
                "scenario": "spatial",
                "timestep": timestep,
                "spatial_consistency": grid_result.spatial_consistency,
                "aggregate_free_energy": grid_result.aggregate_free_energy,
                "h3_resolution": config.h3_resolution,
            }
        )
        last_cell_results = grid_result.cell_results
        analyzer.record_step(
            beliefs=np.mean(agent.beliefs, axis=0),
            observations=np.mean(list(vector_obs.values()), axis=0),
            actions=grid_result.metadata.get("selected_action", {}),
            policies={
                "selected": grid_result.metadata.get("selected_action", {}),
                "expected_free_energy": expected_free_energy,
            },
            free_energy=row["free_energy"],
            metrics=row,
            timestamp=float(timestep),
        )

    _finalize_analyzer(analyzer)
    write_csv(config.output_dir / "data" / "step_metrics.csv", step_rows)
    cell_metrics = _cell_metrics_from_results(cells, last_cell_results)
    _write_geospatial_cell_outputs(config, cells, cell_metrics)
    write_json(config.output_dir / "data" / "h3_diagnostics.json", diagnostics)
    summary = _summary_metrics(step_rows)
    summary.update(
        {
            "cell_count": len(cells),
            "edge_count": step_rows[-1]["edge_count"],
            "coherence": step_rows[-1]["coherence"],
            "neighbor_correlation": step_rows[-1]["neighbor_correlation"],
            "mean_belief_entropy": float(
                np.mean([row["belief_entropy"] for row in step_rows])
            ),
        }
    )
    write_json(config.output_dir / "analysis" / "run_summary.json", summary)
    if config.visualizations:
        _write_geospatial_visualizations(config, step_rows, cell_metrics)
    return summary


def _scenario_observation(
    scenario: str,
    timestep: int,
    params: Mapping[str, Any],
    rng: np.random.Generator,
) -> np.ndarray:
    phase = float(params["phase"])
    amplitude = float(params["amplitude"])
    base = np.asarray(params.get("preference", [0.25, 0.25, 0.25, 0.25]), dtype=float)
    seasonal = np.array(
        [
            math.sin(timestep + phase),
            math.cos((timestep * 0.7) + phase),
            math.sin((timestep * 0.4) + phase + 0.8),
            math.cos((timestep * 0.3) + phase + 1.2),
        ]
    )
    signal = base + amplitude * seasonal
    if scenario in {"verification", "debug"}:
        signal += rng.normal(0.0, 0.005, size=4)
    return normalize_belief_vector(signal)


def _belief_vector(beliefs: Any) -> np.ndarray:
    if isinstance(beliefs, dict) and "states" in beliefs:
        return normalize_belief_vector(beliefs["states"])
    return normalize_belief_vector(beliefs)


def _finalize_analyzer(analyzer: ActiveInferenceAnalyzer) -> None:
    analyzer.export_full_history()
    analyzer.save_traces_to_csv()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            analyzer.analyze_perception_patterns()
            analyzer.analyze_action_selection_patterns()
            analyzer.analyze_free_energy_patterns()
            analyzer.generate_comprehensive_report()
    except Exception as exc:
        write_json(
            analyzer.output_dir / "analysis" / "analysis_warning.json",
            {"warning": str(exc)},
        )


def _summary_metrics(rows: List[Mapping[str, Any]]) -> Dict[str, Any]:
    free_energy = [float(row["free_energy"]) for row in rows]
    expected = [
        float(row["expected_free_energy"])
        for row in rows
        if row.get("expected_free_energy") is not None
    ]
    return {
        "timesteps": len(rows),
        "initial_free_energy": free_energy[0],
        "final_free_energy": free_energy[-1],
        "free_energy_change": free_energy[-1] - free_energy[0],
        "mean_free_energy": float(np.mean(free_energy)),
        "mean_expected_free_energy": float(np.mean(expected)) if expected else 0.0,
        "finite_metrics": bool(np.all(np.isfinite(free_energy))),
    }


def _provenance_caption(config: RunConfig, metric_note: str) -> str:
    """Return compact provenance text for runner visualizations."""
    h3_part = ""
    if config.scenario in {"h3", "spatial"}:
        h3_part = f" | H3 r{config.h3_resolution}, ring {config.h3_ring_size}"
    return (
        f"Scenario: {config.scenario} | seed: {config.seed} | "
        f"timesteps: {config.timesteps}{h3_part} | {metric_note}"
    )


def _add_provenance_caption(
    fig: Any, config: RunConfig, metric_note: str, y: float = 0.005
) -> None:
    """Add visible run provenance to a figure without changing data semantics."""
    fig.text(
        0.01,
        y,
        _provenance_caption(config, metric_note),
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4a4a4a",
    )


def _average_belief_entropy(beliefs: List[Any]) -> float:
    """Compute mean entropy for a collection of belief vectors."""
    if not beliefs:
        return 0.0
    entropies = []
    for belief in beliefs:
        vector = _belief_vector(belief)
        entropies.append(float(-np.sum(vector * np.log(vector + 1e-12))))
    return float(np.mean(entropies))


def _cell_metrics_from_results(
    cells: List[str], cell_results: Mapping[str, Any]
) -> List[Dict[str, Any]]:
    """Build per-cell metric rows from typed grid inference results."""
    adapter = get_h3_adapter()
    metrics = []
    for cell in cells:
        lat, lng = adapter.cell_to_latlng(cell)
        result = cell_results.get(cell)
        belief = (
            _belief_vector(result.beliefs) if result is not None else np.ones(4) / 4
        )
        metrics.append(
            {
                "cell": cell,
                "lat": float(lat),
                "lng": float(lng),
                "resolution": adapter.get_resolution(cell),
                "free_energy": float(result.free_energy) if result is not None else 0.0,
                "expected_free_energy": (
                    float(result.expected_free_energy)
                    if result is not None and result.expected_free_energy is not None
                    else 0.0
                ),
                "belief_entropy": float(-np.sum(belief * np.log(belief + 1e-12))),
                "action": str(result.action) if result is not None else "",
                "beliefs": belief.tolist(),
            }
        )
    return metrics


def _write_geospatial_cell_outputs(
    config: RunConfig, cells: List[str], cell_metrics: List[Dict[str, Any]]
) -> None:
    """Write H3 cell CSV and polygon GeoJSON outputs for geospatial scenarios."""
    adapter = get_h3_adapter()
    write_csv(config.output_dir / "data" / "h3_cells.csv", cell_metrics)
    features = []
    metrics_by_cell = {row["cell"]: row for row in cell_metrics}
    for cell in cells:
        boundary = adapter.cell_to_boundary(cell)
        ring = [[float(lng), float(lat)] for lat, lng in boundary]
        if ring and ring[0] != ring[-1]:
            ring.append(ring[0])
        row = metrics_by_cell[cell]
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [ring]},
                "properties": {
                    "h3_cell": cell,
                    "resolution": row["resolution"],
                    "lat": row["lat"],
                    "lng": row["lng"],
                    "free_energy": row["free_energy"],
                    "expected_free_energy": row["expected_free_energy"],
                    "belief_entropy": row["belief_entropy"],
                    "action": row["action"],
                },
            }
        )
    write_json(
        config.output_dir / "data" / "h3_cells.geojson",
        {"type": "FeatureCollection", "features": features},
    )


def _plot_vector_summary(config: RunConfig, rows: List[Mapping[str, Any]]) -> Path:
    """Create the standard non-geospatial scenario summary visualization."""
    timesteps = [int(row["timestep"]) for row in rows]
    free_energy = [float(row["free_energy"]) for row in rows]
    entropy = [float(row["belief_entropy"]) for row in rows]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4))
    axes[0].plot(timesteps, free_energy, marker="o")
    axes[0].set_title("Variational Free Energy")
    axes[0].set_xlabel("Timestep")
    axes[0].set_ylabel("Free-energy value")
    axes[0].grid(True, alpha=0.25)
    axes[1].plot(timesteps, entropy, marker="s", color="#2c7fb8")
    axes[1].set_title("Belief Entropy")
    axes[1].set_xlabel("Timestep")
    axes[1].set_ylabel("Entropy (nats)")
    axes[1].grid(True, alpha=0.25)
    fig.suptitle(f"Active Inference Scenario: {config.scenario}")
    _add_provenance_caption(
        fig, config, "Data: data/step_metrics.csv and data/full_history.json"
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    path = save_matplotlib_figure_artifact(
        config,
        fig,
        "visualizations/scenario_summary.png",
        title=f"Active Inference Scenario: {config.scenario}",
        description="Summary plot of variational free energy and belief entropy over timesteps.",
        alt_text=(
            f"Two-panel {config.scenario} Active Inference plot showing "
            "free-energy values and belief entropy by timestep."
        ),
        plotted_metrics=["free_energy", "belief_entropy"],
        data_sources=["data/step_metrics.csv", "data/full_history.json"],
        plotted_data=[
            {
                "timestep": int(row["timestep"]),
                "free_energy": float(row["free_energy"]),
                "belief_entropy": float(row["belief_entropy"]),
            }
            for row in rows
        ],
    )
    plt.close(fig)
    return path


def _plot_h3_summary(
    config: RunConfig,
    rows: List[Mapping[str, Any]],
    cell_results: Mapping[str, Any],
) -> Path:
    """Create the legacy two-panel H3 summary visualization."""
    adapter = get_h3_adapter()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    axes[0].plot(
        [int(row["timestep"]) for row in rows],
        [float(row["free_energy"]) for row in rows],
        marker="o",
    )
    axes[0].set_title("H3 Aggregate Free Energy")
    axes[0].set_xlabel("Timestep")
    axes[0].set_ylabel("Free-energy value")
    axes[0].grid(True, alpha=0.25)
    cells = list(cell_results)
    lats = []
    lngs = []
    values = []
    for cell in cells:
        lat, lng = adapter.cell_to_latlng(cell)
        lats.append(lat)
        lngs.append(lng)
        values.append(float(cell_results[cell].free_energy))
    scatter = axes[1].scatter(lngs, lats, c=values, cmap="viridis", s=90)
    axes[1].set_title("Cell Free Energy")
    axes[1].set_xlabel("Longitude (degrees)")
    axes[1].set_ylabel("Latitude (degrees)")
    fig.colorbar(scatter, ax=axes[1], label="Free-energy value")
    fig.suptitle("H3 Active Inference")
    _add_provenance_caption(
        fig, config, "Data: data/step_metrics.csv and H3 cell diagnostics"
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    plotted_data = [
        {
            "record_type": "timeline",
            "timestep": int(row["timestep"]),
            "free_energy": float(row["free_energy"]),
        }
        for row in rows
    ]
    plotted_data.extend(
        {
            "record_type": "cell",
            "h3_cell": cell,
            "lat": float(lat),
            "lng": float(lng),
            "free_energy": float(value),
        }
        for cell, lat, lng, value in zip(cells, lats, lngs, values)
    )
    path = save_matplotlib_figure_artifact(
        config,
        fig,
        "visualizations/h3_grid_summary.png",
        title="H3 Active Inference Summary",
        description="Legacy summary combining H3 aggregate free energy and final per-cell free energy.",
        alt_text="Two-panel H3 Active Inference summary with free-energy time series and cell map.",
        plotted_metrics=["free_energy"],
        data_sources=["data/step_metrics.csv", "data/h3_cells.csv"],
        plotted_data=plotted_data,
    )
    plt.close(fig)
    return path


def _write_geospatial_visualizations(
    config: RunConfig, rows: List[Mapping[str, Any]], cell_metrics: List[Dict[str, Any]]
) -> None:
    """Create the full visualization set required for geospatial scenarios."""
    _plot_h3_cell_metric_map(config, cell_metrics)
    _plot_free_energy_evolution(config, rows)
    _plot_belief_entropy_coherence(config, rows)
    _write_interactive_h3_map(config, cell_metrics)


def _plot_h3_cell_metric_map(
    config: RunConfig, cell_metrics: List[Dict[str, Any]]
) -> Path:
    """Plot H3 cell centroids colored by final free-energy metric."""
    scenario_label = (
        "H3" if config.scenario == "h3" else f"{config.scenario.title()} H3"
    )
    fig, ax = plt.subplots(figsize=(7, 6.4))
    lngs = [row["lng"] for row in cell_metrics]
    lats = [row["lat"] for row in cell_metrics]
    values = [row["free_energy"] for row in cell_metrics]
    scatter = ax.scatter(lngs, lats, c=values, cmap="viridis", s=150, edgecolor="k")
    ax.set_title(f"{scenario_label} Cell Free Energy")
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.grid(True, alpha=0.2)
    fig.colorbar(scatter, ax=ax, label="Final free-energy value")
    _add_provenance_caption(
        fig, config, "Data: data/h3_cells.csv and data/h3_cells.geojson"
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    path = save_matplotlib_figure_artifact(
        config,
        fig,
        "visualizations/h3_cell_metric_map.png",
        title=f"{scenario_label} Cell Free Energy",
        description="Static H3 cell centroid map colored by final variational free energy.",
        alt_text=(
            f"{config.scenario} H3 map with one point per H3 cell, colored by "
            "final free-energy value."
        ),
        plotted_metrics=["free_energy", "lat", "lng"],
        data_sources=["data/h3_cells.csv", "data/h3_cells.geojson"],
        plotted_data=cell_metrics,
    )
    plt.close(fig)
    return path


def _plot_free_energy_evolution(
    config: RunConfig, rows: List[Mapping[str, Any]]
) -> Path:
    """Plot aggregate free-energy and expected-free-energy trajectories."""
    fig, ax = plt.subplots(figsize=(8, 4.4))
    timesteps = [int(row["timestep"]) for row in rows]
    ax.plot(timesteps, [float(row["free_energy"]) for row in rows], marker="o")
    ax.plot(
        timesteps,
        [float(row["expected_free_energy"]) for row in rows],
        marker="s",
        linestyle="--",
    )
    ax.set_title(f"{config.scenario.upper()} Free Energy Evolution")
    ax.set_xlabel("Timestep")
    ax.set_ylabel("Energy value")
    ax.legend(["Free energy", "Expected free energy"])
    ax.grid(True, alpha=0.25)
    _add_provenance_caption(
        fig, config, "Data: data/step_metrics.csv; FE and EFE are aggregate metrics"
    )
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    plotted_data = [
        {
            "timestep": int(row["timestep"]),
            "free_energy": float(row["free_energy"]),
            "expected_free_energy": float(row["expected_free_energy"]),
        }
        for row in rows
    ]
    path = save_matplotlib_figure_artifact(
        config,
        fig,
        "visualizations/free_energy_evolution.png",
        title=f"{config.scenario.upper()} Free Energy Evolution",
        description="Line plot comparing aggregate variational free energy and expected free energy across timesteps.",
        alt_text=(
            f"{config.scenario} line chart with free energy and expected free "
            "energy values across timesteps."
        ),
        plotted_metrics=["free_energy", "expected_free_energy"],
        data_sources=["data/step_metrics.csv", "data/full_history.json"],
        plotted_data=plotted_data,
    )
    plt.close(fig)
    return path


def _plot_belief_entropy_coherence(
    config: RunConfig, rows: List[Mapping[str, Any]]
) -> Path:
    """Plot belief entropy and spatial coherence diagnostics over time."""
    fig, ax1 = plt.subplots(figsize=(8, 4.4))
    timesteps = [int(row["timestep"]) for row in rows]
    ax1.plot(
        timesteps,
        [float(row["belief_entropy"]) for row in rows],
        marker="o",
        color="#2c7fb8",
    )
    ax1.set_xlabel("Timestep")
    ax1.set_ylabel("Belief entropy (nats)", color="#2c7fb8")
    ax1.grid(True, alpha=0.25)
    ax2 = ax1.twinx()
    ax2.plot(
        timesteps,
        [float(row["coherence"]) for row in rows],
        marker="s",
        color="#d95f0e",
    )
    ax2.set_ylabel("Spatial coherence", color="#d95f0e")
    ax1.set_title(f"{config.scenario.upper()} Entropy and Coherence")
    _add_provenance_caption(
        fig,
        config,
        "Data: data/step_metrics.csv; entropy from normalized beliefs, coherence from H3 neighbors",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    plotted_data = [
        {
            "timestep": int(row["timestep"]),
            "belief_entropy": float(row["belief_entropy"]),
            "coherence": float(row["coherence"]),
            "neighbor_correlation": float(row["neighbor_correlation"]),
        }
        for row in rows
    ]
    path = save_matplotlib_figure_artifact(
        config,
        fig,
        "visualizations/belief_entropy_coherence.png",
        title=f"{config.scenario.upper()} Entropy and Spatial Coherence",
        description="Dual-axis plot of mean belief entropy and spatial coherence across timesteps.",
        alt_text=(
            f"{config.scenario} chart with belief entropy on the left axis and "
            "spatial coherence on the right axis across timesteps."
        ),
        plotted_metrics=["belief_entropy", "coherence", "neighbor_correlation"],
        data_sources=["data/step_metrics.csv", "data/h3_diagnostics.json"],
        plotted_data=plotted_data,
    )
    plt.close(fig)
    return path


def _write_interactive_h3_map(
    config: RunConfig, cell_metrics: List[Dict[str, Any]]
) -> Path:
    """Write an interactive HTML cell map, using Plotly when available."""
    title = f"{config.scenario.upper()} H3 Active Inference Map"
    description = (
        "Interactive H3 cell map with final free energy, expected free energy, "
        "belief entropy, and selected action hover diagnostics."
    )
    alt_text = (
        f"Interactive {config.scenario} H3 map with each cell plotted by "
        "latitude and longitude and colored by free-energy value."
    )
    try:
        import plotly.express as px  # noqa: PLC0415

        fig = px.scatter_geo(
            cell_metrics,
            lat="lat",
            lon="lng",
            color="free_energy",
            hover_name="cell",
            hover_data=["expected_free_energy", "belief_entropy", "action"],
            height=520,
            title=title,
        )
        fig.update_geos(fitbounds="locations", visible=True)
        fig.update_layout(
            margin={"r": 0, "t": 70, "l": 0, "b": 35},
            annotations=[
                {
                    "text": _provenance_caption(
                        config,
                        "Data: data/h3_cells.csv and data/h3_cells.geojson",
                    ),
                    "showarrow": False,
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0,
                    "y": -0.08,
                    "xanchor": "left",
                    "font": {"size": 11, "color": "#4a4a4a"},
                }
            ],
        )
        html = fig.to_html(include_plotlyjs="cdn", full_html=True)
    except Exception:
        rows = "\n".join(
            "<tr>"
            f"<td>{row['cell']}</td><td>{row['lat']:.6f}</td><td>{row['lng']:.6f}</td>"
            f"<td>{row['free_energy']:.6f}</td><td>{row['belief_entropy']:.6f}</td>"
            "</tr>"
            for row in cell_metrics
        )
        html = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>{config.scenario} H3 map</title></head><body>"
            f"<h1>{config.scenario.upper()} H3 Active Inference Map</h1>"
            f"<p>{_provenance_caption(config, 'Data: data/h3_cells.csv and data/h3_cells.geojson')}</p>"
            "<table><thead><tr><th>Cell</th><th>Lat</th><th>Lng</th>"
            "<th>Free energy</th><th>Belief entropy</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></body></html>"
        )
    return write_html_figure_artifact(
        config,
        "visualizations/interactive_h3_map.html",
        html,
        title=title,
        description=description,
        alt_text=alt_text,
        plotted_metrics=[
            "free_energy",
            "expected_free_energy",
            "belief_entropy",
            "action",
            "lat",
            "lng",
        ],
        data_sources=["data/h3_cells.csv", "data/h3_cells.geojson"],
        plotted_data=cell_metrics,
    )


def main(argv: Optional[List[str]] = None) -> int:
    """CLI-compatible main for direct module execution."""
    from geo_infer_act.runners.cli import main as cli_main

    return cli_main(argv if argv is not None else sys.argv[1:])
