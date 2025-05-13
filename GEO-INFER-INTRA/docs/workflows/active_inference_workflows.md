# Active Inference Workflows in Geospatial Contexts

This document details how active inference principles are implemented in workflows across the GEO-INFER framework. These workflows demonstrate the practical application of free energy principles in geospatial analysis and modeling.

## Active Inference Process Overview

The core active inference process follows this general workflow:

```mermaid
flowchart TD
    A[Define Generative Model] --> B[Set Prior Beliefs]
    B --> C[Collect Observations]
    C --> D[Update Beliefs via Variational Inference]
    D --> E[Compute Expected Free Energy]
    E --> F[Select Optimal Policy]
    F --> G[Execute Actions]
    G --> H[Observe Outcomes]
    H --> C
    
    classDef model fill:#bbf,stroke:#333,stroke-width:2px
    classDef perception fill:#dfd,stroke:#333,stroke-width:2px
    classDef action fill:#f9f,stroke:#333,stroke-width:2px
    classDef feedback fill:#ffd,stroke:#333,stroke-width:2px
    
    class A,B model
    class C,D perception
    class E,F,G action
    class H feedback
```

## Spatial Active Inference Workflow

In geospatial contexts, active inference involves spatial components:

```mermaid
flowchart TD
    A[Define Spatial Generative Model] --> B[Set Spatial Priors]
    B --> C[Collect Geospatial Observations]
    C --> D[Update Spatial Beliefs]
    D --> E[Compute Expected Free Energy]
    E --> F[Select Spatial Policy]
    F --> G[Execute Spatial Actions]
    G --> H[Observe Spatial Outcomes]
    H --> C
    
    subgraph "Spatial Components"
        SB[Spatial Boundaries]
        SP[Spatial Patterns]
        SI[Spatial Indices]
        SC[Spatial Coordinates]
    end
    
    A --> SB
    A --> SP
    A --> SI
    A --> SC
    
    SB --> B
    SP --> B
    SI --> C
    SC --> C
    
    classDef model fill:#bbf,stroke:#333,stroke-width:2px
    classDef perception fill:#dfd,stroke:#333,stroke-width:2px
    classDef action fill:#f9f,stroke:#333,stroke-width:2px
    classDef feedback fill:#ffd,stroke:#333,stroke-width:2px
    classDef spatial fill:#f96,stroke:#333,stroke-width:2px
    
    class A,B model
    class C,D perception
    class E,F,G action
    class H feedback
    class SB,SP,SI,SC spatial
```

## Temporal Active Inference Workflow

When incorporating temporal dynamics:

```mermaid
flowchart TD
    A[Define Spatiotemporal Model] --> B[Set Spatiotemporal Priors]
    B --> C[Collect Observations across Time]
    C --> D[Update Beliefs with Temporal Dynamics]
    D --> E[Compute Expected Free Energy over Time]
    E --> F[Select Policy with Temporal Horizon]
    F --> G[Execute Actions with Temporal Effects]
    G --> H[Observe Temporal Outcomes]
    H --> C
    
    subgraph "Temporal Components"
        TM[Temporal Modeling]
        TS[Time Series Analysis]
        FF[Future Forecasting]
        HP[Historical Patterns]
    end
    
    A --> TM
    D --> TS
    E --> FF
    B --> HP
    
    classDef model fill:#bbf,stroke:#333,stroke-width:2px
    classDef perception fill:#dfd,stroke:#333,stroke-width:2px
    classDef action fill:#f9f,stroke:#333,stroke-width:2px
    classDef feedback fill:#ffd,stroke:#333,stroke-width:2px
    classDef temporal fill:#f96,stroke:#333,stroke-width:2px
    
    class A,B model
    class C,D perception
    class E,F,G action
    class H feedback
    class TM,TS,FF,HP temporal
```

## Multi-Scale Active Inference

When working across different spatial scales:

