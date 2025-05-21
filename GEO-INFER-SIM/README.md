# GEO-INFER-SIM

**Simulation Environments for Geospatial Hypothesis Testing & Policy Evaluation**

## Overview

GEO-INFER-SIM is the **core simulation engine and experimentation workbench** within the GEO-INFER framework. It empowers users to create, run, and analyze simulations of complex geospatial systems to test hypotheses, explore future scenarios, and evaluate the potential impacts of different policies or interventions. By supporting various simulation paradigms, including agent-based modeling (ABM), system dynamics, cellular automata, and digital twin technology, this module provides a versatile platform for understanding and predicting the behavior of ecological, urban, social, and environmental systems across multiple spatial and temporal scales.

## Core Objectives

-   **Hypothesis Testing:** Provide a virtual laboratory to test theories about how geospatial systems function and respond to changes.
-   **Scenario Exploration:** Enable the creation and comparison of multiple future scenarios based on different assumptions or interventions.
-   **Policy Evaluation:** Assess the likely outcomes and trade-offs of various policy options before implementation in the real world.
-   **Behavioral Understanding:** Gain insights into the emergent behavior of complex systems arising from the interactions of individual components or agents.
-   **Decision Support:** Furnish policymakers and stakeholders with quantitative and qualitative evidence to inform decision-making under uncertainty.
-   **Digital Twin Creation:** Facilitate the development of dynamic, data-driven virtual replicas of real-world geospatial assets or systems.

## Key Features

-   **Multi-Paradigm Simulation Support:** Implements and integrates various simulation approaches:
    -   **Agent-Based Models (ABM):** Simulating systems as collections of autonomous, interacting agents (e.g., individuals, households, animals, organizations).
    -   **System Dynamics (SD):** Modeling systems using stocks, flows, and feedback loops to understand aggregate behavior over time.
    -   **Cellular Automata (CA):** Simulating spatial processes based on local rules applied to grid cells (e.g., urban sprawl, fire spread).
    -   **Discrete Event Simulation (DES):** Modeling systems as sequences of events occurring at discrete points in time (e.g., queuing systems, logistics).
    -   **Hybrid Models:** Combining elements from different paradigms to capture diverse aspects of a system.
-   **Digital Twin Technology Foundation:** Tools for creating dynamic virtual representations of real-world systems (e.g., cities, ecosystems, infrastructure networks) that are continuously updated with real-world data, enabling real-time monitoring, prediction, and optimization.
-   **Scenario Management & Analysis:** Robust capabilities for defining, managing, running, and comparing multiple simulation scenarios with varying parameters, inputs, or policy interventions.
-   **Integration with Real-World Data:** Tools for calibrating simulation models using historical data and validating simulation outputs against observed real-world patterns (from GEO-INFER-DATA).
-   **Extensible Model Library:** A collection of pre-built, customizable simulation models for common geospatial applications (e.g., urban growth, disease spread, land use change, ecological succession).
-   **Visualization & Output Analysis:** Integrated tools for visualizing simulation dynamics (2D/3D, temporal animations) and analyzing output data (statistical summaries, sensitivity analysis, uncertainty quantification).
-   **High-Performance Computing (HPC) Support:** Designed for scalability, with options for parallel execution, GPU acceleration, and distributed computing for large and computationally intensive simulations.

## General Simulation Workflow (Conceptual)

```mermaid
graph TD
    subgraph Setup_Phase as "1. Model Setup & Calibration"
        A[Define Research Question / Policy Problem]
        B[Conceptual Model Development]
        C[Select Simulation Paradigm (ABM, SD, CA etc.)]
        D[Gather Input Data (GEO-INFER-DATA)]
        E[Model Implementation (Code/Visual)]
        F[Parameterization & Calibration (using Historical Data)]
        G[Model Validation]
    end

    subgraph Experimentation_Phase as "2. Experimentation & Scenario Analysis"
        H[Define Scenarios / Interventions]
        I[Set Up Simulation Experiments (Batch Runs)]
        J[Run Simulations (GEO-INFER-SIM Engine)]
        K[Collect Simulation Output Data]
    end

    subgraph Analysis_Phase as "3. Output Analysis & Interpretation"
        L[Visualize Simulation Dynamics]
        M[Statistical Analysis of Outputs]
        N[Sensitivity Analysis & Uncertainty Quantification]
        O[Compare Scenarios & Evaluate Outcomes]
        P[Generate Reports & Insights]
        Q[Decision Support / Further Iteration]
    end

    A --> B --> C --> E
    D --> E
    D --> F
    E --> F --> G
    G --> H
    H --> I --> J --> K
    K --> L; K --> M; K --> N; K --> O;
    L --> P; M --> P; N --> P; O --> P;
    P --> Q
    Q --> A %% Iterative process

    classDef simPhase fill:#f0f8ff,stroke:#4682b4,stroke-width:2px;
    class Setup_Phase,Experimentation_Phase,Analysis_Phase simPhase;
```

