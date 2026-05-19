# GEO-INFER-ACT Documentation

These documents describe the canonical Active Inference implementation in
`GEO-INFER-ACT/src/geo_infer_act`.

## Start Here

- [Active Inference Overview](./active_inference_overview.md): concepts and code map.
- [Free Energy Principle](./free_energy_principle.md): VFE/EFE equations and implementation locations.
- [Mathematical Framework](./mathematical_framework.md): deeper mathematical notes.
- [Method, Output, and Visualization Inventory](./method_inventory.md): public ACT method surface, runner outputs, and visualization artifact contract.
- [Geospatial Applications](./geospatial_applications.md): runnable geospatial examples using current ACT classes.
- [World Systems Modeling](./world_systems_modeling.md): systems-level framing.
- [References](./references.md): background citations.

## Verification

From the repository root:

```bash
uv run --package geo-infer-act --extra dev python GEO-INFER-ACT/verify_comprehensive.py \
  --output-dir GEO-INFER-ACT/examples/output/comprehensive_act_audit
uv run python GEO-INFER-TEST/validate_act_script_orchestration.py
uv run python GEO-INFER-TEST/validate_active_inference_contract.py
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests -q
```

`verify_comprehensive.py` audits every ACT markdown file, every ACT README, all
local markdown links, and every Mermaid block. When `mmdc` is installed, the
Mermaid blocks are rendered to SVG under
`../examples/output/comprehensive_act_audit/method_audit/docs_and_mermaid/mermaid/`
and each render result is recorded in `docs_mermaid_audit.json`.

## Runner Contracts

Scenario scripts in `GEO-INFER-ACT/examples/`, `debug_models.py`, and
`verify_pipeline.py` are compatibility wrappers. The canonical runner API is:

```python
from geo_infer_act.runners import RunConfig, run_scenario

result = run_scenario(
    RunConfig(
        scenario="h3",
        output_dir="/tmp/geo-infer-act-h3",
        seed=42,
        timesteps=8,
        visualizations=True,
    )
)
print(result.manifest_path)
```

The external file contracts are versioned JSON Schema files in
`src/geo_infer_act/schemas/`. When visualizations are enabled, every generated
figure is also a traceable artifact: the manifest records artifact type, MIME
type, digest, sidecar paths, plotted metrics, data sources, description, and alt
text; the figure itself embeds ACT metadata; and adjacent sidecars store
`*.metadata.json` plus the exact plotted data as CSV or JSON.

The canonical logged audit output for documentation and diagram verification is
`../examples/output/comprehensive_act_audit/`.
