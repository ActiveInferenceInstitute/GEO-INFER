# Setting Up GEO-INFER

This tutorial walks through setting up the GEO-INFER workspace for first-time
use. GEO-INFER is a uv-managed monorepo; there is no standalone PyPI
distribution — you work from a clone of the repository.

## Prerequisites

- **Python 3.11+** (see `.python-version`).
- **uv** (the package manager; install from https://docs.astral.sh/uv/).
- **Git**.

## Step 1: Clone and Sync

```bash
git clone https://github.com/ActiveInferenceInstitute/GEO-INFER.git
cd GEO-INFER
uv sync --all-packages --all-extras
```

For work on a single module, sync only that package:

```
```bash
uv sync --package geo-infer-act
```

## Step 2: Verify the Workspace

Run the syntax and documentation gates:

```
```bash
python -m compileall GEO-INFER-*/src GEO-INFER-*/examples
uv run python GEO-INFER-TEST/validate_documentation.py --strict
```

## Step 3: Run an Example

Each module ships runnable examples under `GEO-INFER-*/examples/`. For
example, the ACT module examples:

```
```bash
uv run python GEO-INFER-ACT/examples/simple_model.py
```

See the [Examples gallery](../../examples_gallery.md) and the
[First Analysis](../../getting_started/first_analysis.md) tutorial for guided
workflows.

## Step 4: Configure

Module configuration lives in each module's `config/` directory and is read at
runtime through the module packages. See the module READMEs for the
configuration reference of each package.

## Next Steps

- [Installation Guide](../../getting_started/installation_guide.md) — detailed
  setup including CI extras.
- [First Map](../../getting_started/first_map.md) — render your first map.
- [Developer Guide](../../developer_guide/index.md) — for contributors.
