## GEO-INFER-SIM — Simulation Environments

GEO-INFER-SIM provides advanced simulation environments for geospatial hypothesis testing, policy evaluation, and scenario analysis using agent-based modeling and system dynamics (per its `README.md`). The package `geo_infer_sim` contains `core/`, `paradigms/`, `scenarios/`, and a `module_simulations.py` integration surface, at approximately 4,393 lines of Python — sized to serve as the framework's experimental sandbox rather than a monolithic simulator.

The public interface, verified from `__init__.py`, exports nine symbols spanning three modeling paradigms plus coordination. Agent-based modeling: `AgentBasedModel` and `Agent` for individual-level spatial agents. System dynamics: `SystemDynamicsModel` for aggregate stock-and-flow simulation. Cellular automata: `CellularAutomata` for lattice-based spatial dynamics. These run under `SimulationEngine` configured by `SimulationConfig`, while `ScenarioManager` organizes scenario definitions and `ModuleSimulations` with `ModuleSimulationConfig` expose per-module simulation entry points so other GEO-INFER modules can be exercised inside simulated worlds.

The test census counts 7 test files with 19 test classes and 72 test functions, covering engine stepping, each paradigm's dynamics, and scenario management.

Under the root README's Module Themes, SIM belongs to Bayesian & Active Inference alongside BAYES, SPM, MATH, COG, and ACT. Its role there is the generative counterfactual: where SPM detects significant patterns in observed data and MATH supplies the estimators, SIM generates synthetic worlds in which hypotheses and policies can be evaluated before touching real geographies — the forward-model complement to the framework's observational modules.
