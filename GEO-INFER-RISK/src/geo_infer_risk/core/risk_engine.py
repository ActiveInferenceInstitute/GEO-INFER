"""
RiskEngine: The core orchestrator for risk modeling and analysis.

This module provides the RiskEngine class which serves as the main entry point
for running risk analyses, coordinating the interaction between hazard,
vulnerability, and exposure models to generate comprehensive risk metrics.
"""

import logging
import os
import time
from typing import Dict, List, Optional, Union, Any

import numpy as np
import pandas as pd

from geo_infer_risk.core.hazard_model import HazardModel
from geo_infer_risk.core.vulnerability_model import VulnerabilityModel
from geo_infer_risk.core.exposure_model import ExposureModel
from geo_infer_risk.utils.validation import validate_config
from geo_infer_risk.utils.risk_metrics import calculate_aal, calculate_ep_curve


class RiskEngine:
    """
    The main orchestrator for risk analysis, coordinating hazard, vulnerability,
    and exposure models to generate comprehensive risk metrics.
    
    The RiskEngine handles:
    - Configuration management
    - Model initialization and coordination
    - Simulation execution
    - Results aggregation and metrics calculation
    - Output generation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the RiskEngine with the provided configuration.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary for the risk analysis
        """
        self.config = config
        self.logger = self._setup_logging()
        
        # Validate the configuration
        self.config = validate_config(config)
        
        # Initialize model containers
        self.hazard_models = {}
        self.vulnerability_models = {}
        self.exposure_models = {}
        
        # Initialize results containers
        self.event_losses = None
        self.aggregated_metrics = None
        
        # Setup output directory
        self.output_dir = config.get("general", {}).get("output_directory", "./outputs")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.logger.info("RiskEngine initialized successfully")
    
    def _setup_logging(self) -> logging.Logger:
        """
        Set up logging for the RiskEngine.
        
        Returns:
            logging.Logger: Configured logger instance
        """
        log_level = self.config.get("general", {}).get("log_level", "INFO")
        level = getattr(logging, log_level)
        
        logger = logging.getLogger("geo_infer_risk")
        logger.setLevel(level)
        
        # Create console handler if no handlers exist
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            
            # Create formatter
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)
            
            # Add handler to logger
            logger.addHandler(console_handler)
        
        return logger
    
    def load_models(self):
        """
        Load and initialize all models based on the configuration.
        """
        self.logger.info("Loading risk models...")
        
        # Load hazard models
        hazard_config = self.config.get("hazards", {})
        for hazard_type, hazard_params in hazard_config.items():
            if hazard_params.get("enabled", False):
                self.logger.info(f"Loading {hazard_type} hazard model")
                
                # Dynamic model loading would go here
                # For now, we'll use a placeholder
                self.hazard_models[hazard_type] = HazardModel(
                    hazard_type=hazard_type,
                    params=hazard_params
                )
        
        # Load vulnerability models
        vuln_config = self.config.get("vulnerability", {})
        for vuln_type, vuln_params in vuln_config.items():
            if vuln_params.get("enabled", False):
                self.logger.info(f"Loading {vuln_type} vulnerability model")
                
                self.vulnerability_models[vuln_type] = VulnerabilityModel(
                    vulnerability_type=vuln_type,
                    params=vuln_params
                )
        
        # Load exposure models
        exposure_config = self.config.get("exposure", {})
        for exp_type, exp_params in exposure_config.items():
            if exp_params.get("enabled", False):
                self.logger.info(f"Loading {exp_type} exposure model")
                
                self.exposure_models[exp_type] = ExposureModel(
                    exposure_type=exp_type,
                    params=exp_params
                )
        
        self.logger.info(
            f"Models loaded: {len(self.hazard_models)} hazard, "
            f"{len(self.vulnerability_models)} vulnerability, "
            f"{len(self.exposure_models)} exposure"
        )
    
    def run_analysis(self):
        """
        Execute the full risk analysis workflow.
        
        Returns:
            Dict: Results dictionary containing all risk metrics
        """
        start_time = time.time()
        self.logger.info("Starting risk analysis...")
        
        # Ensure models are loaded
        if not self.hazard_models:
            self.load_models()
        
        # Run the event simulation
        self._run_event_simulation()
        
        # Calculate aggregate metrics
        self._calculate_metrics()
        
        # Generate outputs
        results = self._format_results()
        
        elapsed_time = time.time() - start_time
        self.logger.info(f"Risk analysis completed in {elapsed_time:.2f} seconds")
        
        return results
    
    def _run_event_simulation(self):
        """
        Run the event-based simulation across all models.
        """
        self.logger.info("Running event simulation...")
        
        # Get simulation parameters
        monte_carlo_iterations = self.config.get("risk_model", {}).get(
            "monte_carlo_iterations", 1000
        )
        random_seed = self.config.get("risk_model", {}).get("random_seed", 42)
        
        # Set random seed for reproducibility
        np.random.seed(random_seed)
        
        # Initialize event loss container
        self.event_losses = {
            "event_id": [],
            "hazard_type": [],
            "exposure_type": [],
            "loss": []
        }
        
        # For each hazard model, generate events
        for hazard_type, hazard_model in self.hazard_models.items():
            self.logger.info(f"Generating events for {hazard_type}")
            
            # Generate hazard events
            events = hazard_model.generate_events(monte_carlo_iterations)
            
            # For each event, calculate losses for all exposure types
            for event in events:
                for exp_type, exposure_model in self.exposure_models.items():
                    # Get exposure at risk
                    exposed_assets = exposure_model.get_exposure_for_event(event)
                    
                    # For each exposed asset, calculate vulnerability and damage
                    for asset in exposed_assets:
                        # Find appropriate vulnerability model
                        vulnerability = self.vulnerability_models.get(
                            asset.get("type"), 
                            self.vulnerability_models.get("building")
                        )
                        
                        # Calculate damage ratio
                        damage_ratio = vulnerability.calculate_damage(
                            hazard_type=hazard_type,
                            hazard_intensity=event.get("intensity_at_asset", 0),
                            asset_properties=asset
                        )
                        
                        # Calculate loss
                        loss = damage_ratio * asset.get("value", 0)
                        
                        # Store result
                        self.event_losses["event_id"].append(event.get("id"))
                        self.event_losses["hazard_type"].append(hazard_type)
                        self.event_losses["exposure_type"].append(exp_type)
                        self.event_losses["loss"].append(loss)
        
        # Convert to DataFrame for easier analysis
        self.event_losses = pd.DataFrame(self.event_losses)
        self.logger.info(f"Completed event simulation with {len(self.event_losses)} individual loss calculations")
    
    def _calculate_metrics(self):
        """
        Calculate aggregate risk metrics from the event simulation results.
        """
        self.logger.info("Calculating aggregate risk metrics...")
        
        # Initialize metrics container
        self.aggregated_metrics = {}
        
        # Convert event_losses to event loss table
        event_loss_table = self.event_losses.groupby(["event_id", "hazard_type"]).sum().reset_index()
        
        # Calculate Average Annual Loss (AAL)
        aal = calculate_aal(event_loss_table)
        self.aggregated_metrics["aal"] = aal
        
        # Calculate Exceedance Probability (EP) curve
        exceedance_probs = self.config.get("output", {}).get(
            "exceedance_probabilities", 
            [0.5, 0.2, 0.1, 0.04, 0.02, 0.01, 0.004, 0.002]
        )
        ep_curve = calculate_ep_curve(event_loss_table, exceedance_probs)
        self.aggregated_metrics["ep_curve"] = ep_curve
        
        # Add additional metrics as needed
        # ...
        
        self.logger.info("Risk metrics calculation completed")
    
    def _format_results(self) -> Dict:
        """
        Format the risk analysis results for output.
        
        Returns:
            Dict: Formatted results dictionary
        """
        self.logger.info("Formatting results...")
        
        results = {
            "summary": {
                "aal": self.aggregated_metrics.get("aal", {}).copy(),
                "return_period_losses": self.aggregated_metrics.get("ep_curve", {}).copy(),
            },
            "details": {
                "event_losses": self.event_losses.to_dict(orient="records") 
                if self.event_losses is not None else []
            },
            "metadata": {
                "run_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "config_summary": {
                    "hazards": list(self.hazard_models.keys()),
                    "vulnerability": list(self.vulnerability_models.keys()),
                    "exposure": list(self.exposure_models.keys()),
                    "monte_carlo_iterations": self.config.get("risk_model", {}).get(
                        "monte_carlo_iterations", 1000
                    )
                }
            }
        }
        
        return results
    
    def save_results(self, filename: Optional[str] = None):
        """
        Save the risk analysis results to disk.
        
        Args:
            filename (str, optional): Custom filename for results. If None,
                                     a default timestamped name will be used.
        """
        if self.aggregated_metrics is None:
            self.logger.warning("No results to save. Run analysis first.")
            return
        
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"risk_analysis_results_{timestamp}.json"
        
        # Ensure the file has .json extension
        if not filename.endswith(".json"):
            filename += ".json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Format results for saving
        results = self._format_results()
        
        # Convert DataFrame to records for serialization
        if isinstance(results.get("details", {}).get("event_losses"), pd.DataFrame):
            results["details"]["event_losses"] = results["details"]["event_losses"].to_dict(orient="records")
        
        # Convert numpy types to Python native types for JSON serialization
        import json
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super(NumpyEncoder, self).default(obj)
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(results, f, cls=NumpyEncoder, indent=2)
        
        self.logger.info(f"Results saved to {filepath}")
        
        return filepath
    
    def plot_results(self, plot_type: str = "ep_curve", **kwargs):
        """
        Generate plots from the risk analysis results.
        
        Args:
            plot_type (str): Type of plot to generate ('ep_curve', 'aal_breakdown', etc.)
            **kwargs: Additional parameters for the specific plot type
            
        Returns:
            matplotlib.Figure: Figure object for the generated plot
        """
        try:
            import matplotlib.pyplot as plt
            
            if self.aggregated_metrics is None:
                self.logger.warning("No results to plot. Run analysis first.")
                return None
            
            if plot_type == "ep_curve":
                # Create EP curve plot
                fig, ax = plt.subplots(figsize=(10, 6))
                
                ep_data = self.aggregated_metrics.get("ep_curve", {})
                if not ep_data:
                    self.logger.warning("No EP curve data available")
                    return None
                
                # Extract data
                return_periods = [1/p for p in ep_data.get("exceedance_probability", [])]
                losses = ep_data.get("loss", [])
                
                # Plot
                ax.semilogx(return_periods, losses, 'o-', linewidth=2)
                ax.set_xlabel("Return Period (years)")
                ax.set_ylabel("Loss")
                ax.set_title("Exceedance Probability Curve")
                ax.grid(True, which="both", linestyle="--", linewidth=0.5)
                
                # Add annotations
                for rp, loss in zip(return_periods, losses):
                    ax.annotate(
                        f"{int(rp)}yr: {loss:.1f}M",
                        xy=(rp, loss),
                        xytext=(5, 5),
                        textcoords="offset points"
                    )
                
                plt.tight_layout()
                
                # Save if requested
                if kwargs.get("save", False):
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = kwargs.get("filename", f"ep_curve_{timestamp}.png")
                    filepath = os.path.join(self.output_dir, filename)
                    plt.savefig(filepath, dpi=300)
                    self.logger.info(f"Plot saved to {filepath}")
                
                return fig
            
            elif plot_type == "aal_breakdown":
                # Create AAL breakdown plot
                fig, ax = plt.subplots(figsize=(10, 6))
                
                aal_data = self.aggregated_metrics.get("aal", {})
                if not aal_data:
                    self.logger.warning("No AAL data available")
                    return None
                
                # Extract data by hazard type
                hazards = aal_data.get("by_hazard", {})
                
                if not hazards:
                    self.logger.warning("No hazard breakdown data available")
                    return None
                
                # Plot
                ax.bar(list(hazards.keys()), list(hazards.values()))
                ax.set_xlabel("Hazard Type")
                ax.set_ylabel("Average Annual Loss")
                ax.set_title("Average Annual Loss by Hazard Type")
                
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # Save if requested
                if kwargs.get("save", False):
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = kwargs.get("filename", f"aal_breakdown_{timestamp}.png")
                    filepath = os.path.join(self.output_dir, filename)
                    plt.savefig(filepath, dpi=300)
                    self.logger.info(f"Plot saved to {filepath}")
                
                return fig
            
            else:
                self.logger.warning(f"Unknown plot type: {plot_type}")
                return None
                
        except ImportError:
            self.logger.error("Matplotlib not available. Please install it to generate plots.")
            return None 