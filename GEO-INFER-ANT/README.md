# GEO-INFER-ANT

**Active Inference in Networked Topologies: Complex Adaptive Systems Modeling**

## Overview

GEO-INFER-ANT is a specialized module for modeling and simulating complex adaptive systems (CAS) inspired by swarm intelligence and stigmergy. It uses Active Inference from GEO-INFER-ACT for agent behavior and studies emergent collective dynamics in spatial and temporal contexts.

### Documentation
- Module page: ../GEO-INFER-INTRA/docs/modules/geo-infer-ant.md
- Modules index: ../GEO-INFER-INTRA/docs/modules/index.md

## Core Concepts

-   **Complex Adaptive Systems (CAS):** Systems composed of many interacting components whose collective behavior is difficult to predict from the behavior of individual components. They exhibit properties like emergence, self-organization, and adaptation.
-   **Swarm Intelligence:** The collective problem-solving behavior of decentralized, self-organized systems, typically consisting of a population of simple agents interacting locally with one another and with their environment.
-   **Stigmergy:** A mechanism of indirect coordination between agents, where the trace left in the environment by an action stimulates the performance of a subsequent action by the same or a different agent (e.g., pheromone trails in ants).
-   **Emergence:** The arising of novel and coherent structures, patterns, and properties during the process of self-organization in complex systems.
-   **Self-Organization:** A process where some form of overall order or coordination arises out of the local interactions between smaller, initially disordered components of a system, without external control.
-   **Active Inference for Agents:** Individual agents within the ANT module are often modeled as active inference agents, making decisions to minimize their free energy (see GEO-INFER-ACT).

## Key Features

-   **Multi-Scale "Ant" Entity Modeling:** Design and simulation of individual agents ("ants" or other entities) with specific sensory capabilities, internal states (beliefs, preferences modeled via active inference), and action repertoires operating within a geospatial environment.
-   **Movement Data Integration & Analysis:** Tools for integrating empirical movement data (e.g., GPS tracks of animals, pedestrian flows) to calibrate and validate agent-based models or to serve as input for collective behavior analysis.
-   **Configurable Simulation Environments:** Flexible environments allowing definition of spatial layouts (using GEO-INFER-SPACE), resource distributions, obstacles, and dynamic changes (using GEO-INFER-TIME) that influence agent behavior.
-   **Stigmergic Interaction Mechanisms:** Implementation of various forms of indirect communication, such as digital pheromones, shared knowledge maps, or environmental markers that agents can deposit, sense, and react to.
-   **Ant-Inspired & Bio-Inspired Algorithms:** Implementation of algorithms like Ant Colony Optimization (ACO), Particle Swarm Optimization (PSO), Artificial Bee Colony (ABC), and other swarm intelligence techniques for geospatial optimization problems (e.g., routing, task allocation, area coverage).
-   **Collective Behavior Analysis Tools:** Metrics and visualization techniques to study emergent patterns, such as flocking, schooling, trail formation, task specialization, and collective decision-making.
-   **Network-Based Interactions:** Modeling interactions between agents based on various network topologies (e.g., spatial proximity networks, social networks, communication networks).

## Conceptual Model of ANT System Dynamics

