# GEO-INFER validation evidence — 2026-08-13

This receipt records the documentation-audit validation campaign against the
uncommitted worktree based on Git commit
`e561998bddc4552314e1e6b8f30ed369c0caa572`. It is evidence for the tested
bytes, not a claim that the checkout was clean, committed, or release-ready.

## Tested state

- Base commit: `e561998bddc4552314e1e6b8f30ed369c0caa572`.
- Changed source/test digest:
  `940ede954d357ed1887bc991948e1932e9441fa5b96db3a6cbb7b58e56c79cf9`.
  This is the SHA-256 of sorted `sha256sum` records for every modified or
  untracked path selected by `(^|/)(src|tests)/`, root `conftest.py`, or
  `GEO-INFER-TEST/run_unified_tests.py`. Documentation-only edits and ignored
  result files are intentionally outside this digest.
- `pyproject.toml` SHA-256:
  `6f1278b0666da53ac30f24f00f7decde44a18a39e99395690accc79c73c1596f`.
- `uv.lock` SHA-256:
  `3f76ba37a270fccaf85e86e31efea05c49b0361febc27f6f1d41497deb61de50`.
- Test window: 2026-08-13, America/Los_Angeles. Performance began at
  11:47; the coverage report and retry were complete by 13:10.

## Environment

| Item | Observed value |
| --- | --- |
| OS | Linux `7.0.13+parrot7-amd64`, x86_64, glibc 2.41 |
| Python | 3.12.11 |
| uv | 0.12.3 |
| H3 | 4.5.0 |
| TensorFlow | 2.19.0 |
| PyTorch | 2.8.0; CUDA available; one NVIDIA GeForce GTX 1650 Ti |
| PyMC | 5.25.1 |
| Mesa | 3.5.1 |
| JAX | 0.5.3 |
| XGBoost | 3.0.3 |
| Not installed | SRAI, Lifelines, CuPy, LightGBM, Optuna |

The locked all-extras command did **not** succeed:

```bash
uv sync --locked --all-packages --all-extras
```

It exited 1 while building `cupy==13.5.1`. This host exposes a CUDA-capable
GPU to PyTorch, but it does not provide the CUDA development headers or
`nvcc` required for a source CuPy build. The results below therefore describe
the existing CPU/available-backend environment, not a fully synchronized
all-extras installation.

## Performance campaign

Command:

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --category performance --timeout 600
```

Exit code: 0. The runner passed 4/4 isolated module steps. JUnit recorded 52
tests, 0 failures, 0 errors, and 0 skips in 57.113 aggregate test seconds:

| Module | Tests | Runner duration (s) |
| --- | ---: | ---: |
| ANT | 10 | 36.956 |
| DATA | 15 | 25.147 |
| INTRA | 8 | 4.655 |
| SPM | 19 | 4.660 |

The four JUnit files have aggregate digest
`e4687d31d30bdde5d1dd73a4a288c856720586698b336505c3ba80876f2dd37f`;
the successful runner summary has digest
`38fcfd8e96e61f106552b09bf5045783ac9dc1099c6eff3db4d1d16a448ab63c`.
The aggregate digest hashes each sorted filename, a NUL byte, and its exact
file bytes.

## Coverage campaign

Initial command:

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --category coverage --timeout 600
```

Exit code: 1; runner summary: 45/46 steps passed. All 44 module JUnit reports
were written with 7,327 tests, 0 failures, 0 errors, and 0 skips, and both
coverage-report commands passed. The METAGOV tests themselves recorded 115
passes in 5.514 JUnit seconds, but that pytest process did not terminate after
writing its report. During the run the execution host was suspended for about
49 minutes; on resumption, the configured timeout was reported after 2,971.024
wall seconds. The failed attempt remains a failure in the original summary,
whose digest is
`f5135a021a21f724baaa99c9b687eaa43253416b286721a09499a3f8d7b21981`.

The hang could not be reproduced: METAGOV exited in 1.23 seconds without
coverage and 2.74 seconds with an isolated coverage file. Its exact aggregate
coverage step was then retried against the campaign coverage file:

```bash
mapfile -t metagov_tests < <(
  find GEO-INFER-METAGOV/tests -type f \
    \( -name 'test_*.py' -o -name '*_test.py' \) -print | sort
)
COVERAGE_FILE="$PWD/.geo-infer-test-results/.coverage" \
  uv run python -m pytest -c "$PWD/pyproject.toml" \
  -v --tb=short --durations=10 -W error \
  "${metagov_tests[@]}" \
  --cov="$PWD/GEO-INFER-METAGOV/src" --cov-append --cov-report= \
  --junitxml="$PWD/.geo-infer-test-results/METAGOV_coverage_results.xml"
```

Retry exit code: 0; 115 passed in 2.16 seconds. The timeout is not reclassified
as a pass: the original failed attempt and the successful retry are separate
observations.

Final report commands:

```bash
COVERAGE_FILE="$PWD/.geo-infer-test-results/.coverage" \
  uv run python -m coverage json \
  -o "$PWD/.geo-infer-test-results/coverage.json"
COVERAGE_FILE="$PWD/.geo-infer-test-results/.coverage" \
  uv run python -m coverage report --show-missing
```

Both exited 0. Final line coverage is 64,584 of 121,204 statements,
53.285370119798024%; 56,620 statements are missing and 1,454 are excluded.
No repository-wide coverage floor is declared for this aggregate. The final
44 JUnit files have aggregate digest
`f3374d922d9fa34871c22cf9e6dcabe775b0b3809c8645d778960e9719d597d4`;
the final coverage JSON digest is
`ffcd520b748dadce122802538150c26f5acdc2573bcad5fab35b2e9778f1089a`.

## Contract and focused validation

- Generated documentation: all 1,697 generated README/folder-contract files
  current; 30 authoritative pages passed strict documentation validation.
- Repository contracts: 44 modules checked, 0 errors, 0 warnings under strict
  source-language validation.
- Test contracts: every inventory, marker, control, and docstring check passed.
- Skills: 45/45 passed, including cross-references.
- H3/Active Inference contract passed; all nine deterministic model probes
  returned finite results.
- The 23 changed Python files passed focused Ruff `E`, `F`, and `I` checks and
  `ruff format --check`.
- The rewritten Cascadia focused profile passed 4/4 and the canonical/full
  profile passed 6/6. Its complete nested integration directory is **not**
  green: 19 passed, 5 failed, and 1 skipped because four referenced ecological
  GeoJSON inputs are absent. `PLACE-V14` tracks authoritative sourcing,
  licensing, and provenance for those inputs; no coordinates were invented.

## Interpretation

The performance and module-coverage evidence is complete for the recorded
worktree and available backends. It does not prove a full all-extras install,
high aggregate coverage, or a clean Cascadia bioregion-data surface. Those
boundaries remain explicit so downstream release decisions can distinguish a
tested campaign from full release readiness.
