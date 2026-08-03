# Installation

GEO-INFER is a uv-managed monorepo: there is no standalone PyPI distribution
for the framework. You install by cloning the repository and syncing the uv
workspace.

## Prerequisites

- **Python 3.11+** (see `.python-version` in the repository root).
- **uv** — the package manager (install from https://docs.astral.sh/uv/).
- **Git**.

## Method 1: Full Workspace Sync

```bash
git clone https://github.com/ActiveInferenceInstitute/GEO-INFER.git
cd GEO-INFER
uv sync --all-packages --all-extras
```

`--all-extras` installs the optional scientific, Bayesian, web, IoT,
performance, quality, and documentation dependencies. CI intentionally omits
native-only extras that cannot build on its CPU runner; see
`.github/workflows/ci.yml` for the exact exception list.

## Method 2: Single-Package Sync

When developing one module, sync only that package:

```
```bash
uv sync --package geo-infer-act
uv sync --package geo-infer-space
```

## Verifying the Installation

From the repository root:

```
```bash
python -m compileall GEO-INFER-*/src GEO-INFER-*/examples
uv run python GEO-INFER-TEST/validate_documentation.py --strict
```

See the [Quick Start](../getting_started/installation_guide.md) and the
[First Analysis](../getting_started/first_analysis.md) tutorial for the full
onboarding path.

## Troubleshooting

If you encounter issues during installation:

- Check that `uv` is installed and on your `PATH`.
- Verify your Python version is 3.11+.
- Run `uv sync --all-packages --all-extras` again after pulling latest `main`.
- See the [Installation Issues](../support/installation_issues.md) page.

## Next Steps

- [Installation Guide](../getting_started/installation_guide.md) — detailed
  setup including CI extras.
- [Configuration](../deployment/environment.md) — environments and setup.
- [Getting Started](../getting_started/index.md) — first workflows.