```mermaid
flowchart TD
    A[Define Multi-Scale Generative Model] --> B[Set Hierarchical Priors]
    B --> C[Collect Multi-Scale Observations]
    C --> D[Update Hierarchical Beliefs]
    D --> E[Compute EFE across Scales]
    E --> F[Select Multi-Scale Policy]
    F --> G[Execute Multi-Scale Actions]
    G --> H[Observe Multi-Scale Outcomes]
    H --> C
    
    subgraph "Global Scale"
        GBM[Global Generative Model]
        GBO[Global Observations]
        GBP[Global Policies]
    end
    
    subgraph "Regional Scale"
        RGM[Regional Generative Model]
        RGO[Regional Observations]
        RGP[Regional Policies]
    end
    
    subgraph "Local Scale"
        LCM[Local Generative Model]
        LCO[Local Observations]
        LCP[Local Policies]
    end
    
    GBM --> RGM
    RGM --> LCM
    
    GBO --> B
    RGO --> B
    LCO --> B
    
    GBP --> F
    RGP --> F
    LCP --> F
    
    classDef model fill:#bbf,stroke:#333,stroke-width:2px
    classDef perception fill:#dfd,stroke:#333,stroke-width:2px
    classDef action fill:#f9f,stroke:#333,stroke-width:2px
    classDef feedback fill:#ffd,stroke:#333,stroke-width:2px
    classDef global fill:#f96,stroke:#333,stroke-width:2px
    classDef regional fill:#ddf,stroke:#333,stroke-width:2px
    classDef local fill:#fdb,stroke:#333,stroke-width:2px
    
    class A,B model
    class C,D perception
    class E,F,G action
    class H feedback
    class GBM,GBO,GBP global
    class RGM,RGO,RGP regional
    class LCM,LCO,LCP local
```

## Active Inference Components

The key components in an active inference workflow:

```mermaid
classDiagram
    class GenerativeModel {
        +ObservationModel likelihood
        +StateTransitionModel transition
        +PriorModel prior
        +PreferenceModel preference
        +define_model()
        +calculate_free_energy()
        +calculate_expected_free_energy()
    }
    
    class ObservationModel {
        +calculate_likelihood(state, observation)
        +generate_observation(state)
    }
    
    class StateTransitionModel {
        +calculate_transition(current_state, action)
        +predict_next_state(current_state, action)
    }
    
    class PriorModel {
        +get_prior_distribution()
        +sample_from_prior()
    }
    
    class PreferenceModel {
        +calculate_preference(observation)
        +define_goal_states()
    }
    
    class InferenceEngine {
        +update_beliefs(observation)
        +variational_inference()
        +belief_propagation()
    }
    
    class PolicySelection {
        +evaluate_policies()
        +select_optimal_policy()
        +calculate_expected_free_energy()
    }
    
    class ActionExecution {
        +execute_action(policy)
        +monitor_results()
    }
    
    GenerativeModel *-- ObservationModel
    GenerativeModel *-- StateTransitionModel
    GenerativeModel *-- PriorModel
    GenerativeModel *-- PreferenceModel
    GenerativeModel --> InferenceEngine
    InferenceEngine --> PolicySelection
    PolicySelection --> ActionExecution
    ActionExecution --> GenerativeModel
```

## Geospatial Active Inference Implementation

This diagram shows a concrete implementation in the GEO-INFER framework:

