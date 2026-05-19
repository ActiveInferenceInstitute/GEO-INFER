# GEO-INFER-ACT Logged Outputs

This directory is reserved for intentional ACT run artifacts that should be easy
to inspect from the repository. The current canonical folder is
`comprehensive_act_audit/`, produced by:

```bash
uv run --package geo-infer-act --extra dev python GEO-INFER-ACT/verify_comprehensive.py \
  --output-dir GEO-INFER-ACT/examples/output/comprehensive_act_audit
```

## `comprehensive_act_audit/`

The comprehensive audit folder is a logged, reproducible evidence bundle for
ACT methods, runner outputs, visualization generation, README coverage, and
Mermaid rendering.

Key files and folders:

- `comprehensive_audit_summary.json`: top-level status, section timings, and
  links to section payloads.
- `logs/comprehensive_audit.log`: timestamped execution log.
- `method_audit/*/result.json`: one result file per audited method family.
- `method_audit/visualization_methods/figures/`: direct visualization-method
  PNG outputs.
- `method_audit/scenario_outputs/scenario_suite/`: all runner scenario outputs,
  including manifests, data files, analysis JSON, logs, visualization artifacts,
  sidecars, and suite manifest.
- `method_audit/docs_and_mermaid/`: README/local-link audit plus Mermaid source
  and rendered SVG files when `mmdc` is available.

These artifacts are generated data, but they are intentionally retained because
they are the evidence bundle for the current ACT audit.
