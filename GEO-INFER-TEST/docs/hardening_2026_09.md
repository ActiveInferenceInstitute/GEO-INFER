# September 2026 hardening review

This review covers the 44-module workspace at baseline `fc62502cce7111398b34363e9928536f9837006d`.
The user-approved scope includes numeric acceleration, real streaming transports,
deterministic spatial previews, and a bounded USGS hydrography pilot with a
configurable US Cascadia loader. Full-region acquisition, publication, and
claims of hardware speedup are outside this pass.

## Changes and migrations

- [SPACE kernels](../../GEO-INFER-SPACE/docs/GPU_ACCELERATION.md): lazy device
  checks, explicit backend selection, float64 reference parity, bounded distance
  tiles, stable label semantics, and honest host-only H3 topology reporting.
- [TIME transports](../../GEO-INFER-TIME/docs/streaming_migration.md): real
  WebSocket and Kafka ingestion, explicit replay, bounded buffers, event-time
  ordering, watermark/window corrections, and acknowledgement after processing.
- [PLACE hydrography](../../GEO-INFER-PLACE/src/geo_infer_place/hydrography/GUIDE.md):
  installable source/network APIs, resumable bounded acquisition, checksummed
  native IDs, full topology before filtering, and a bundled 34-reach USGS excerpt.
- [Module previews](../../GEO-INFER-INTRA/docs/modules/previews_index.md): all 44
  bundles contain actual H3 resolution 7 geometry, deterministic HTML/SVG/PNG,
  artifact checksums, illustrative-content labels, and an offline SVG fallback.
- Runtime version literals now agree with each distribution's declared 0.2.0
  metadata. Conflicting runtime license literals agree with repository licensing.
- Imports in repository validation run in separate processes with per-package
  timeouts. Wheel checks compare metadata and source resources, then install and
  import actual wheels in an isolated environment outside the checkout. Installed
  imports have a configurable positive timeout and capture child stacks when
  they block, so a timeout includes a diagnostic rather than only an exit code.
  A shared runner requires a parent-validated completion receipt and terminates
  the POSIX process group on timeout, including ordinary child processes.

### Raster expressions

`geo_infer_space.analytics.raster.map_algebra` evaluates an allowlisted expression
AST. Inputs must share dimensions, transform, and CRS. Nodata masks propagate;
nonfinite results become the requested finite float32 nodata value. Scalar
expressions broadcast to the raster shape. Existing arithmetic and comparison
expressions using `b1`, `b2`, etc. continue to work, including
`np.where(b1 > 0, b1 / b2, nodata)`.

Supported NumPy calls are `where`, `sqrt`, `log`, `log10`, `exp`, `abs`,
`minimum`, `maximum`, `clip`, `isfinite`, `logical_and`, `logical_or`, and
`logical_not`. They accept only their unary, binary, or ternary arguments. Arbitrary
Python calls, attribute chains, indexing, mutation via output arguments, and
filesystem access raise `ValueError`. Expressions are limited to 4096 characters
and 128 AST nodes. Migrate broader calculations into ordinary trusted Python code
and pass resulting rasters explicitly.

## Verification method

The baseline was captured before edits, with remaining slow suites rerun in a
detached pristine checkout and every package import origin asserted. Baseline
180-second timeouts are recorded as incomplete measurements under concurrent
load, not as product failures. Final module tests use separate processes with
600-second limits and strict repository warning/skip policies. The four incomplete
baseline suites were subsequently repeated with 600-second limits in the pristine
checkout; their completed results replace timeout-only entries in the table.

All 44 wheels are built in fresh directories and installed together into a clean
virtual environment with locked dependency constraints. `python -I` probes
require imports from that environment. Source Python modules, package-data globs, and configuration resource inventories
and bytes are compared with wheel contents before installation.

Actual Kafka 4.3.1 loopback verification exercised produce, unacknowledged replay,
commit, and resumed consumption. The owned container was removed afterward.
The immutable image digest was
`sha256:77e3df9054047a88b520d0cc46e16696d3b22022e1d580aeccd2632df6532837`.
WebSocket tests use real local servers. The Smith River pilot was acquired from
the official USGS service; its bundled manifest records source selection and
checksums. Local HTTP tests exercise pagination and failure/resume paths.

## Verification limits

- [DEFERRED-VERIFY] Real GPU parity and performance require a supported physical
  GPU. Local CuPy is absent; Torch has no CUDA and JAX exposes CPU only. CPU and
  injected failure-path tests do not establish GPU performance.