```mermaid
graph TD
    subgraph "GEO-INFER-ACT"
        GM[Generative Model]
        FE[Free Energy Calculator]
        INF[Inference Engine]
        POL[Policy Selector]
    end
    
    subgraph "GEO-INFER-SPACE"
        SPA[Spatial Indexing]
        GEOM[Geometry Engine]
        PROJ[Projection System]
    end
    
    subgraph "GEO-INFER-TIME"
        TIME[Temporal Indexing]
        TS[Time Series]
        PRED[Predictive Models]
    end
    
    subgraph "GEO-INFER-AGENT"
        AGENT[Agent Model]
        ENV[Environment]
        SENS[Sensory System]
        ACT[Action System]
    end
    
    subgraph "Domain Module"
        DOM_GM[Domain Generative Model]
        DOM_DATA[Domain Data]
        DOM_PRIOR[Domain Priors]
        DOM_UTIL[Domain Utilities]
    end
    
    GM --> FE
    FE --> INF
    INF --> POL
    
    DOM_GM --> GM
    DOM_PRIOR --> GM
    
    SPA --> GM
    GEOM --> DOM_GM
    PROJ --> DOM_GM
    
    TIME --> GM
    TS --> DOM_GM
    PRED --> DOM_GM
    
    POL --> AGENT
    AGENT --> SENS
    AGENT --> ACT
    ENV --> SENS
    ACT --> ENV
    
    DOM_DATA --> ENV
    
    classDef act fill:#f9f,stroke:#333,stroke-width:2px
    classDef space fill:#bbf,stroke:#333,stroke-width:2px
    classDef time fill:#dfd,stroke:#333,stroke-width:2px
    classDef agent fill:#ffd,stroke:#333,stroke-width:2px
    classDef domain fill:#f96,stroke:#333,stroke-width:2px
    
    class GM,FE,INF,POL act
    class SPA,GEOM,PROJ space
    class TIME,TS,PRED time
    class AGENT,ENV,SENS,ACT agent
    class DOM_GM,DOM_DATA,DOM_PRIOR,DOM_UTIL domain
```

## Workflow Sequence: Land Use Prediction

Example of a complete active inference workflow for land use prediction:

```mermaid
sequenceDiagram
    participant DATA as GEO-INFER-DATA
    participant SPACE as GEO-INFER-SPACE
    participant TIME as GEO-INFER-TIME
    participant ACT as GEO-INFER-ACT
    participant AGENT as GEO-INFER-AGENT
    participant AG as GEO-INFER-AG
    participant APP as GEO-INFER-APP
    
    DATA->>SPACE: Load land use data
    DATA->>TIME: Load temporal data
    
    SPACE->>ACT: Initialize spatial components
    TIME->>ACT: Initialize temporal dynamics
    
    AG->>ACT: Define agricultural priors
    
    ACT->>AGENT: Setup generative model
    
    AGENT->>AGENT: Define perception model
    AGENT->>AGENT: Define transition model
    AGENT->>AGENT: Define preference model
    
    AGENT->>ACT: Run active inference
    ACT->>AGENT: Update beliefs
    AGENT->>AGENT: Calculate EFE
    AGENT->>AGENT: Select policies
    
    AGENT->>AG: Return land use predictions
    AG->>APP: Visualize predictions
    AG->>DATA: Store results
    
    APP->>AG: User adjusts parameters
    AG->>AGENT: Update parameters
    AGENT->>ACT: Rerun inference
    
    note over AGENT,ACT: Iterative active inference process
```

## Hierarchical Perception

Hierarchical perception across scales in geospatial active inference:

```mermaid
graph TD
    subgraph "Global Perception"
        G_OBS[Global Observations]
        G_INF[Global Inference]
        G_BELIEF[Global Beliefs]
    end
    
    subgraph "Regional Perception"
        R_OBS[Regional Observations]
        R_INF[Regional Inference]
        R_BELIEF[Regional Beliefs]
    end
    
    subgraph "Local Perception"
        L_OBS[Local Observations]
        L_INF[Local Inference]
        L_BELIEF[Local Beliefs]
    end
    
    G_OBS --> G_INF
    G_INF --> G_BELIEF
    
    R_OBS --> R_INF
    R_INF --> R_BELIEF
    
    L_OBS --> L_INF
    L_INF --> L_BELIEF
    
    G_BELIEF --> R_INF
    R_BELIEF --> L_INF
    
    L_BELIEF --> R_INF
    R_BELIEF --> G_INF
    
    classDef global fill:#f9f,stroke:#333,stroke-width:2px
    classDef regional fill:#bbf,stroke:#333,stroke-width:2px
    classDef local fill:#dfd,stroke:#333,stroke-width:2px
    
    class G_OBS,G_INF,G_BELIEF global
    class R_OBS,R_INF,R_BELIEF regional
    class L_OBS,L_INF,L_BELIEF local
```

