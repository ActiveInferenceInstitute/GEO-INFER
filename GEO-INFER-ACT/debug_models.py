
import numpy as np
import logging
import traceback
from geo_infer_act.models.climate import ClimateModel
from geo_infer_act.models.urban import UrbanModel

logging.basicConfig(level=logging.DEBUG)

def test_climate():
    print("--- Testing ClimateModel ---")
    try:
        model = ClimateModel()
        print(f"Initialized. Num controls: {model.num_controls}")
        print(f"B shapes: {[b.shape for b in model.generative_model.transition_model]}")
        
        # Test step
        obs = [0, 0]
        beliefs, action = model.step(obs)
        print(f"Step Result: Beliefs={beliefs}, Action={action}")
        
    except Exception as e:
        print(f"ClimateModel Failed: {e}")
        traceback.print_exc()

def test_urban():
    pass

if __name__ == "__main__":
    test_climate()