- [DEFERRED-VERIFY] Interceptor reports no connected browser extension. Generated
  geometry, deterministic bytes, resource links and static imagery were checked;
  keyboard interaction and live Leaflet rendering require a connected browser.
- [DEFERRED-VERIFY] Windows `taskkill` process-tree cleanup is implemented but
  was not exercised. POSIX timeout cleanup was verified with real child processes.
- The bundled Smith River excerpt contains 34 reaches in a bounded envelope. It
  does not establish full Smith River watershed or full Cascadia coverage.

## Pre-merge module and gate results

The tables below describe implementation commit `3a68ce80`, before integrating
remote `b7e3a8ea`. They are generated from captured command outcomes and
JUnit reports. Local detailed logs live under `/tmp/geo-infer-final-tests/` and
`/tmp/geo-infer-baseline-fc62502c/`; these are ephemeral verification artifacts.
<!-- VERIFIED-RESULTS -->

| Module | Baseline Python 3.12 | Final Python 3.12 | Final Python 3.11 |
| --- | --- | --- | --- |
| GEO-INFER-ACT | 465 pass | 465 pass | 465 pass |
| GEO-INFER-AG | 83 pass | 83 pass | 83 pass |
| GEO-INFER-AGENT | 208 pass | 208 pass | 208 pass |
| GEO-INFER-AI | 85 pass | 85 pass | 85 pass |
| GEO-INFER-ANT | 164 pass | 164 pass | 164 pass |
| GEO-INFER-API | 108 pass | 108 pass | 108 pass |
| GEO-INFER-APP | 63 pass | 63 pass | 63 pass |
| GEO-INFER-ART | 72 pass | 72 pass | 72 pass |
| GEO-INFER-BAYES | 311 pass | 311 pass | 311 pass |
| GEO-INFER-BIO | 43 pass | 43 pass | 43 pass |
| GEO-INFER-CIV | 90 pass | 90 pass | 90 pass |
| GEO-INFER-CLIMATE | 98 pass | 98 pass | 98 pass |
| GEO-INFER-COG | 167 pass | 167 pass | 167 pass |
| GEO-INFER-COMMS | 53 pass | 53 pass | 53 pass |
| GEO-INFER-DATA | 322 pass, 1 failures | 323 pass | 323 pass |
| GEO-INFER-ECON | 154 pass | 154 pass | 154 pass |
| GEO-INFER-EDU | 101 pass | 101 pass | 101 pass |
| GEO-INFER-EMERGENCY | 140 pass | 140 pass | 140 pass |
| GEO-INFER-ENERGY | 93 pass | 93 pass | 93 pass |
| GEO-INFER-EXAMPLES | 71 pass | 71 pass | 71 pass |
| GEO-INFER-FOREST | 81 pass | 81 pass | 81 pass |
| GEO-INFER-GIT | 123 pass | 123 pass | 123 pass |
| GEO-INFER-HEALTH | 195 pass | 195 pass | 195 pass |
| GEO-INFER-INTRA | 46 pass | 50 pass | 50 pass |
| GEO-INFER-IOT | 96 pass | 96 pass | 96 pass |
| GEO-INFER-LOG | 65 pass | 65 pass | 65 pass |
| GEO-INFER-MARINE | 89 pass | 89 pass | 89 pass |
| GEO-INFER-MATH | 289 pass | 289 pass | 289 pass |
| GEO-INFER-METAGOV | 115 pass | 115 pass | 115 pass |
| GEO-INFER-NORMS | 135 pass | 135 pass | 135 pass |
| GEO-INFER-OPS | 157 pass | 157 pass | 157 pass |
| GEO-INFER-ORG | 91 pass | 91 pass | 91 pass |
| GEO-INFER-PEP | 84 pass | 84 pass | 84 pass |
| GEO-INFER-PLACE | 316 pass, 14 failures | 359 pass | 359 pass |
| GEO-INFER-REQ | 70 pass | 70 pass | 70 pass |
| GEO-INFER-RISK | 255 pass | 255 pass | 255 pass |
| GEO-INFER-SEC | 257 pass | 257 pass | 257 pass |
| GEO-INFER-SIM | 60 pass | 60 pass | 60 pass |
| GEO-INFER-SPACE | 532 pass, 1 failures | 582 pass | 582 pass |
| GEO-INFER-SPM | 360 pass | 360 pass | 360 pass |
| GEO-INFER-TEST | 1309 pass | 1378 pass | 1378 pass |
| GEO-INFER-TIME | 423 pass | 456 pass | 456 pass |
| GEO-INFER-TRANSPORT | 90 pass | 90 pass | 90 pass |
| GEO-INFER-WATER | 84 pass | 84 pass | 84 pass |
| **Total** | 8213 pass, 16 failures | 8413 pass | 8413 pass |