## Example: Drought Prediction Workflow

A concrete example of an active inference workflow for drought prediction:

```mermaid
flowchart TD
    A[Load Historical Climate Data] --> B[Define Spatiotemporal Model]
    B --> C[Set Prior Beliefs on Climate Patterns]
    C --> D[Incorporate Satellite Observations]
    D --> E[Update Beliefs using Variational Inference]
    E --> F[Compute Expected Free Energy of Climate Scenarios]
    F --> G[Select Optimal Prediction Policy]
    G --> H[Generate Drought Forecasts]
    H --> I[Validate with New Observations]
    I --> J{Accurate?}
    J -->|Yes| K[Finalize Forecast]
    J -->|No| L[Adjust Model Parameters]
    L --> E
    
    subgraph "Data Sources"
        DS1[Satellite Data]
        DS2[Weather Stations]
        DS3[Historical Records]
        DS4[Soil Moisture Sensors]
    end
    
    DS1 --> D
    DS2 --> D
    DS3 --> A
    DS4 --> D
    
    subgraph "Model Components"
        MC1[Precipitation Model]
        MC2[Temperature Model]
        MC3[Soil Moisture Model]
        MC4[Evapotranspiration Model]
    end
    
    MC1 --> B
    MC2 --> B
    MC3 --> B
    MC4 --> B
    
    classDef data fill:#bbf,stroke:#333,stroke-width:2px
    classDef model fill:#dfd,stroke:#333,stroke-width:2px
    classDef inference fill:#f9f,stroke:#333,stroke-width:2px
    classDef output fill:#ffd,stroke:#333,stroke-width:2px
    classDef sources fill:#f96,stroke:#333,stroke-width:2px
    classDef components fill:#fdb,stroke:#333,stroke-width:2px
    
    class A,D data
    class B,C,L model
    class E,F,G inference
    class H,I,J,K output
    class DS1,DS2,DS3,DS4 sources
    class MC1,MC2,MC3,MC4 components
```

## Policy Selection Process

Detailed view of how policies are evaluated and selected in geospatial active inference:

```mermaid
flowchart LR
    subgraph "Policies"
        P1[Policy 1]
        P2[Policy 2]
        P3[Policy 3]
    end
    
    subgraph "Expected Free Energy Components"
        subgraph "Policy 1 EFE"
            P1_EX[Exploration Term]
            P1_EX_VAL[Epistemic Value]
            P1_PR[Preference Term]
            P1_PR_VAL[Pragmatic Value]
        end
        
        subgraph "Policy 2 EFE"
            P2_EX[Exploration Term]
            P2_EX_VAL[Epistemic Value]
            P2_PR[Preference Term]
            P2_PR_VAL[Pragmatic Value]
        end
        
        subgraph "Policy 3 EFE"
            P3_EX[Exploration Term]
            P3_EX_VAL[Epistemic Value]
            P3_PR[Preference Term]
            P3_PR_VAL[Pragmatic Value]
        end
    end
    
    P1_EX --> P1_EX_VAL
    P1_PR --> P1_PR_VAL
    
    P2_EX --> P2_EX_VAL
    P2_PR --> P2_PR_VAL
    
    P3_EX --> P3_EX_VAL
    P3_PR --> P3_PR_VAL
    
    P1 --> P1_EX
    P1 --> P1_PR
    
    P2 --> P2_EX
    P2 --> P2_PR
    
    P3 --> P3_EX
    P3 --> P3_PR
    
    P1_EX_VAL --> EFE1[Total EFE 1]
    P1_PR_VAL --> EFE1
    
    P2_EX_VAL --> EFE2[Total EFE 2]
    P2_PR_VAL --> EFE2
    
    P3_EX_VAL --> EFE3[Total EFE 3]
    P3_PR_VAL --> EFE3
    
    EFE1 --> SEL{Policy Selection}
    EFE2 --> SEL
    EFE3 --> SEL
    
    SEL --> BEST[Best Policy]
    
    classDef policy fill:#bbf,stroke:#333,stroke-width:2px
    classDef term fill:#dfd,stroke:#333,stroke-width:2px
    classDef value fill:#f9f,stroke:#333,stroke-width:2px
    classDef total fill:#ffd,stroke:#333,stroke-width:2px
    classDef selection fill:#f96,stroke:#333,stroke-width:2px
    
    class P1,P2,P3 policy
    class P1_EX,P1_PR,P2_EX,P2_PR,P3_EX,P3_PR term
    class P1_EX_VAL,P1_PR_VAL,P2_EX_VAL,P2_PR_VAL,P3_EX_VAL,P3_PR_VAL value
    class EFE1,EFE2,EFE3 total
    class SEL,BEST selection
```

