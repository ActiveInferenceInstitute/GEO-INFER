
import pytest
import numpy as np
from geo_infer_act.models.climate import ClimateModel
from geo_infer_act.models.ecological import EcologicalModel
from geo_infer_act.models.urban import UrbanModel

class TestRealActiveInferenceModels:
    
    def test_climate_model_initialization_and_step(self):
        """Test ClimateModel initialization and stepping."""
        model = ClimateModel()
        
        # Check matrices exist
        assert hasattr(model.generative_model, 'observation_model')
        assert hasattr(model.generative_model, 'transition_model')
        
        # Run a step
        # Observations: [Thermometer, CO2_Sensor]
        obs = [0, 0] # Normal, Low
        beliefs, action = model.step(obs)
        
        assert beliefs is not None
        assert 'states' in beliefs or isinstance(beliefs, (list, np.ndarray))
        assert action is not None

    def test_ecological_model_initialization_and_step(self):
        """Test EcologicalModel initialization and stepping."""
        model = EcologicalModel()
        
        # Check components
        assert model.num_states == [3, 2]
        
        # Run a step
        # Observations: [Food, Threat]
        obs = [2, 0] # Abundant Food, No Threat
        result = model.step(obs)
        
        # Step returns dict with 'beliefs', 'action', 'observation'
        assert isinstance(result, dict)
        assert 'beliefs' in result
        assert 'action' in result

    def test_urban_model_simulation(self):
        """Test UrbanModel multi-agent simulation."""
        model = UrbanModel(n_agents=2, n_locations=3)
        
        # Run simulation
        history = model.run_simulation(n_steps=5)
        
        assert len(history) == 5
        assert 'states' in history[0]
        assert len(history[0]['states']) == 2 # 2 agents
        
        # Check agent movement
        # Locations should be valid ints
        loc = history[0]['states'][0]['location']
        assert isinstance(loc, (int, np.integer))
        assert 0 <= loc < 3

if __name__ == "__main__":
    pytest.main([__file__])