The baseline DATA failure was its wall-clock validation benchmark under concurrent
load; no performance correction is claimed. SPACE's baseline failure concerned
numeric precision. PLACE's 14 baseline failures concerned absent geographic layers
and implicit flowline data. The final suites include added regressions, so their
inventories are larger. There are no final failures, errors, or skips.

The final tests ran once per module/process using Python 3.12.11 and 3.11.15:

```bash
# Repeat for each of the 44 module directories, with the corresponding interpreter.
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MPLBACKEND=Agg \
  .venv/bin/python -m pytest GEO-INFER-<MODULE>/tests -q --tb=short \
  --junitxml=/tmp/geo-infer-final-tests/GEO-INFER-<MODULE>.xml
```

The outer runner limits each process to 600 seconds and prepends all workspace
`src` directories to `PYTHONPATH`. Targeted reruns replaced final reports after
metadata-test migrations and the additional shared-validator/preview regressions.
PLACE's equivalent complete suite was run by its implementation owner.

| Gate | Final outcome | Command or evidence |
| --- | --- | --- |
| Locked dependency consistency | Pass | `uv lock --check` |
| Source syntax 3.11/3.12 | Pass | `python -m compileall -q GEO-INFER-*/src GEO-INFER-*/examples` |
| Critical source hygiene | Pass | `ruff check GEO-INFER-*/src --select F821,F823,E721,E722` |
| Changed Python formatting | Pass | `ruff format --check` on changed/new Python files |
| Repository contracts | 44 modules, 0 errors, 0 warnings | `validate_repo_contracts.py --strict-source-language` |
| Packaging contracts | 44 modules, 0 errors, 0 warnings | `validate_packaging.py --strict` |
| Authoritative documentation | 30 pages pass | `validate_documentation.py --strict` |
| Skill contracts | 45 files pass, 0 warnings | `validate_skills.py --check-xrefs` |
| Generated signposts | 1,692 current | `rewrite_readme_agents.py --check` |
| Test contracts | Pass | `validate_test_contracts.py --strict` |
| Model contracts 3.11/3.12 | Pass | `validate_model_contracts.py --strict --seed 42` |
| Reproducibility 3.11/3.12 | Identical hash | `run_model_audit.py --seed 42 --reproducible` |
| Active Inference/H3 | Pass | `validate_active_inference_contract.py`, `validate_h3_active_inference_contract.py` |
| Geospatial H3 artifacts 3.11/3.12 | Pass | `validate_act_geospatial_contract.py` |
| ACT orchestration | Pass | `validate_act_script_orchestration.py` |
| Final wheel inventories | 44 match source code/data bytes and metadata | `build_package_wheels.py --outdir /tmp/geo-infer-final-wheels --verify`; final content comparison |
| macOS installed wheel probes 3.11/3.12 | 44 pass on each interpreter | `/tmp/geo-final-installed-wheels311-bounded.log`, `/tmp/geo-final-installed-wheels312-bounded.log` |
| Linux ARM64 installed wheel probes 3.11/3.12 | 44 pass on each interpreter; 11 resource files verified per run | `/tmp/geo-linux-wheel-py311-20260904-systemdeps/`, `/tmp/geo-linux-wheel-py312-20260904-systemdeps/` |
| Kafka live service | Pass | `GEO-INFER-TIME/tests/integration/kafka_service_check.py --bootstrap-servers 127.0.0.1:9092` |
| Preview regeneration | 44 bundles byte-identical | Regeneration to a temporary directory compared with tracked HTML/SVG/PNG/manifests |
| Git whitespace | Pass | `git diff --check` |

Validator command filenames in this table are relative to `GEO-INFER-TEST/`.
Both model audits produced
`d195004a4030f4362b0f9402b218a318864766f7f321ef77697a595db18f32dc`.

## Independent review and remaining work

Peer review reproduced and closed mutable NumPy output arguments in raster
expressions, unsafe SVG color attributes, missing wheel resources/code, import
shadowing, lost multipart flowlines, incorrect projected-coordinate handling,
and slow-response budgets. H3 sampling is now documented as approximate.
A final fresh-context review reproduced two validator gaps: early successful
process exits bypassed validation, and timed-out imports left descendants alive.
Both were corrected in the shared import-probe runner. Twelve added regression
cases cover `SystemExit(0)`, `os._exit(0)`, delayed child writes after timeout,
and nonfinite timeout values in both CLIs. All 41 focused import/wheel tests pass.
Existing clean-install matrix logs were also checked for all 44 unique completed
package receipts per interpreter; their passes do not depend on exit codes alone.

