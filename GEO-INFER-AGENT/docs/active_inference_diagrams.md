# Active Inference Module Diagrams

This document provides visual representations of the Active Inference architecture and workflows.

## Class Diagram

```mermaid
classDiagram
    class BaseAgent {
        <<abstract>>
        +agent_id: str
        +config: Dict
        +initialize() async
        +perceive() async
        +decide() async
        +act(action) async
        +shutdown() async
    }
    
    class AgentState {
        <<abstract>>
        +to_dict() Dict
        +from_dict(data) AgentState
    }
    
    class GenerativeModel {
        +state_dimensions: int
        +observation_dimensions: int
        +control_dimensions: int
        +learning_rate: float
        +A: ndarray
        +B: ndarray
        +C: ndarray
        +D: ndarray
        +current_state_beliefs: ndarray
        +history: List
        +update_likelihood(observation, state)
        +update_transition(prev_state, current_state, action)
        +update_preferences(preferred_observations)
        +infer_state(observation) ndarray
        +predict_next_state(current_state, action) ndarray
        +expected_free_energy(state_belief, action, planning_horizon) float
        +select_action(current_state_belief, planning_horizon) int
        +to_dict() Dict
        +from_dict(data) GenerativeModel
    }
    
    class ActiveInferenceState {
        +state_dimensions: int
        +observation_dimensions: int
        +control_dimensions: int
        +generative_model: GenerativeModel
        +observation_history: List
        +action_history: List
        +update_with_observation(observation) ndarray
        +record_action(action, reward)
        +update_preferences(preferred_obs)
        +select_action(planning_horizon) int
        +to_dict() Dict
        +from_dict(data) ActiveInferenceState
    }
    
    class ActiveInferenceAgent {
        +state: ActiveInferenceState
        +_action_handlers: Dict
        +_perception_handlers: Dict
        +initialize() async
        +perceive() async
        +_process_observations(observations)
        +decide() async
        +_convert_action_index_to_action(action_idx) Dict
        +act(action) async
        +shutdown() async
        +_register_default_action_handlers()
        +_register_default_perception_handlers()
        +_handle_wait_action(agent, action) async
        +_handle_update_preferences(agent, action) async
        +_handle_query_model(agent, action) async
        +_handle_sensor_perceptions(agent, perception)
        +_save_model(path)
        +_load_model(path)
    }
    
    BaseAgent <|-- ActiveInferenceAgent
    AgentState <|-- ActiveInferenceState
    ActiveInferenceAgent o-- ActiveInferenceState
    ActiveInferenceState o-- GenerativeModel
```

## Active Inference Process

```mermaid
sequenceDiagram
    participant E as Environment
    participant A as ActiveInferenceAgent
    participant S as ActiveInferenceState
    participant G as GenerativeModel
    
    A->>A: initialize()
    A->>S: Create ActiveInferenceState
    S->>G: Create GenerativeModel
    
    loop Agent Lifecycle
        A->>E: perceive()
        E-->>A: observations
        A->>S: update_with_observation(observations)
        S->>G: infer_state(observations)
        G-->>S: posterior state beliefs
        
        A->>A: decide()
        A->>S: select_action()
        S->>G: select_action(state_beliefs)
        G->>G: expected_free_energy for each action
        G-->>S: selected action
        S-->>A: action index
        A->>A: convert action index to action
        
        A->>E: act(action)
        E-->>A: action result
        A->>S: record_action(action, reward)
        
        alt Positive Reward
            A->>S: update_preferences(observation)
            S->>G: update_preferences(observation)
        end
        
        alt New Transition Observed
            S->>G: update_transition(prev_state, current_state, action)
        end
        
        alt New Observation
            S->>G: update_likelihood(observation, state)
        end
    end
    
    A->>A: shutdown()
```

## Free Energy Minimization

```mermaid
flowchart TD
    A[Active Inference Agent] -->|Perceives| B[Sensory Observations]
    B -->|Updates| C[Generative Model]
    C -->|Infers| D[Hidden States]
    D -->|Predicts| E[Expected Free Energy]
    E -->|Minimizes| F[Action Selection]
    F -->|Executes| G[Actions]
    G -->|Changes| H[Environment]
    H -->|Produces| B
    
    subgraph "State Inference (Perception)"
        B
        C
        D
    end
    
    subgraph "Action Selection (Decision)"
        E
        F
    end
    
    C -.->|Updates Model Parameters| C
```

## Geospatial Integration

```mermaid
flowchart LR
    A[Geospatial Data] -->|Encoding| B[Observation Vector]
    B -->|Update| C[Active Inference Agent]
    C -->|Decision| D[Action Selection]
    D -->|Execution| E[Geospatial Action]
    E -->|Feedback| F[Environment Change]
    F -->|New Data| A
    
    subgraph "Observation Processing"
        G[Land Cover] -->|Encode| B
        H[Points of Interest] -->|Distance| B
        I[Elevation] -->|Normalize| B
    end
    
    subgraph "Action Types"
        D --> J[Movement]
        D --> K[Sampling]
        D --> L[Analysis]
    end
```

## Model Components Interaction

```mermaid
stateDiagram-v2
    [*] --> Initialize
    
    state "Active Inference Agent" as Agent {
        [*] --> Perceive
        Perceive --> Decide
        Decide --> Act
        Act --> Perceive
        
        state "Generative Model" as Model {
            [*] --> Prior
            Prior --> Likelihood
            Likelihood --> Posterior
            Posterior --> FreeEnergy
            FreeEnergy --> PolicySelection
            PolicySelection --> ActionExecution
            ActionExecution --> ModelUpdate
            ModelUpdate --> Prior
        }
    }
    
    Initialize --> Agent
    Agent --> [*] : Shutdown
``` 