## Implementation in Codebase

The relationship between the workflow design and actual GEO-INFER code:

```mermaid
graph TD
    subgraph "Workflow Definition"
        WF[Active Inference Workflow]
        STAGES[Workflow Stages]
        PARAMS[Workflow Parameters]
    end
    
    subgraph "Implementation"
        GM_CODE[GenerativeModel Class]
        INF_CODE[InferenceEngine Class]
        POL_CODE[PolicySelector Class]
        AGENT_CODE[Agent Class]
    end
    
    subgraph "Execution"
        CONF[Configuration]
        EXEC[Execution Engine]
        RESULTS[Results Handler]
    end
    
    WF --> STAGES
    STAGES --> PARAMS
    
    STAGES --> GM_CODE
    STAGES --> INF_CODE
    STAGES --> POL_CODE
    STAGES --> AGENT_CODE
    
    PARAMS --> CONF
    
    GM_CODE --> EXEC
    INF_CODE --> EXEC
    POL_CODE --> EXEC
    AGENT_CODE --> EXEC
    CONF --> EXEC
    
    EXEC --> RESULTS
    
    classDef workflow fill:#bbf,stroke:#333,stroke-width:2px
    classDef implementation fill:#f9f,stroke:#333,stroke-width:2px
    classDef execution fill:#dfd,stroke:#333,stroke-width:2px
    
    class WF,STAGES,PARAMS workflow
    class GM_CODE,INF_CODE,POL_CODE,AGENT_CODE implementation
    class CONF,EXEC,RESULTS execution
```

## Key Workflow Templates

The GEO-INFER framework provides several workflow templates for common active inference scenarios in geospatial contexts:

1. **Spatial Belief Updating** - A workflow for updating beliefs about spatial patterns based on new observations
2. **Temporal Forecasting** - A workflow for predicting future states using active inference principles
3. **Multi-Scale Analysis** - A workflow that integrates information across different spatial scales
4. **Agent-Based Simulation** - A workflow for simulating the behavior of multiple agents in a spatial environment
5. **Risk Assessment** - A workflow for assessing risks using active inference to quantify uncertainty
6. **Adaptive Sampling** - A workflow for determining optimal locations for new observations
7. **Intervention Planning** - A workflow for evaluating potential interventions in a spatial system

## Using the Active Inference Workflow Templates

To use these workflow templates:

1. Import the appropriate template from `geo_infer_intra.workflows.templates.active_inference`
2. Configure the template parameters for your specific use case
3. Connect the template to your data sources and sinks
4. Execute the workflow using the workflow engine
5. Analyze and visualize the results

See the [Examples Directory](../examples/workflows/active_inference/) for complete examples of each workflow template. 