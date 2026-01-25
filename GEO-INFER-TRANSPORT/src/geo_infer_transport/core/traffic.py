"""
Traffic analysis module.

Provides traffic flow modeling, congestion analysis,
and simulation capabilities.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TrafficCondition(Enum):
    """Traffic condition levels."""
    FREE_FLOW = "free_flow"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    CONGESTED = "congested"
    BLOCKED = "blocked"


@dataclass
class TrafficCount:
    """Traffic count observation."""
    location_id: str
    timestamp: datetime
    count: int
    speed_kmh: Optional[float] = None
    occupancy: Optional[float] = None
    direction: Optional[str] = None


@dataclass
class FlowResult:
    """Traffic flow analysis result."""
    segment_id: str
    volume: int  # vehicles per hour
    density: float  # vehicles per km
    speed: float  # km/h
    level_of_service: str  # A-F


class TrafficAnalyzer:
    """
    Analyze and model traffic flow patterns.
    
    Supports flow modeling, congestion detection, and
    traffic simulation.
    """
    
    # Level of Service thresholds (volume/capacity)
    LOS_THRESHOLDS = {
        "A": 0.35,
        "B": 0.55,
        "C": 0.75,
        "D": 0.87,
        "E": 0.95,
        "F": 1.0
    }
    
    def __init__(
        self,
        data_sources: Optional[List[str]] = None,
        model_type: str = "bpr",
        time_resolution: str = "15min"
    ):
        """
        Initialize traffic analyzer.
        
        Args:
            data_sources: Traffic data sources
            model_type: Traffic model type ('bpr', 'akcelik', 'hcm')
            time_resolution: Temporal resolution
        """
        self.data_sources = data_sources or ["sensor", "probe"]
        self.model_type = model_type
        self.time_resolution = time_resolution
        self._traffic_counts: List[TrafficCount] = []
        logger.info(f"Initialized TrafficAnalyzer with {model_type} model")
    
    def analyze_flow(
        self,
        segment: Dict[str, Any],
        counts: List[Dict[str, Any]],
        time_period: str = "peak"
    ) -> FlowResult:
        """
        Analyze traffic flow on a road segment.
        
        Args:
            segment: Road segment properties
            counts: Traffic count data
            time_period: Analysis time period
            
        Returns:
            Flow analysis result
        """
        # Calculate average volume
        total_count = sum(c.get("count", 0) for c in counts)
        avg_volume = total_count / len(counts) if counts else 0
        
        # Hourly volume
        hourly_volume = int(avg_volume * 4)  # Assuming 15-min counts
        
        # Calculate speed from counts or use default
        speeds = [c.get("speed_kmh", segment.get("speed_limit", 50)) for c in counts if c.get("speed_kmh")]
        avg_speed = sum(speeds) / len(speeds) if speeds else segment.get("speed_limit", 50)
        
        # Calculate density (vehicles per km)
        density = hourly_volume / avg_speed if avg_speed > 0 else 0
        
        # Determine Level of Service
        capacity = segment.get("capacity", 2000)  # Default capacity
        vc_ratio = hourly_volume / capacity if capacity > 0 else 0
        
        los = "F"
        for level, threshold in self.LOS_THRESHOLDS.items():
            if vc_ratio <= threshold:
                los = level
                break
        
        result = FlowResult(
            segment_id=segment.get("id", "unknown"),
            volume=hourly_volume,
            density=round(density, 2),
            speed=round(avg_speed, 1),
            level_of_service=los
        )
        
        logger.info(f"Flow analysis for {segment.get('id')}: LOS {los}")
        return result
    
    def model_congestion(
        self,
        network_flows: Dict[str, float],
        capacity_data: Dict[str, float],
        algorithm: str = "bpr"
    ) -> Dict[str, Any]:
        """
        Model congestion across the network.
        
        Args:
            network_flows: Volume on each segment
            capacity_data: Capacity of each segment
            algorithm: Congestion function
            
        Returns:
            Congestion analysis results
        """
        congestion_results = {
            "algorithm": algorithm,
            "timestamp": datetime.now().isoformat(),
            "segments": [],
            "summary": {
                "total_segments": len(network_flows),
                "congested_segments": 0,
                "average_delay_factor": 0
            }
        }
        
        total_delay = 0
        
        for segment_id, volume in network_flows.items():
            capacity = capacity_data.get(segment_id, 2000)
            
            # Calculate delay using BPR function: t = t0 * (1 + α(v/c)^β)
            # α = 0.15, β = 4 are standard BPR parameters
            if algorithm == "bpr":
                vc_ratio = volume / capacity if capacity > 0 else 0
                delay_factor = 1 + 0.15 * (vc_ratio ** 4)
            else:
                delay_factor = 1 + (volume / capacity) if capacity > 0 else 1
            
            # Determine condition
            if delay_factor < 1.05:
                condition = TrafficCondition.FREE_FLOW
            elif delay_factor < 1.2:
                condition = TrafficCondition.LIGHT
            elif delay_factor < 1.5:
                condition = TrafficCondition.MODERATE
            elif delay_factor < 2.0:
                condition = TrafficCondition.HEAVY
            else:
                condition = TrafficCondition.CONGESTED
                congestion_results["summary"]["congested_segments"] += 1
            
            total_delay += delay_factor
            
            congestion_results["segments"].append({
                "segment_id": segment_id,
                "volume": volume,
                "capacity": capacity,
                "vc_ratio": round(volume / capacity, 3) if capacity > 0 else 0,
                "delay_factor": round(delay_factor, 3),
                "condition": condition.value
            })
        
        if network_flows:
            congestion_results["summary"]["average_delay_factor"] = round(
                total_delay / len(network_flows), 3
            )
        
        logger.info(f"Congestion modeled for {len(network_flows)} segments")
        return congestion_results
    
    def simulate_traffic(
        self,
        network: Any,
        demand_matrix: Dict[str, Any],
        simulation_hours: int = 1,
        time_step_seconds: int = 60
    ) -> Dict[str, Any]:
        """
        Simulate traffic flow over time.
        
        Args:
            network: Transport network
            demand_matrix: OD demand matrix
            simulation_hours: Hours to simulate
            time_step_seconds: Simulation time step
            
        Returns:
            Simulation results
        """
        num_steps = (simulation_hours * 3600) // time_step_seconds
        
        simulation = {
            "simulation_id": f"sim_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "duration_hours": simulation_hours,
            "time_step_seconds": time_step_seconds,
            "total_steps": num_steps,
            "results": [],
            "statistics": {
                "total_trips": 0,
                "completed_trips": 0,
                "average_travel_time": 0
            }
        }
        
        # Simple microsimulation mock
        matrix = demand_matrix.get("matrix", [[]])
        total_demand = sum(sum(row) for row in matrix)
        simulation["statistics"]["total_trips"] = int(total_demand)
        
        # Generate simplified step results
        for step in range(min(num_steps, 60)):  # Limit output
            step_time = step * time_step_seconds
            
            simulation["results"].append({
                "step": step,
                "time_seconds": step_time,
                "vehicles_in_network": int(total_demand * 0.3),  # 30% at any time
                "average_speed_kmh": 45 - (step % 10),  # Varying speed
                "congestion_level": "moderate" if step % 3 == 0 else "light"
            })
        
        simulation["statistics"]["completed_trips"] = int(total_demand * 0.95)
        simulation["statistics"]["average_travel_time"] = 600  # 10 minutes average
        
        logger.info(f"Traffic simulation completed: {num_steps} steps")
        return simulation
    
    def detect_incidents(
        self,
        current_data: Dict[str, Any],
        historical_baseline: Dict[str, Any],
        threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Detect traffic incidents from anomalies.
        
        Args:
            current_data: Current traffic conditions
            historical_baseline: Historical patterns
            threshold: Anomaly detection threshold
            
        Returns:
            List of detected incidents
        """
        incidents = []
        
        for segment_id, current in current_data.items():
            baseline = historical_baseline.get(segment_id, {})
            
            current_speed = current.get("speed", 50)
            baseline_speed = baseline.get("speed", 50)
            
            # Detect significant speed drop
            if baseline_speed > 0:
                speed_deviation = (baseline_speed - current_speed) / baseline_speed
                
                if speed_deviation > threshold:
                    severity = "high" if speed_deviation > 0.5 else "moderate"
                    
                    incidents.append({
                        "incident_id": f"inc_{segment_id}_{datetime.now().strftime('%H%M%S')}",
                        "segment_id": segment_id,
                        "type": "congestion_anomaly",
                        "severity": severity,
                        "current_speed": current_speed,
                        "expected_speed": baseline_speed,
                        "deviation": round(speed_deviation, 3),
                        "detected_at": datetime.now().isoformat()
                    })
        
        logger.info(f"Detected {len(incidents)} potential incidents")
        return incidents
    
    def forecast_traffic(
        self,
        historical_data: List[Dict[str, Any]],
        forecast_horizon: str = "1h",
        model: str = "arima"
    ) -> Dict[str, Any]:
        """
        Forecast future traffic conditions.
        
        Args:
            historical_data: Historical traffic data
            forecast_horizon: Forecast time horizon
            model: Forecasting model
            
        Returns:
            Traffic forecast
        """
        # Parse forecast horizon
        if "h" in forecast_horizon:
            steps = int(forecast_horizon.replace("h", "")) * 4  # 15-min intervals
        elif "m" in forecast_horizon:
            steps = int(forecast_horizon.replace("m", "")) // 15
        else:
            steps = 4
        
        # Simple moving average forecast (placeholder for actual model)
        if historical_data:
            values = [d.get("volume", 0) for d in historical_data[-12:]]
            avg_volume = sum(values) / len(values) if values else 0
        else:
            avg_volume = 1000
        
        forecast = {
            "model": model,
            "forecast_horizon": forecast_horizon,
            "generated_at": datetime.now().isoformat(),
            "forecasts": []
        }
        
        # Generate forecast points
        base_time = datetime.now()
        for i in range(steps):
            # Add some variation
            variation = (i % 4 - 2) * 50
            
            forecast["forecasts"].append({
                "time_offset_minutes": (i + 1) * 15,
                "predicted_volume": int(avg_volume + variation),
                "confidence_lower": int(avg_volume * 0.8),
                "confidence_upper": int(avg_volume * 1.2)
            })
        
        logger.info(f"Generated {steps}-step traffic forecast")
        return forecast
