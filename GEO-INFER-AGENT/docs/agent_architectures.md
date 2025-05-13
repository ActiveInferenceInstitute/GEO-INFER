# GEO-INFER-AGENT Architectures

This document provides an overview of the agent architectures implemented in the GEO-INFER-AGENT module.

## Table of Contents

1. [Overview](#overview)
2. [Common Architecture](#common-architecture)
3. [BDI Agent Architecture](#bdi-agent-architecture)
4. [Active Inference Agent Architecture](#active-inference-agent-architecture)
5. [Reinforcement Learning Agent Architecture](#reinforcement-learning-agent-architecture)
6. [Rule-Based Agent Architecture](#rule-based-agent-architecture)
7. [Hybrid Agent Architecture](#hybrid-agent-architecture)
8. [Integration with GEO-INFER-APP](#integration-with-geo-infer-app)

## Overview

GEO-INFER-AGENT provides several agent architectures for building intelligent geospatial agents:

- **BDI (Belief-Desire-Intention)**: Models agents based on beliefs about the world, desires (goals), and intentions (plans)
- **Active Inference**: Based on the free energy principle, agents perceive and act to minimize surprise
- **Reinforcement Learning**: Agents learn optimal behavior through trial and error
- **Rule-Based**: Simple condition-action rules for reactive behavior
- **Hybrid**: Combines multiple architectures to leverage the strengths of each approach

## Common Architecture

All agent implementations share a common base architecture:

```mermaid
classDiagram
    class BaseAgent {
        +id: str
        +config: Dict
        +state: AgentState
        +sensors: Dict
        +action_handlers: Dict
        +perception_handlers: Dict
        +initialize() async
        +perceive() async
        +decide() async
        +act(action) async
        +shutdown() async
        +register_sensor()
        +register_action_handler()
        +register_perception_handler()
    }
    
    class AgentState {
        +agent_id: str
        +created_at: datetime
        +last_updated: datetime
        +to_dict()
        +from_dict()
    }
    
    BaseAgent *-- AgentState : contains
```

The agent lifecycle follows this pattern:

```mermaid
sequenceDiagram
    participant Environment
    participant Agent
    participant Sensors
    participant ActionHandlers
    
    Environment->>Agent: initialize()
    loop Agent Lifecycle
        Agent->>Sensors: perceive()
        Sensors-->>Agent: perceptions
        Agent->>Agent: decide()
        Agent-->>Agent: selected action
        Agent->>ActionHandlers: act(action)
        ActionHandlers-->>Environment: effects
        Environment-->>ActionHandlers: result
        ActionHandlers-->>Agent: action result
    end
    Environment->>Agent: shutdown()
```

## BDI Agent Architecture

The Belief-Desire-Intention architecture models agents in terms of:
- **Beliefs**: What the agent knows about the world
- **Desires**: Goals the agent wants to achieve
- **Intentions**: Plans the agent has committed to

```mermaid
classDiagram
    class BDIAgent {
        +state: BDIState
        +perceive() async
        +decide() async
        +act(action) async
    }
    
    class BDIState {
        +beliefs: Dict[str, Belief]
        +desires: Dict[str, Desire]
        +intentions: List[Plan]
        +current_intention: Plan
        +add_belief()
        +update_belief()
        +add_desire()
        +add_intention()
        +get_current_intention()
    }
    
    class Belief {
        +name: str
        +value: Any
        +confidence: float
        +timestamp: datetime
        +metadata: Dict
        +update()
    }
    
    class Desire {
        +name: str
        +description: str
        +priority: float
        +deadline: datetime
        +conditions: Dict
        +achieved: bool
        +set_achieved()
        +is_expired()
    }
    
    class Plan {
        +name: str
        +desire_name: str
        +actions: List[Dict]
        +context_conditions: Dict
        +current_action_index: int
        +complete: bool
        +successful: bool
        +next_action()
        +advance()
        +mark_complete()
    }
    
    BDIAgent *-- BDIState
    BDIState *-- Belief
    BDIState *-- Desire
    BDIState *-- Plan
```

BDI Agent Decision Flow:

```mermaid
flowchart TD
    A[Perceive Environment] --> B[Update Beliefs]
    B --> C[Select Applicable Desires]
    C --> D{Has Current Intention?}
    D -- Yes --> E[Is Intention Still Valid?]
    D -- No --> F[Select Highest Priority Desire]
    E -- Yes --> G[Get Next Action from Plan]
    E -- No --> F
    F --> H[Find Plan for Desire]
    H --> I[Set as Current Intention]
    I --> G
    G --> J[Execute Action]
```

## Active Inference Agent Architecture

The Active Inference architecture is based on the free energy principle:
- Agents maintain a generative model of the world
- Actions are selected to minimize expected free energy
- Learning occurs by updating the model based on observations

```mermaid
classDiagram
    class ActiveInferenceAgent {
        +state: ActiveInferenceState
        +planning_horizon: int
        +perceive() async
        +decide() async
        +act(action) async
    }
    
    class ActiveInferenceState {
        +model: GenerativeModel
        +observation_history: List
        +state_history: List
        +action_history: List
        +current_observation: ndarray
        +current_state_belief: ndarray
        +update_with_observation()
        +record_action()
        +update_preferences()
        +select_action()
    }
    
    class GenerativeModel {
        +state_dimensions: int
        +observation_dimensions: int
        +control_dimensions: int
        +A: ndarray  %% Likelihood mapping
        +B: ndarray  %% Transition dynamics
        +C: ndarray  %% Preferences
        +D: ndarray  %% Prior beliefs
        +update_likelihood()
        +update_transition()
        +update_preferences()
        +infer_state()
        +predict_next_state()
        +expected_free_energy()
        +select_action()
    }
    
    ActiveInferenceAgent *-- ActiveInferenceState
    ActiveInferenceState *-- GenerativeModel
```

Active Inference Decision Flow:

```mermaid
flowchart TD
    A[Perceive Observation] --> B[Update Generative Model]
    B --> C[Infer Current State]
    C --> D[For Each Possible Action]
    D --> E[Calculate Expected Free Energy]
    E --> F[Select Action with Minimum EFE]
    F --> G[Execute Action]
    G --> H[Observe Result]
    H --> I[Update Model with Experience]
    I --> A
```

## Reinforcement Learning Agent Architecture

The Reinforcement Learning architecture:
- Agents learn from experience through rewards
- Q-learning maintains a table of state-action values
- Experience replay helps with efficient learning

```mermaid
classDiagram
    class RLAgent {
        +state: RLState
        +train_frequency: int
        +perceive() async
        +decide() async
        +act(action) async
    }
    
    class RLState {
        +q_table: QTable
        +replay_buffer: ReplayBuffer
        +learning_rate: float
        +discount_factor: float
        +epsilon: float
        +current_state: Any
        +select_action()
        +update_q_values()
        +record_episode_reward()
        +train_from_buffer()
    }
    
    class QTable {
        +q_table: ndarray
        +state_size: int
        +action_size: int
        +get_value()
        +update_value()
        +get_best_action()
    }
    
    class ReplayBuffer {
        +buffer: deque
        +capacity: int
        +add()
        +sample()
        +size()
    }
    
    class Experience {
        +state: Any
        +action: int
        +reward: float
        +next_state: Any
        +done: bool
    }
    
    RLAgent *-- RLState
    RLState *-- QTable
    RLState *-- ReplayBuffer
    ReplayBuffer *-- Experience
```

Reinforcement Learning Decision Flow:

```mermaid
flowchart TD
    A[Perceive State] --> B[Select Action]
    B --> C{Explore or Exploit?}
    C -- Explore --> D[Random Action]
    C -- Exploit --> E[Best Known Action]
    D --> F[Execute Action]
    E --> F
    F --> G[Observe Reward & Next State]
    G --> H[Store Experience]
    H --> I[Update Q-Values]
    I --> J[Periodically Train from Buffer]
    J --> A
```

## Rule-Based Agent Architecture

The Rule-Based architecture:
- Simple condition-action rules
- Rules have priorities for conflict resolution
- Fast, reactive behavior

```mermaid
classDiagram
    class RuleBasedAgent {
        +state: RuleBasedState
        +perceive() async
        +decide() async
        +act(action) async
    }
    
    class RuleBasedState {
        +rule_set: RuleSet
        +facts: Dict
        +execution_history: List
        +add_rule()
        +remove_rule()
        +update_fact()
        +get_fact()
        +find_matching_rules()
        +record_execution()
    }
    
    class RuleSet {
        +rules: Dict[str, Rule]
        +add_rule()
        +remove_rule()
        +get_rule()
        +enable_rule()
        +disable_rule()
        +find_matching_rules()
    }
    
    class Rule {
        +id: str
        +condition: Union[Dict, Callable, str]
        +action: Dict
        +priority: int
        +enabled: bool
        +match_count: int
        +matches()
    }
    
    RuleBasedAgent *-- RuleBasedState
    RuleBasedState *-- RuleSet
    RuleSet *-- Rule
```

Rule-Based Decision Flow:

```mermaid
flowchart TD
    A[Perceive Environment] --> B[Update Facts]
    B --> C[Find Matching Rules]
    C --> D{Any Matches?}
    D -- Yes --> E[Select Highest Priority Rule]
    D -- No --> F[Use Default Action if Available]
    E --> G[Execute Rule's Action]
    F --> G
    G --> H[Update Facts with Result]
    H --> A
```

## Hybrid Agent Architecture

The Hybrid architecture:
- Combines multiple agent types
- Uses policy to select between sub-agents
- Shares information across architectures

```mermaid
classDiagram
    class HybridAgent {
        +state: HybridState
        +perceive() async
        +decide() async
        +act(action) async
    }
    
    class HybridState {
        +context: Dict
        +sub_agents: Dict[str, SubAgentWrapper]
        +decision_history: List
        +update_context()
        +add_sub_agent()
        +get_active_agents()
        +record_decision()
        +record_result()
    }
    
    class SubAgentWrapper {
        +agent_type: str
        +agent: BaseAgent
        +priority: int
        +activation_conditions: Dict
        +is_active: bool
        +decision_count: int
        +successful_decision_count: int
        +check_activation()
        +record_decision()
    }
    
    HybridAgent *-- HybridState
    HybridState *-- SubAgentWrapper
    SubAgentWrapper *-- BaseAgent
```

Hybrid Agent Decision Flow:

```mermaid
flowchart TD
    A[Perceive Environment] --> B[Update Shared Context]
    B --> C[Forward Perceptions to Sub-Agents]
    C --> D[Get Active Sub-Agents]
    D --> E[Collect Decisions from Sub-Agents]
    E --> F[Select Best Decision Using Policy]
    F --> G[Execute Action]
    G --> H[Update Context with Result]
    H --> I[Share Result with Source Sub-Agent]
    I --> A
```

## Integration with GEO-INFER-APP

GEO-INFER-AGENT integrates with GEO-INFER-APP to provide intelligent agent capabilities within the application:

```mermaid
flowchart LR
    subgraph GEO-INFER-APP
        A[UI Components] <--> B[APP Core]
        B <--> C[APP API Client]
    end
    
    subgraph GEO-INFER-AGENT
        D[Agent Manager] <--> E[Agent Instances]
        E <--> F[Agent Models]
        F --- G[BDI]
        F --- H[Active Inference]
        F --- I[RL]
        F --- J[Rule-Based]
        F --- K[Hybrid]
    end
    
    subgraph GEO-INFER-API
        L[API Endpoints]
        M[Data Services]
    end
    
    C <--> D
    E <--> L
```

Agent components can be integrated into the app interface:

```mermaid
classDiagram
    class AgentWidgetComponent {
        +agent: AgentInterface
        +status: string
        +decisions: List
        +initializeAgent()
        +startAgent()
        +stopAgent()
        +sendCommand()
        +displayStatus()
    }
    
    class AgentConfigComponent {
        +agentType: string
        +configOptions: Dict
        +saveConfig()
        +loadConfig()
        +validateConfig()
    }
    
    class AgentMonitorComponent {
        +agents: List[AgentInterface]
        +refreshRate: number
        +updateStats()
        +displayMetrics()
        +showAlerts()
    }
    
    class AgentInterface {
        +id: string
        +status: string
        +initialize()
        +start()
        +stop()
        +sendCommand()
        +getStatus()
    }
    
    AgentWidgetComponent --> AgentInterface
    AgentConfigComponent --> AgentInterface
    AgentMonitorComponent --> AgentInterface
```

The integration architecture for the GEO-INFER-APP uses a bridge pattern:

```mermaid
classDiagram
    class AppAgentBridge {
        +registerAgent()
        +unregisterAgent()
        +executeAgentAction()
        +subscribeToAgentUpdates()
        +getAgentStatus()
    }
    
    class AgentManager {
        +agents: Dict
        +createAgent()
        +destroyAgent()
        +pauseAgent()
        +resumeAgent()
        +dispatchPerception()
    }
    
    class UIAgentController {
        +selectedAgent: string
        +viewMode: string
        +displayMode: string
        +connectToAgent()
        +displayAgentData()
        +handleAgentCommands()
    }
    
    AppAgentBridge --> AgentManager
    UIAgentController --> AppAgentBridge
``` 