Runtime metadata review added a 44-package regression and corrected CI's
initial-commit diff fallback. The H3 artifact gate exposed seven missing runner
docstrings; those were added without changing executable ASTs.

The planned local implementation is complete. The backlog retains explicit GPU
hardware and browser verification work, full-region hydrography acquisition,
and acquisition of the four absent regional geographic layers. No local CPU test
or constructed test fixture substitutes for those measurements.


Installed-wheel verification initially timed out in ART at 120 seconds in fresh
macOS environments, including an isolated hardlink probe. Native sampling
showed `dyld` mapping and signature validation; child stack capture located
native pandas imports. These failures are retained in the local timeout logs.
The successful final macOS matrix ran sequentially with `UV_LINK_MODE=hardlink`
and an explicit 600-second per-import bound (`--import-timeout 600` in the wheel CLI). No operating
system validation or security controls were changed. These runs establish
import/resource correctness, not a cold-start latency guarantee. A regression
checks that a blocked installed import times out with its child stack attached.


The macOS clean-install runs completed in 664.37 seconds (Python 3.11.15) and
440.45 seconds (3.12.11), including installation and all 44 import probes.
Linux ARM64 containers independently verified the same 44 wheel hashes on Python
3.11.16 and 3.12.14, with no import errors, stderr, or timeouts. Each checked
installed origins, runtime/distribution versions, and 11 packaged configuration
resources byte-for-byte. Total run times were 521.33 and 486.88 seconds.

The Linux images were `python:3.11-slim` at
`sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534`
and `python:3.12-slim` at
`sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea`.
Initial dependency installation failed because the pinned Fiona/Rasterio builds
needed GDAL on ARM64. Container-only `build-essential` and `libgdal-dev` resolved
that prerequisite; original failure logs remain available. Both containers had
only read-only wheel and constraint mounts, no source checkout, and no published
ports. All owned containers were removed. These are local ARM64 results; hosted
x86 CI was not executed.

GitNexus had no GEO-INFER index. Caller and impact review used repository text
search and direct source inspection, with reduced code-intelligence confidence.


## Publication integration on September 4

Remote `main` advanced seven commits from the original baseline to `b7e3a8ea`.
The tested local implementation was preserved as `3a68ce80` before a normal merge;
neither published history nor unrelated upstream work was rewritten.

Conflict reconciliation preserved upstream unconditional public imports and BIO
exports while retaining canonical package versions. TIME retains normalization,
injected adapters, broker timestamps and dependency diagnostics within the real
transport/manual-acknowledgement implementation. PLACE retains environment-path
and offline controls, branching-network coverage, and explicit observable
projection fallback within its installable package. The wheel builder retains
fresh builds, archive checks and complete isolated-import receipts; a regression
proves stale wheel filenames cannot satisfy a new build. Upstream dependency
parity, passive-logging checks, fail-fast test orchestration and manuscript CI
remain enabled. Requirements now declare Pillow/networkx alongside package
metadata, and the combined dependency lock was regenerated.

Pre-merge results above are historical evidence. Remaining
work is centralized in [TODO.md](../../TODO.md), with responsible areas,
prerequisites, bounded deliverables and acceptance evidence.


The complete merged module suites pass **8,607 tests on Python 3.11.15 and
8,607 on 3.12.11**, with zero failures, errors or skips. Reports live at
`/tmp/geo-merge-tests311/` and `/tmp/geo-merge-tests312/`. The same bounded
per-module runner and CPU environment described above were used.

The first merged ANT runs failed their 300 MB RSS cleanup threshold. A separate
three-cycle probe found zero retained agent weak references; after the first
cycle, traced Python allocation growth was about 0.07 MB per cycle while process
RSS varied much more. The cleanup benchmark now performs an identical seeded
warmup before measuring retained simulation memory, keeping the original 300 MB
limit and explicitly asserting release of all agent objects. Complete ANT suites
then passed on both interpreters. Original failures and allocation-probe output
are retained under `/tmp/geo-ant-merge-investigation/` and alongside the final
JUnit reports; no cold-import memory improvement is claimed.

The first clean merged wheel run found DATA's newly unconditional connector
imports required undeclared `aiohttp`. Its runtime metadata and requirements now
include that dependency. Three missing test imports reported by upstream CI
(`networkx`, `structlog`, `sys`) were also corrected. These findings demonstrate
why pre-merge workspace results were not treated as installed-package evidence.