## Directory Structure
```
GEO-INFER-SIM/
├── config/              # Configuration for simulation runs, model parameters, scenarios
├── docs/                # Detailed documentation, model descriptions, tutorials
├── examples/            # Example simulation scripts and use cases
├── src/                 # Source code
│   └── geo_infer_sim/   # Main Python package
│       ├── api/         # API for controlling simulations and retrieving results
│       ├── core/        # Core simulation engine, schedulers, event handlers
│       ├── models/      # Base classes for agents, environments, specific model implementations
│       ├── paradigms/   # Implementations for ABM, SD, CA, DES logic
│       ├── io/          # Input/output for simulation data, model states
│       ├── analysis/    # Tools for analyzing simulation outputs
│       └── utils/       # Utility functions, visualization helpers
└── tests/               # Unit and integration tests for simulation components
```

## Getting Started

### Prerequisites
- Python 3.9+
- NumPy, SciPy, Pandas, Matplotlib
- Specific libraries depending on paradigm (e.g., Mesa for ABM, PySD for System Dynamics)
- Access to GEO-INFER-DATA for input/calibration data.

### Installation
```bash
# Clone the GEO-INFER repository if you haven't already
# git clone https://github.com/activeinference/GEO-INFER.git
# cd GEO-INFER/GEO-INFER-SIM

pip install -e .
# or poetry install if pyproject.toml is configured
```

### Configuration
Simulation scenarios, model parameters, input data paths, and output locations are typically defined in YAML or JSON configuration files within the `config/` directory or passed as arguments to simulation scripts.
```bash
# cp config/example_urban_growth_scenario.yaml config/my_urban_scenario.yaml
# # Edit my_urban_scenario.yaml
```

### Running a Simulation
Simulations are usually executed via scripts or a command-line interface provided by the module.
```bash
python -m geo_infer_sim.run --config config/my_urban_scenario.yaml
# or
# python examples/run_forest_fire_simulation.py --parameters config/fire_params.json
```

## Simulation Types Supported

GEO-INFER-SIM offers flexibility by supporting various established simulation paradigms:

-   **Agent-Based Models (ABM):** Focuses on individual heterogeneous agents and their local interactions. Excellent for capturing emergent behavior from the bottom up (e.g., pedestrian models, market simulations, epidemiological models).
-   **System Dynamics (SD):** Uses stocks, flows, and feedback loops to model aggregate system behavior over time. Useful for understanding policy impacts in complex systems with delays and non-linearities (e.g., resource management, macroeconomic models).
-   **Cellular Automata (CA):** Models systems as a grid of cells, where each cell's state changes based on local rules and the states of its neighbors. Effective for simulating spatial diffusion, pattern formation, and land-use change.
-   **Discrete Event Simulation (DES):** Represents systems as a sequence of events occurring at specific points in time. Suited for process-oriented modeling, such as logistics, queuing systems, or healthcare workflows.
-   **Hybrid Models:** Combines strengths of different paradigms. For example, an ABM might be used for household decisions, with the aggregate impact fed into an SD model of resource consumption, all within a CA-defined spatial landscape.

## Digital Twin Capabilities

The module provides foundational elements for developing Digital Twins of geospatial systems:

