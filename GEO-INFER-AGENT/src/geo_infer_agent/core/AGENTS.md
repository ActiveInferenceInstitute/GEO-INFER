

# Agent: core

#

# Scope

This directory contains core agent framework components for the module. It provides 7 classes and 1 function implementing base agent functionality, active inference agents, BDI agents, and agent registry management. 

## Classes and Functions 

### ActiveInferenceConfig Configuration for active inference models. 

### GenerativeModel Neural network-based generative model for active inference. **Methods**: - `likelihood(state: torch.Tensor) -> Normal`: Compute the likelihood distribution p(o|s). - `transition(state: torch.Tensor, action: torch.Tensor) -> Normal`: Compute the transition distribution p(s'|s,a). - `prior(batch_size: int) -> Normal`: Compute the prior distribution p(s). - `policy(state: torch.Tensor) -> Categorical`: Compute the policy distribution p(a|s). - `encode(observation: torch.Tensor, steps: int) -> Normal`: Infer the state given an observation (recognition/perception). - `expected_free_energy(state: torch.Tensor, action: torch.Tensor) -> torch.Tensor`: Compute the expected free energy for a state-action pair. - `plan_actions(current_state: torch.Tensor) -> List[torch.Tensor]`: Plan a sequence of actions to minimize expected free energy. - `select_action(state: torch.Tensor) -> torch.Tensor`: Select next action based on current state by minimizing expected free energy. - `update(states: torch.Tensor, actions: torch.Tensor, next_states: torch.Tensor, observations: torch.Tensor) -> Dict[str, float]`: Update the generative model based on experience. 

### ActiveInferenceAgent Agent that uses active inference for perception and action selection. **Methods**: - `perceive(observation: np.ndarray) -> np.ndarray`: Infer the current state given an observation. - `plan(state: np.ndarray) -> List[np.ndarray]`: Plan a sequence of actions given the current state. - `act(state: np.ndarray) -> np.ndarray`: Select an action given the current state. - `add_experience(state: np.ndarray, action: np.ndarray, next_state: np.ndarray, observation: np.ndarray) -> None`: Add an experience to the buffer. - `learn(batch_size: Optional[int]) -> Dict[str, float]`: Update the generative model based on collected experience. - `save(filepath: str) -> None`: Save the agent's model. - `load(filepath: str) -> None`: Load the agent's model. - `clear_experience() -> None`: Clear the experience buffer. 

### AgentState Represents the internal state of an agent. **Methods**: - `update_belief(key: str, value: Any) -> None`: Update a belief with information. - `add_desire(desire: Dict[str, Any]) -> None`: Add a goal/desire for the agent. - `set_intention(intention: Dict[str, Any]) -> None`: Set current intention/plan. - `add_to_memory(item: Dict[str, Any]) -> None`: Add an item to agent's memory. - `get_top_desire() -> Optional[Dict[str, Any]]`: Get the highest priority desire. - `to_dict() -> Dict[str, Any]`: Convert state to dictionary for serialization. - `from_dict(cls, data: Dict[str, Any]) -> 'AgentState'`: Create state from dictionary. 

### BaseAgent Base agent class that all specialized agents inherit from. **Methods**: - `stop() -> None`: Stop the agent execution. - `update_beliefs(perception: Dict[str, Any]) -> None`: Update agent's beliefs based on perception. - `save_state(filepath: Optional[str]) -> str`: Save agent state to file. - `load_state(cls, filepath: str, config: Optional[Dict]) -> 'BaseAgent'`: Create agent from saved state. 

### ExampleAgent Example agent implementation for demonstration. **Methods**: - `update_beliefs(perception: Dict[str, Any]) -> None`: Update beliefs based on perception. 

### AgentRegistry Registry for managing agent instances. **Methods**: - `remove_agent(agent_id: str) -> None`: Remove an agent from the registry. - `get_agent(agent_id: str) -> BaseAgent`: Get an agent instance. - `get_agent_info(agent_id: str) -> Dict[str, Any]`: Get information about an agent. - `is_agent_running(agent_id: str) -> bool`: Check if an agent is running. - `list_agents() -> List[Dict[str, Any]]`: List all registered agents. - `list_agent_types() -> Dict[str, str]`: List all available agent types. 

### simple_env `simple_env(state, action)` Simple environment for testing. 

## Capabilities 
- **7 classes** for core functionality 
- **1 functions** for utility operations 

## Integration 
- **Location**: `GEO-INFER-AGENT/src/geo_infer_agent/core` 
- **Type**: Directory Node 