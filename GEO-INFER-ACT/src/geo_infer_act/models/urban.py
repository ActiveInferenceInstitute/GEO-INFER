"""
Urban planning model using active inference.
"""
from typing import Dict, List, Optional, Any, Tuple
import numpy as np

from geo_infer_act.models.base import ActiveInferenceModel
from geo_infer_act.api.interface import ActiveInferenceInterface


class UrbanModel(ActiveInferenceModel):
    """
    Urban planning model using active inference.
    
    This model represents urban development and planning processes
    through active inference, considering multiple agents (stakeholders)
    and their interactions within an urban environment.
    """
    
    def __init__(self, 
                config: Optional[Dict[str, Any]] = None, 
                n_agents: int = 3,
                n_resources: int = 4,
                n_locations: int = 5,
                planning_horizon: int = 10):
        """
        Initialize the urban planning model.
        
        Args:
            config: Configuration dictionary
            n_agents: Number of agents (stakeholders)
            n_resources: Number of resource types
            n_locations: Number of spatial locations
            planning_horizon: Planning time horizon
        """
        super().__init__(config)
        
        self.n_agents = n_agents
        self.n_resources = n_resources
        self.n_locations = n_locations
        self.planning_horizon = planning_horizon
        
        # Model components
        self.agent_models = []
        self.resource_distribution = np.zeros((n_resources, n_locations))
        self.location_connectivity = np.zeros((n_locations, n_locations))
        self.agent_preferences = np.zeros((n_agents, n_resources))
        
        # Initialize model components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize model components."""
        # Create agent models
        for i in range(self.n_agents):
            agent_id = f"agent_{i}"
            agent_model = self._create_agent_model(agent_id)
            self.agent_models.append(agent_model)
            
        # Initialize resource distribution (random for now)
        self.resource_distribution = np.random.rand(self.n_resources, self.n_locations)
        
        # Initialize location connectivity (random for now)
        self.location_connectivity = np.random.rand(self.n_locations, self.n_locations)
        # Make connectivity symmetric
        self.location_connectivity = (self.location_connectivity + 
                                    self.location_connectivity.T) / 2
        # Set diagonal to 1 (self-connectivity)
        np.fill_diagonal(self.location_connectivity, 1.0)
        
        # Initialize agent preferences (random for now)
        self.agent_preferences = np.random.rand(self.n_agents, self.n_resources)
        # Normalize preferences
        self.agent_preferences = self.agent_preferences / np.sum(
            self.agent_preferences, axis=1, keepdims=True
        )
    
    def _create_agent_model(self, agent_id: str) -> Dict[str, Any]:
        """
        Create an active inference model for an agent.
        
        Args:
            agent_id: Identifier for the agent
            
        Returns:
            Agent model
        """
        # Create a new interface for this agent
        ai_interface = ActiveInferenceInterface()
        
        # Create a categorical model for the agent
        model_parameters = {
            "state_dim": self.n_locations * self.n_resources,  # Combined state space
            "obs_dim": self.n_locations + self.n_resources,    # Observations
            "prior_precision": 1.0
        }
        
        ai_interface.create_model(
            model_id=agent_id,
            model_type="categorical",
            parameters=model_parameters
        )
        
        # Return the agent model
        return {
            "id": agent_id,
            "interface": ai_interface,
            "location": np.random.randint(0, self.n_locations),  # Random initial location
            "resources": np.zeros(self.n_resources),  # Initial resources
            "policy_history": []
        }
    
    def step(self, actions: Optional[List[Dict[str, Any]]] = None) -> Tuple[Dict[str, Any], bool]:
        """
        Advance the urban model by one step.
        
        Args:
            actions: Optional list of actions for each agent
            
        Returns:
            Tuple of (state, done)
        """
        # If no actions provided, select actions for each agent
        if actions is None:
            actions = self._select_agent_actions()
        
        # Apply actions and update environment
        self._apply_actions(actions)
        
        # Update agent beliefs based on new observations
        self._update_agent_beliefs()
        
        # Return current state and whether simulation is complete
        current_state = self._get_current_state()
        is_done = self._check_termination()
        
        return current_state, is_done
    
    def _select_agent_actions(self) -> List[Dict[str, Any]]:
        """
        Select actions for all agents using active inference.
        
        Returns:
            List of actions for each agent
        """
        actions = []
        
        for agent in self.agent_models:
            # Get policy from agent's model
            policy_result = agent["interface"].select_policy(agent["id"])
            
            # Convert policy to action
            action = self._policy_to_action(policy_result, agent)
            
            # Store policy for later analysis
            agent["policy_history"].append(policy_result)
            
            actions.append(action)
        
        return actions
    
    def _policy_to_action(self, policy_result: Dict[str, Any], 
                         agent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert policy to concrete action.
        
        Args:
            policy_result: Policy selection result
            agent: Agent model
            
        Returns:
            Action dictionary
        """
        # Extract policy from result
        policy = policy_result["policy"]
        
        # For simplicity, assume policy directly maps to action
        # In a more complex implementation, we would decode the policy
        # to specific urban planning actions
        
        # Example action: move to a new location or allocate resources
        action_type = np.random.choice(["move", "allocate"])
        
        if action_type == "move":
            # Move to new location
            current_loc = agent["location"]
            # Choose connected locations with probability based on connectivity
            probs = self.location_connectivity[current_loc]
            new_loc = np.random.choice(self.n_locations, p=probs/np.sum(probs))
            
            return {
                "agent_id": agent["id"],
                "type": "move",
                "from_location": current_loc,
                "to_location": new_loc
            }
        else:
            # Allocate resources
            resource_idx = np.random.choice(self.n_resources)
            amount = np.random.rand() * 0.1  # Small random amount
            
            return {
                "agent_id": agent["id"],
                "type": "allocate",
                "resource_idx": resource_idx,
                "location": agent["location"],
                "amount": amount
            }
    
    def _apply_actions(self, actions: List[Dict[str, Any]]) -> None:
        """
        Apply actions to update environment state.
        
        Args:
            actions: List of actions for each agent
        """
        for action in actions:
            agent_id = action["agent_id"]
            agent_idx = int(agent_id.split("_")[1])  # Extract index from ID
            
            if action["type"] == "move":
                # Update agent location
                self.agent_models[agent_idx]["location"] = action["to_location"]
            
            elif action["type"] == "allocate":
                # Update resource distribution
                location = action["location"]
                resource_idx = action["resource_idx"]
                amount = action["amount"]
                
                # Increase resource at location
                self.resource_distribution[resource_idx, location] += amount
                
                # Ensure resource constraints
                self.resource_distribution = np.clip(self.resource_distribution, 0, 1)
    
    def _update_agent_beliefs(self) -> None:
        """Update agents' beliefs based on new observations."""
        for agent_idx, agent in enumerate(self.agent_models):
            # Get observations for this agent
            observations = self._get_agent_observations(agent)
            
            # Update beliefs
            agent["interface"].update_beliefs(
                agent["id"], {"observations": observations}
            )
    
    def _get_agent_observations(self, agent: Dict[str, Any]) -> np.ndarray:
        """
        Get observations for an agent.
        
        Args:
            agent: Agent model
            
        Returns:
            Observation vector
        """
        location = agent["location"]
        
        # Location-based observations (one-hot encoding of location)
        loc_obs = np.zeros(self.n_locations)
        loc_obs[location] = 1
        
        # Resource observations (resources available at current location)
        res_obs = self.resource_distribution[:, location]
        
        # Combine observations
        return np.concatenate([loc_obs, res_obs])
    
    def _get_current_state(self) -> Dict[str, Any]:
        """
        Get the current state of the urban model.
        
        Returns:
            Current state dictionary
        """
        return {
            "resource_distribution": self.resource_distribution.copy(),
            "agent_locations": [agent["location"] for agent in self.agent_models],
            "agent_resources": [agent["resources"].copy() for agent in self.agent_models]
        }
    
    def _check_termination(self) -> bool:
        """
        Check if simulation should terminate.
        
        Returns:
            True if simulation should terminate, False otherwise
        """
        # For simplicity, never terminate in this implementation
        return False
    
    def run_simulation(self, n_steps: int = 20) -> List[Dict[str, Any]]:
        """
        Run the urban simulation for a number of steps.
        
        Args:
            n_steps: Number of steps to simulate
            
        Returns:
            History of states
        """
        state_history = []
        
        for step in range(n_steps):
            state, done = self.step()
            state_history.append(state)
            
            if done:
                break
                
        return state_history
    
    def evaluate_plan(self, state_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Evaluate the quality of an urban plan.
        
        Args:
            state_history: History of states
            
        Returns:
            Evaluation metrics
        """
        # Example metrics for urban planning quality
        final_state = state_history[-1]
        
        # Resource distribution evenness
        resource_evenness = -np.sum(
            np.std(self.resource_distribution, axis=1)
        ) / self.n_resources
        
        # Resource accessibility (based on agent locations and connectivity)
        resource_accessibility = 0.0
        for agent_idx, location in enumerate(final_state["agent_locations"]):
            # Sum accessibility from this location to all resources
            for loc in range(self.n_locations):
                connectivity = self.location_connectivity[location, loc]
                resources = np.sum(self.resource_distribution[:, loc])
                resource_accessibility += connectivity * resources
                
        resource_accessibility /= self.n_agents
        
        # Agent satisfaction (based on preferences)
        agent_satisfaction = 0.0
        for agent_idx, agent in enumerate(self.agent_models):
            location = agent["location"]
            preferences = self.agent_preferences[agent_idx]
            resources = self.resource_distribution[:, location]
            
            # Compute dot product of preferences and available resources
            satisfaction = np.dot(preferences, resources)
            agent_satisfaction += satisfaction
            
        agent_satisfaction /= self.n_agents
        
        return {
            "resource_evenness": resource_evenness,
            "resource_accessibility": resource_accessibility,
            "agent_satisfaction": agent_satisfaction,
            "overall_score": resource_evenness + resource_accessibility + agent_satisfaction
        } 