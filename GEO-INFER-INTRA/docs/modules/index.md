# Module Catalog

GEO-INFER contains 44 independently packaged modules. Every module has a
package directory, `pyproject.toml`, tests, generated `README.md` and
`AGENTS.md` signposts, and a `SKILL.md` describing current agent-facing usage.

Use the root [module index](../../../README.md#module-index) for live source and
test counts. The links below are the conceptual pages in this documentation
hub; the module-local README is the source-backed operational reference.

## Foundations and inference

| Module | Role | Operational reference |
| --- | --- | --- |
| ACT | Active Inference, free energy, policies, spatial diagnostics | [README](../../../GEO-INFER-ACT/README.md) · [guide](geo-infer-act.md) |
| AI | Machine-learning and model integration | [README](../../../GEO-INFER-AI/README.md) · [guide](geo-infer-ai.md) |
| BAYES | Bayesian models and inference | [README](../../../GEO-INFER-BAYES/README.md) · [guide](geo-infer-bayes.md) |
| COG | Cognitive and attention models | [README](../../../GEO-INFER-COG/README.md) · [guide](geo-infer-cog.md) |
| MATH | Mathematical and statistical foundations | [README](../../../GEO-INFER-MATH/README.md) · [guide](geo-infer-math.md) |
| SPM | Spatial statistical inference | [README](../../../GEO-INFER-SPM/README.md) · [guide](geo-infer-spm.md) |

## Spatial, temporal, and data foundations

| Module | Role | Operational reference |
| --- | --- | --- |
| DATA | Ingestion, validation, storage, caching | [README](../../../GEO-INFER-DATA/README.md) · [guide](geo-infer-data.md) |
| SPACE | H3 v4, CRS, geometry, backend dispatch | [README](../../../GEO-INFER-SPACE/README.md) · [guide](geo-infer-space.md) |
| TIME | Time series and temporal analysis | [README](../../../GEO-INFER-TIME/README.md) · [guide](geo-infer-time.md) |
| IOT | Sensor and streaming integration | [README](../../../GEO-INFER-IOT/README.md) · [guide](geo-infer-iot.md) |

## Agents, optimization, and applications

| Module | Role | Operational reference |
| --- | --- | --- |
| AGENT | Agent lifecycle and coordination | [README](../../../GEO-INFER-AGENT/README.md) · [guide](geo-infer-agent.md) |
| ANT | Ant-colony, particle-swarm, bee-colony, and stigmergic optimization | [README](../../../GEO-INFER-ANT/README.md) · [guide](geo-infer-ant.md) |
| SIM | Simulation and scenario execution | [README](../../../GEO-INFER-SIM/README.md) · [guide](geo-infer-sim.md) |
| APP | Application and dashboard components | [README](../../../GEO-INFER-APP/README.md) · [guide](geo-infer-app.md) |
| API | API and service integration surfaces | [README](../../../GEO-INFER-API/README.md) · [guide](geo-infer-api.md) |
| ART | Visual and creative geospatial outputs | [README](../../../GEO-INFER-ART/README.md) · [guide](geo-infer-art.md) |
| PLACE | Place-based analysis and visualization | [README](../../../GEO-INFER-PLACE/README.md) · [guide](geo-infer-place.md) |

## Domain modules

AG, BIO, CLIMATE, CIV, ECON, EDU, EMERGENCY, ENERGY, FOREST, HEALTH, LOG,
MARINE, PEP, RISK, TRANSPORT, and WATER provide domain-oriented workflows.
Their operational references are available in the root module directories and
their conceptual pages below.

| Agriculture | Ecology and climate | Society and infrastructure |
| --- | --- | --- |
| [AG](geo-infer-ag.md) | [BIO](geo-infer-bio.md) | [CIV](geo-infer-civ.md) |
| [ENERGY](geo-infer-energy.md) | [CLIMATE](geo-infer-climate.md) | [EDU](geo-infer-edu.md) |
| [FOREST](geo-infer-forest.md) | [MARINE](geo-infer-marine.md) | [EMERGENCY](geo-infer-emergency.md) |
| [WATER](geo-infer-water.md) | [RISK](geo-infer-risk.md) | [HEALTH](geo-infer-health.md) |
|  |  | [LOG](geo-infer-log.md) · [PEP](geo-infer-pep.md) · [TRANSPORT](geo-infer-transport.md) |

## Governance and tooling

COMMS, GIT, INTRA, METAGOV, NORMS, OPS, ORG, REQ, SEC, TEST, and EXAMPLES
provide communication, governance, repository operations, documentation,
security, validation, and cross-module demonstrations.

- [GEO-INFER-TEST](geo-infer-test.md) — executable repository gates.
- [GEO-INFER-INTRA](geo-infer-intra.md) — documentation and knowledge hub.
- [GEO-INFER-EXAMPLES](geo-infer-examples.md) — runnable orchestration examples.
- [GEO-INFER-SEC](geo-infer-sec.md) — security utilities and boundaries.

## Selecting a module

1. Start with the module that owns the data or behavior.
2. Read its root `README.md`, `SKILL.md`, and `tests/README.md`.
3. Confirm the public import path from `src/<package>/__init__.py`.
4. Run the module gate before changing a cross-module consumer.
5. Update the relevant conceptual page only when the source-backed behavior is
   implemented and validated.
