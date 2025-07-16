import unittest
import numpy as np
from geo_infer_act.utils.integration import ModernToolsIntegration, integrate_rxinfer, integrate_bayeux, integrate_pymdp

class TestModernToolsIntegration(unittest.TestCase):
    """Tests for ModernToolsIntegration."""

    def setUp(self):
        """Set up test fixtures."""
        self.integration = ModernToolsIntegration()

    def test_check_available_tools(self):
        """Test checking available tools."""
        tools = self.integration._check_available_tools()
        self.assertIsInstance(tools, dict)
        self.assertIn('pymdp', tools)  # Assume at least one is checked

    # Add conditional tests for each integration method
    def test_create_pymdp_agent(self):
        """Test pymdp integration if available."""
        if self.integration.available_tools.get('pymdp', False):
            try:
                from pymdp.agent import Agent  # Correct import
                # Test code
            except ImportError as e:
                self.skipTest(f'pymdp import failed: {e}')
        else:
            self.skipTest('pymdp not available')

    # Similar for other tools like rxinfer, bayeux, etc.

if __name__ == '__main__':
    unittest.main() 