"""
Unit tests for BDI agent interface.
"""

import unittest
from unittest.mock import MagicMock, patch
import json

from geo_infer_app.models.agent_interface import AgentType, AgentState
from geo_infer_app.models.interfaces.bdi_interface import BDIAgentInterface

class TestBDIAgentInterface(unittest.TestCase):
    """Test cases for the BDI agent interface."""
    
    def setUp(self):
        """Set up the test environment."""
        self.interface = BDIAgentInterface()
        
        # Create a test agent
        self.agent_config = {
            "name": "Test BDI Agent",
            "beliefs": {
                "location": {"lat": 40.7128, "lng": -74.0060},
                "weather": "sunny"
            },
            "desires": ["explore", "collect_data"],
            "initial_location": {"lat": 40.7128, "lng": -74.0060}
        }
        
        self.agent_id = self.interface.create_agent(AgentType.BDI, self.agent_config)
    
    def test_create_agent(self):
        """Test creating a BDI agent."""
        # Verify the agent was created
        self.assertIsNotNone(self.agent_id)
        self.assertTrue(len(self.agent_id) > 0)
        
        # Create another agent
        another_agent_id = self.interface.create_agent(AgentType.BDI, {
            "name": "Another Agent"
        })
        
        # Verify it's a different agent
        self.assertNotEqual(self.agent_id, another_agent_id)
        
        # Verify error when creating a non-BDI agent
        with self.assertRaises(ValueError):
            self.interface.create_agent(AgentType.RL, {})
    
    def test_get_agent_state(self):
        """Test retrieving agent state."""
        state = self.interface.get_agent_state(self.agent_id)
        
        # Verify the state is correct
        self.assertIsInstance(state, AgentState)
        self.assertEqual(state.agent_id, self.agent_id)
        self.assertEqual(state.agent_type, AgentType.BDI)
        self.assertEqual(state.status, "idle")
        self.assertEqual(state.location, self.agent_config["initial_location"])
        self.assertEqual(state.beliefs, self.agent_config["beliefs"])
        self.assertEqual(state.goals, self.agent_config["desires"])
        self.assertIsNotNone(state.last_updated)
        self.assertIsNotNone(state.metadata)
        self.assertIn("intentions", state.metadata)
        
        # Verify error for invalid agent ID
        with self.assertRaises(ValueError):
            self.interface.get_agent_state("invalid-id")
    
    def test_list_agents(self):
        """Test listing agents."""
        agents = self.interface.list_agents()
        
        # Verify the agent list
        self.assertIsInstance(agents, list)
        self.assertTrue(len(agents) > 0)
        
        # Find our test agent
        test_agent = next((a for a in agents if a["id"] == self.agent_id), None)
        self.assertIsNotNone(test_agent)
        self.assertEqual(test_agent["name"], self.agent_config["name"])
        self.assertEqual(test_agent["type"], "bdi")
        self.assertEqual(test_agent["location"], self.agent_config["initial_location"])
        
        # Test filtering by status
        idle_agents = self.interface.list_agents({"status": "idle"})
        self.assertTrue(len(idle_agents) > 0)
        
        active_agents = self.interface.list_agents({"status": "active"})
        self.assertEqual(len(active_agents), 0)
        
        # Test filtering by location
        nearby_agents = self.interface.list_agents({
            "location": {
                "center": {"lat": 40.7128, "lng": -74.0060},
                "radius": 10
            }
        })
        self.assertTrue(len(nearby_agents) > 0)
        
        far_agents = self.interface.list_agents({
            "location": {
                "center": {"lat": 0, "lng": 0},
                "radius": 0.1
            }
        })
        self.assertEqual(len(far_agents), 0)
    
    def test_send_command(self):
        """Test sending commands to an agent."""
        # Test adding a belief
        response = self.interface.send_command(self.agent_id, "add_belief", {
            "belief": {"temperature": 25}
        })
        self.assertTrue(response["success"])
        
        # Verify the belief was added
        state = self.interface.get_agent_state(self.agent_id)
        self.assertIn("temperature", state.beliefs)
        self.assertEqual(state.beliefs["temperature"], 25)
        
        # Test adding a desire
        response = self.interface.send_command(self.agent_id, "add_desire", {
            "desire": "go_home"
        })
        self.assertTrue(response["success"])
        
        # Verify the desire was added
        state = self.interface.get_agent_state(self.agent_id)
        self.assertIn("go_home", state.goals)
        
        # Test deliberation
        response = self.interface.send_command(self.agent_id, "deliberate", {})
        self.assertTrue(response["success"])
        
        # Verify the intention was added
        state = self.interface.get_agent_state(self.agent_id)
        self.assertIn("go_home", state.metadata["intentions"])
        
        # Test execution
        response = self.interface.send_command(self.agent_id, "execute", {})
        self.assertTrue(response["success"])
        
        # Test moving
        new_location = {"lat": 41.0, "lng": -75.0}
        response = self.interface.send_command(self.agent_id, "move", {
            "location": new_location
        })
        self.assertTrue(response["success"])
        
        # Verify the location was updated
        state = self.interface.get_agent_state(self.agent_id)
        self.assertEqual(state.location, new_location)
        
        # Test invalid command
        with self.assertRaises(ValueError):
            self.interface.send_command(self.agent_id, "invalid_command", {})
        
        # Test invalid agent ID
        with self.assertRaises(ValueError):
            self.interface.send_command("invalid-id", "add_belief", {})
    
    def test_event_handlers(self):
        """Test event handlers."""
        # Create a mock event handler
        mock_handler = MagicMock()
        
        # Register the handler
        self.interface.register_event_handler("agent_updated", mock_handler)
        
        # Send a command to trigger the event
        self.interface.send_command(self.agent_id, "move", {
            "location": {"lat": 42.0, "lng": -76.0}
        })
        
        # Verify the handler was called
        mock_handler.assert_called_once()
        call_args = mock_handler.call_args[0][0]
        self.assertEqual(call_args["agent_id"], self.agent_id)
        self.assertIsInstance(call_args["state"], AgentState)

if __name__ == "__main__":
    unittest.main() 