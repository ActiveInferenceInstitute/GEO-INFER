# Agent
: paradigms ## Scope
 This directory contains paradigms components for the module. It provides 6 classes and 1 functions. ## Classes
 and Functions ### Agen
t
 Base agent class for agent-based models. **Methods**: - `step(time: float, environment: Dict[str, Any]) -> None`: Execute one step of agent behavior. - `interact(other_agent: 'Agent', time: float) -> None`: Interact with another agent. ### AgentBasedMode
l
 Agent-Based Model for geospatial simulations. **Methods**: - `add_agent(agent: Agent) -> None`: Add an agent to the model. - `remove_agent(agent_id: str) -> bool`: Remove an agent from the model. - `get_agent(agent_id: str) -> Optional[Agent]`: Get an agent by ID. - `find_neighbors(agent: Agent, radius: float, max_neighbors: Optional[int]) -> List[Agent]`: Find neighboring agents within a radius. - `step(time_step: float) -> None`: Execute one simulation step for all agents. - `get_state() -> Dict[str, Any]`: Get current model state. ### CellularAutomat
a
 Cellular Automata model for geospatial simulations. **Methods**: - `get_neighbors(row: int, col: int, neighborhood: str) -> List[Tuple[int, int]]`: Get neighbor cell coordinates. - `apply_rule(rule_func: Callable[[int, List[int]], int], neighborhood: str) -> None`: Apply a transition rule to all cells. - `step(rule_func: Optional[Callable[[int, List[int]], int]], neighborhood: str) -> None`: Execute one simulation step. - `get_state() -> Dict[str, Any]`: Get current model state. - `reset(initial_states: Optional[np.ndarray]) -> None`: Reset the model to initial state. ### Stoc
k
 Represents a stock (accumulation) in system dynamics. ### Flo
w
 Represents a flow (rate of change) in system dynamics. ### SystemDynamicsMode
l
 System Dynamics model for geospatial simulations. **Methods**: - `add_stock(name: str, initial_value: float, min_value: Optional[float], max_value: Optional[float]) -> None`: Add a stock to the model. - `add_flow(name: str, source_stock: Optional[str], target_stock: Optional[str], rate_function: Optional[Callable[[Dict[str, float]], float]], constant_rate: Optional[float]) -> None`: Add a flow to the model. - `calculate_flow_rate(flow: Flow, stock_values: Dict[str, float]) -> float`: Calculate flow rate for a flow. - `step(time_step: float) -> None`: Execute one simulation step. - `get_state() -> Dict[str, Any]`: Get current model state. - `reset() -> None`: Reset the model to initial state. ### game_of_life_rul
e
 `game_of_life_rule(current: int, neighbors: List[int]) -> int` ## Capabilities
 - **6 classes** for core functionality - **1 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-SIM/src/geo_infer_sim/paradigms` - **Type**: Directory Node 