All twelve merged repository/package/logging/documentation/skill/test/model/
reproducibility/Active-Inference/H3/geospatial/orchestration gates pass; outputs
are in `/tmp/geo-merge-gates/`. Python 3.11 model contracts and reproducibility
also pass with the same deterministic hash recorded above. The newly integrated
manuscript producer passes `--verify`; its outputs remain ignored. Generated
signposts are maintained from the merged inventory: 922 source files, 566 test
files and 1,692 README/AGENTS files.


### Combined-tree module results

| Module | Python 3.12 passed | Python 3.11 passed |
| --- | ---: | ---: |
| GEO-INFER-ACT | 465 | 465 |
| GEO-INFER-AG | 83 | 83 |
| GEO-INFER-AGENT | 209 | 209 |
| GEO-INFER-AI | 89 | 89 |
| GEO-INFER-ANT | 164 | 164 |
| GEO-INFER-API | 122 | 122 |
| GEO-INFER-APP | 63 | 63 |
| GEO-INFER-ART | 72 | 72 |
| GEO-INFER-BAYES | 312 | 312 |
| GEO-INFER-BIO | 43 | 43 |
| GEO-INFER-CIV | 90 | 90 |
| GEO-INFER-CLIMATE | 98 | 98 |
| GEO-INFER-COG | 169 | 169 |
| GEO-INFER-COMMS | 53 | 53 |
| GEO-INFER-DATA | 365 | 365 |
| GEO-INFER-ECON | 164 | 164 |
| GEO-INFER-EDU | 106 | 106 |
| GEO-INFER-EMERGENCY | 149 | 149 |
| GEO-INFER-ENERGY | 93 | 93 |
| GEO-INFER-EXAMPLES | 71 | 71 |
| GEO-INFER-FOREST | 84 | 84 |
| GEO-INFER-GIT | 123 | 123 |
| GEO-INFER-HEALTH | 200 | 200 |
| GEO-INFER-INTRA | 50 | 50 |
| GEO-INFER-IOT | 97 | 97 |
| GEO-INFER-LOG | 67 | 67 |
| GEO-INFER-MARINE | 92 | 92 |
| GEO-INFER-MATH | 306 | 306 |
| GEO-INFER-METAGOV | 129 | 129 |
| GEO-INFER-NORMS | 135 | 135 |
| GEO-INFER-OPS | 165 | 165 |
| GEO-INFER-ORG | 91 | 91 |
| GEO-INFER-PEP | 84 | 84 |
| GEO-INFER-PLACE | 365 | 365 |
| GEO-INFER-REQ | 70 | 70 |
| GEO-INFER-RISK | 257 | 257 |
| GEO-INFER-SEC | 265 | 265 |
| GEO-INFER-SIM | 63 | 63 |
| GEO-INFER-SPACE | 583 | 583 |
| GEO-INFER-SPM | 360 | 360 |
| GEO-INFER-TEST | 1384 | 1384 |
| GEO-INFER-TIME | 474 | 474 |
| GEO-INFER-TRANSPORT | 98 | 98 |
| GEO-INFER-WATER | 85 | 85 |
| **Total** | **8607** | **8607** |


### Final merged installed-wheel verification

Both fresh builds and clean isolated installations passed after declaring DATA's
`aiohttp` dependency. Each package completed origin, version and resource checks.
The final archives were independently compared with current source code, metadata
and resource bytes. Imports used the explicit 600-second bound; no speed guarantee
is implied. Wheel-inventory digests hash sorted `filename sha256` lines.

- Python 3.11: 44 completed import receipts and 44 source-matching wheels;
  inventory SHA256 `2fd309b9ef9489f65c0eba01b212e26888c1a25ce7ec212ecdadb5ba647724d4`.
- Python 3.12: 44 completed import receipts and 44 source-matching wheels;
  inventory SHA256 `ef9b2dbeb886a08fc693afe427b2a4ad3c91fe501eb4bb0a8a182342b829a2d7`.

Logs: `/tmp/geo-merge-wheels311-final.log` and
`/tmp/geo-merge-wheels312-final.log`. The earlier missing-dependency failure remains
in `/tmp/geo-merge-wheels311.log`. The pre-merge Linux ARM64 checks above remain
historical; the final merged clean-install checks were run on macOS. Hosted CI
results must be tied to the pushed SHA. Outgoing formatting, critical lint and
whitespace checks are scoped against the fetched remote `main`.