```mermaid
graph TD
    subgraph Environment_Layer as "Geospatial Environment (SPACE, TIME)"
        RE[Resources]
        OBS[Obstacles]
        PATHS[Pathways]
        STIG[Stigmergic Traces (Pheromones, Markers)]
    end

    subgraph Agent_Layer as "Population of Active Inference Agents (ANTs)"
        A1[Agent 1 (ActInf)]
        A2[Agent 2 (ActInf)]
        An[Agent n (ActInf)]
    end

    subgraph Collective_Behavior as "Emergent Collective Behavior"
        FORAGE[Collective Foraging]
        NAV[Optimized Navigation]
        TASK_ALLOC[Dynamic Task Allocation]
        SENSE[Distributed Sensing]
    end

    %% Agent-Environment Interactions
    A1 -- "Senses/Acts" --> RE
    A1 -- "Senses/Acts" --> OBS
    A1 -- "Senses/Acts" --> PATHS
    A1 -- "Deposits/Senses" --> STIG
    A2 -- "Senses/Acts" --> RE
    A2 -- "Senses/Acts" --> OBS
    A2 -- "Senses/Acts" --> PATHS
    A2 -- "Deposits/Senses" --> STIG
    An -- "Senses/Acts" --> RE
    An -- "Senses/Acts" --> OBS
    An -- "Senses/Acts" --> PATHS
    An -- "Deposits/Senses" --> STIG

    %% Agent-Agent Interactions (often indirect via STIG or direct if modeled)
    A1 <-->|Local Interactions| A2
    A2 <-->|Local Interactions| An

    %% Emergence
    Agent_Layer -- "Local Interactions Lead To" --> Collective_Behavior
    STIG -- "Mediates" --> Collective_Behavior

    classDef antComponent fill:#ffd9b3,stroke:#ff8c00,stroke-width:2px;
    class Agent_Layer,Collective_Behavior antComponent;
```

## Directory Structure
```
GEO-INFER-ANT/
├── config/              # Configuration files for simulations, agent parameters
├── docs/                # Detailed documentation, theoretical background, algorithm descriptions
├── examples/            # Example simulations and applications (e.g., ACO, swarm models)
├── src/                 # Source code
│   └── geo_infer_ant/   # Main Python package
│       ├── api/         # Interfaces for controlling simulations and querying agent states
│       ├── core/        # Core simulation engine, agent logic, stigmergy mechanisms
│       ├── models/      # Definitions for agent types, environment features, collective states
│       ├── algorithms/  # Implementations of specific bio-inspired algorithms (ACO, PSO etc.)
│       └── utils/       # Utility functions, visualization tools for swarms and environments
└── tests/               # Unit and integration tests
```

## Getting Started

### Prerequisites
- Python 3.9+
- NumPy, SciPy, Matplotlib
- NetworkX (for graph-based interactions)
- Integration with GEO-INFER-ACT, GEO-INFER-SPACE, GEO-INFER-TIME.

### Installation
```bash
pip install -e ./GEO-INFER-ANT
```

### Configuration
Simulation parameters, agent characteristics (e.g., sensory range, pheromone deposition rates), and environment details are typically configured via YAML files in `config/` or directly in experiment scripts.
```bash
# cp config/example_aco_config.yaml config/my_aco_experiment.yaml
# # Edit my_aco_experiment.yaml
```

### Running Examples
```bash
python examples/ant_colony_optimization_routing.py
python examples/swarm_foraging_simulation.py
```

## Theoretical Foundations

GEO-INFER-ANT builds upon and integrates concepts from:

-   **Active Inference (GEO-INFER-ACT):** Provides the principled basis for individual agent perception, learning, and decision-making to minimize free energy.
-   **Complexity Science:** Explores how interactions among many components lead to emergent, system-level properties not present in the components themselves.
-   **Swarm Intelligence:** Studies collective computation and problem-solving in decentralized systems (e.g., ACO, PSO, flocking/schooling models).
-   **Multi-Agent Systems (MAS):** Focuses on systems composed of multiple autonomous, interacting intelligent agents.
-   **Network Theory:** Analyzes the structure of connections between agents and how this influences information flow and collective dynamics.
-   **Statistical Mechanics & Synergetics:** Mathematical frameworks for understanding phase transitions and pattern formation in multi-component systems.

## Modeling Capabilities

The module provides tools for constructing and analyzing models of:

-   **Ant Colony Optimization (ACO) for Spatial Problems:** Finding optimal paths in networks (e.g., road networks, pipeline layouts), a VRP (Vehicle Routing Problem) variant solutions.
-   **Agent-Based Simulations of Movement & Foraging:** Simulating how groups of animals or autonomous robots explore, search for, and exploit resources in a geospatial environment.
-   **Stigmergic Communication & Construction:** Modeling how agents indirectly coordinate through modifications of their shared environment (e.g., trail formation, nest building).
-   **Distributed Sensing & Collective Intelligence:** Simulating how a swarm of simple sensors or agents can collectively map an area, detect anomalies, or make robust group decisions.
-   **Adaptive Foraging & Task Allocation Strategies:** Investigating how agent populations dynamically allocate themselves to different tasks or resource patches in response to changing environmental conditions.
-   **Opinion Dynamics & Consensus Formation:** Modeling how local interactions and information exchange lead to global patterns of agreement or polarization in a spatially distributed population.

