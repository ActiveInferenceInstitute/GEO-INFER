# GEO-INFER-INTRA Documentation

## Overview

This directory is the central documentation hub for the GEO-INFER monorepo. It
contains architecture notes, integration guides, getting-started tutorials,
module references, and generated or historical assessment outputs.

## Current Entry Points

- `getting_started/active_inference_basics.md`: runnable current Active Inference tutorial using `GenerativeModel`, `ActiveInferenceModel`, typed ACT result objects, and expected-free-energy policy selection.
- `active_inference_guide.md`: conceptual Active Inference guide for geospatial systems, with signposts to the ACT H3/spatial manifest, visualization metadata, and figure sidecar contract.
- `architecture/module_catalog.md`: module inventory and cross-module signposting.
- `guides/MODULE_INTEGRATION_GUIDE.md`: cross-module integration patterns.
- `developer_guide/testing_guide.md`: testing conventions and command structure.

## Verification Commands

```bash
uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
uv run python GEO-INFER-TEST/validate_repo_contracts.py
uv run python GEO-INFER-TEST/validate_active_inference_contract.py
uv run python GEO-INFER-TEST/validate_act_geospatial_contract.py
```

Generated assessment outputs under `assessment_results/` are historical unless
explicitly regenerated in the current pass.
