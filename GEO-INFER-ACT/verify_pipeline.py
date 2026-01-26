
import sys
import os
import json
import numpy as np
import logging
from pathlib import Path
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Verification")

def check_uv_environment():
    """Triple check uv-related environment variables and paths."""
    logger.info("--- Checking Environment ---")
    
    # Check if inside a virtualenv
    in_venv = sys.prefix != sys.base_prefix
    logger.info(f"Running inside virtualenv: {in_venv}")
    logger.info(f"Python executable: {sys.executable}")
    
    # Check UV specific marker (often UV sets specific env vars or just manages the venv)
    # We check if uv.lock exists in root
    uv_lock = Path("uv.lock")
    if uv_lock.exists():
        logger.info("uv.lock found.")
    else:
        logger.warning("uv.lock NOT found!")

def run_simulation_with_logging():
    """Run a ClimateModel simulation with full logging enabled."""
    logger.info("--- Running Simulation with Full Logging ---")
    
    from geo_infer_act.models.climate import ClimateModel
    
    output_dir = Path("verification_output")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    # Initialize model with output_dir to trigger analyzer
    # The fix we implemented takes kwargs -> ActiveInferenceModel(..., output_dir=...)
    # ClimateModel passes **config to super, but usually we init it with a config dict
    
    config = {
        'output_dir': str(output_dir)
    }
    
    try:
        model = ClimateModel(config=config)
        logger.info("ClimateModel initialized with analyzer.")
        
        # Run detailed steps
        steps = 5
        for t in range(steps):
            obs = [0, 0] # Normal conditions
            model.step(obs)
            logger.info(f"Step {t+1}/{steps} completed.")
            
        # Export full history
        if model.analyzer:
            model.analyzer.export_full_history()
            model.analyzer.analyze_perception_patterns()
            model.analyzer.analyze_action_selection_patterns()
            model.analyzer.analyze_free_energy_patterns()
            logger.info("Analysis and export completed.")
        else:
            logger.error("Model analyzer was NOT initialized!")
            return False
            
        return output_dir
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def verify_artifacts(output_dir: Path):
    """Verify that all expected logs and data files exist."""
    logger.info("--- Verifying Artifacts ---")
    
    expected_files = [
        output_dir / "data" / "full_history.json",
        output_dir / "analysis" / "perception_analysis.json",
        output_dir / "analysis" / "action_selection_analysis.json",
        output_dir / "analysis" / "free_energy_analysis.json",
        output_dir / "logs" / "analysis.log"
    ]
    
    all_exist = True
    for p in expected_files:
        if p.exists():
            size = p.stat().st_size
            logger.info(f"✅ Found {p.name} ({size} bytes)")
            
            # Deep check for full history
            if p.name == "full_history.json":
                with open(p) as f:
                    data = json.load(f)
                    if len(data) >= 5:
                         logger.info(f"   - Verified {len(data)} steps of deep history recorded.")
                    else:
                         logger.error(f"   - History incomplete: only {len(data)} steps.")
                         all_exist = False
        else:
            logger.error(f"❌ MISSING {p.name}")
            all_exist = False
            
    return all_exist

if __name__ == "__main__":
    check_uv_environment()
    
    out_path = run_simulation_with_logging()
    
    if out_path:
        success = verify_artifacts(out_path)
        if success:
            logger.info("\n>>> VERIFICATION SUCCESSFUL: Full total analysis pipeline confirmed. <<<")
            sys.exit(0)
        else:
            logger.error("\n>>> VERIFICATION FAILED: Missing artifacts. <<<")
            sys.exit(1)
    else:
        logger.error("\n>>> VERIFICATION FAILED: Simulation did not complete. <<<")
        sys.exit(1)