## Algorithms

Key algorithms implemented or supported by the module include:

-   **Ant Colony Optimization (ACO) variants:** For pathfinding, routing, and combinatorial optimization problems.
-   **Particle Swarm Optimization (PSO):** For continuous optimization problems in geospatial contexts.
-   **Artificial Bee Colony (ABC) & other foraging algorithms.**
-   **Boids Algorithm (Flocking/Schooling):** For simulating basic swarm movement and cohesion.
-   **Stigmergic Pattern Formation Algorithms:** E.g., digital pheromone evaporation and diffusion models.
-   **Distributed Task Allocation Algorithms:** E.g., threshold-based models, market-based approaches.
-   **Self-Organizing Maps (SOMs) / Growing Neural Gas (GNG):** For adaptive geospatial clustering and topology learning, sometimes inspired by neural self-organization.

## Integration with Other Modules

GEO-INFER-ANT interacts closely with:

-   **GEO-INFER-ACT:** Provides the core active inference framework that can drive the behavior of individual "ant" agents, enabling them to learn and adapt based on minimizing free energy.
-   **GEO-INFER-SPACE:** Defines the spatial environment (grids, networks, continuous spaces, terrain features) in which ANT agents operate and interact. Agent perception and movement are constrained and influenced by SPACE.
-   **GEO-INFER-TIME:** Manages the temporal evolution of the simulation environment and agent states. Dynamic resource availability, environmental changes, and agent lifecycles are handled via TIME.
-   **GEO-INFER-SIM:** ANT can be considered a specialized type of simulation within the broader SIM module. SIM might provide higher-level orchestration or visualization tools for ANT simulations.
-   **GEO-INFER-AI:** Machine learning techniques from AI can be used to analyze the emergent behavior of ANT systems, or to train more sophisticated policies for individual agents.
-   **GEO-INFER-VIS (if it exists, or GEO-INFER-ART/APP for viz):** For visualizing agent movements, pheromone trails, emergent structures, and simulation dynamics.

## Applications

-   **Optimizing Resource Discovery & Exploitation in Ecological Systems:** Modeling animal foraging, pollination dynamics, or predator-prey interactions.
-   **Simulating Human Movement Patterns & Crowd Dynamics:** Understanding pedestrian flows in urban areas, evacuation scenarios, or the spread of information/disease.
-   **Designing Resilient & Adaptive Infrastructure Networks:** E.g., self-healing communication networks, adaptive traffic routing systems.
-   **Robotics & Autonomous Systems:** Developing control strategies for swarms of autonomous robots for tasks like exploration, mapping, search and rescue, or distributed construction.
-   **Logistics & Transportation Network Optimization:** Finding efficient routes for delivery fleets, managing supply chains with decentralized agents.
-   **Understanding Information Flow & Collective Decision-Making in Social Systems:** Modeling opinion dynamics, innovation diffusion, or the emergence of social norms.

## Contributing

Contributions are welcome and can include:
-   Developing new agent behavioral models (especially those based on active inference).
-   Implementing novel swarm intelligence algorithms or stigmergic mechanisms.
-   Creating new simulation environments or scenarios for geospatial CAS.
-   Adding tools for analyzing and visualizing collective behavior.
-   Integrating with empirical data on animal or human collective movement.

Follow the contribution guidelines in the main GEO-INFER documentation (`CONTRIBUTING.md`) and any specific guidelines in `GEO-INFER-ANT/docs/CONTRIBUTING_ANT.md` (to be created).

## License

This module is licensed under the Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0). Please see the `LICENSE` file in the root of the GEO-INFER repository for full details. 