-   **Real-time Data Integration:** Connectors to ingest live data streams (from IoT, sensors, APIs via GEO-INFER-DATA) to keep the digital twin synchronized with its physical counterpart.
-   **Model Calibration & Validation with Historical Data:** Tools to automatically calibrate model parameters using historical observations and validate predictive accuracy.
-   **"What-if" Scenario Generation & Comparison:** Easily define and run alternative scenarios to explore potential futures or the impact of decisions.
-   **Sensitivity Analysis:** Identify which model parameters or input factors have the most significant impact on simulation outcomes.
-   **Uncertainty Quantification:** Propagate uncertainties in input data and model parameters through the simulation to understand the range of possible outcomes.
-   **Interactive Visualization of Simulation Results:** Tools to visualize the state of the digital twin and its predicted evolution in 2D/3D and over time, often integrated with GEO-INFER-APP or GEO-INFER-ART.

## Model Library (Examples)

A library of pre-built or easily adaptable models for common simulation scenarios accelerates development:

-   **Urban Growth & Land Use Change:** Models like SLEUTH, agent-based land market simulations.
-   **Transportation & Mobility Patterns:** ABM for pedestrian/vehicle movement, traffic simulation, public transport optimization.
-   **Ecosystem Dynamics & Biodiversity:** Predator-prey models, species distribution models under climate change, habitat fragmentation effects.
-   **Epidemiological Models:** SEIR/SIR models, agent-based disease spread simulations.
-   **Water Resource Management:** Models for river basin dynamics, irrigation demand, groundwater depletion under different climate and policy scenarios.
-   **Emergency Response & Disaster Scenarios:** Evacuation models, resource allocation during disasters, wildfire spread simulations.
-   **Agricultural Systems:** Crop growth models, farmer decision-making ABMs.

## Integration with Other Modules

GEO-INFER-SIM is a highly integrative module:

-   **GEO-INFER-DATA:** Provides essential input data (initial conditions, parameters, historical series for calibration/validation) for simulations and stores simulation outputs.
-   **GEO-INFER-SPACE:** Defines the spatial context (grids, networks, terrain) in which simulations occur. Spatial analysis tools from SPACE can be used on simulation inputs/outputs.
-   **GEO-INFER-TIME:** Manages the temporal aspects of simulations, including event scheduling, time-stepping, and analysis of time-series outputs.
-   **GEO-INFER-ACT & GEO-INFER-AGENT:** These modules can provide the behavioral logic for agents within ABMs run in SIM. For instance, ACT agents making decisions based on free energy minimization can be simulated in SIM environments.
-   **GEO-INFER-AI:** Machine learning models from AI can be used to create surrogate models for computationally expensive simulations, learn agent behaviors from data, or analyze complex simulation outputs.
-   **GEO-INFER-NORMS & GEO-INFER-REQ:** Policy scenarios, rules, and constraints defined in NORMS or as requirements in REQ can be translated into simulation parameters or agent behaviors to test their impacts.
-   **GEO-INFER-APP & GEO-INFER-ART:** Provide frontends for configuring simulations, visualizing results, and creating interactive digital twin interfaces or artistic representations of simulation dynamics.

## Performance Optimization

Strategies for handling computationally intensive simulations include:

-   **Parallel Processing:** Utilizing multi-core CPUs for running multiple simulation instances or parallelizing computations within a single simulation.
-   **GPU Acceleration:** Offloading suitable computations (e.g., CA updates, some ABM interactions) to GPUs.
-   **Distributed Computing Options:** Support for running large-scale simulations across clusters (e.g., using Dask, Spark, or MPI integrations).
-   **Model Abstraction & Simplification Techniques:** Methods for reducing model complexity while preserving key behaviors.
-   **Surrogate Modeling (Emulation):** Training machine learning models (from GEO-INFER-AI) to approximate the input-output behavior of complex simulations, allowing for faster exploration of parameter space.

## Contributing

Contributions are highly encouraged:
-   Developing new simulation models or extending the model library.
-   Implementing support for new simulation paradigms or engines.
-   Enhancing performance optimization features.
-   Creating tools for advanced simulation output analysis and visualization.
-   Adding new example use cases and tutorials.

Follow the contribution guidelines in the main GEO-INFER documentation (`CONTRIBUTING.md`) and any specific guidelines in `GEO-INFER-SIM/docs/CONTRIBUTING_SIM.md` (to be created).

## License

This module is licensed under the Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0). Please see the `LICENSE` file in the root of the GEO-INFER repository for full details. 