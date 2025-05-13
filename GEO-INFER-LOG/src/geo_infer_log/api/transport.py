"""
API endpoints for multimodal transportation planning in GEO-INFER-LOG.

This module provides FastAPI endpoints for multimodal transportation planning,
transportation network analysis, and emissions calculation.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, Field
import pandas as pd

from geo_infer_log.models.schemas import Vehicle, Route, VehicleType, FuelType
from geo_infer_log.core.transport import (
    MultiModalPlanner, TransportationNetworkAnalyzer, 
    TrafficSimulator, EmissionsCalculator
)


router = APIRouter(
    prefix="/transport",
    tags=["transport"],
    responses={404: {"description": "Not found"}},
)


class RouteRequest(BaseModel):
    """Request model for multimodal route planning."""
    origin: Tuple[float, float] = Field(..., description="(lon, lat) of origin")
    destination: Tuple[float, float] = Field(..., description="(lon, lat) of destination")
    allowed_modes: List[str] = Field(..., description="List of allowed transportation modes")
    preferences: Optional[Dict] = None

    class Config:
        schema_extra = {
            "example": {
                "origin": (13.404954, 52.520008),  # Berlin
                "destination": (11.576124, 48.137154),  # Munich
                "allowed_modes": ["car", "train", "bus"],
                "preferences": {
                    "cost_weight": 1.0,
                    "time_weight": 1.5,
                    "emissions_weight": 2.0,
                    "transfers_weight": 0.5
                }
            }
        }


class CompareRoutesRequest(BaseModel):
    """Request model for route comparison."""
    origin: Tuple[float, float] = Field(..., description="(lon, lat) of origin")
    destination: Tuple[float, float] = Field(..., description="(lon, lat) of destination")
    mode_combinations: List[List[str]] = Field(
        ..., 
        description="List of mode combinations to compare"
    )

    class Config:
        schema_extra = {
            "example": {
                "origin": (13.404954, 52.520008),  # Berlin
                "destination": (11.576124, 48.137154),  # Munich
                "mode_combinations": [
                    ["car"],
                    ["train"],
                    ["car", "train"]
                ]
            }
        }


class NetworkMetricsRequest(BaseModel):
    """Request model for network metrics calculation."""
    network_id: str

    class Config:
        schema_extra = {
            "example": {
                "network_id": "transport-network-001"
            }
        }


class TrafficSimulationRequest(BaseModel):
    """Request model for traffic simulation."""
    origin: str
    destination: str
    departure_time: str

    class Config:
        schema_extra = {
            "example": {
                "origin": "node-001",
                "destination": "node-045",
                "departure_time": "morning_peak"
            }
        }


class EmissionsCalculationRequest(BaseModel):
    """Request model for emissions calculation."""
    vehicle: Vehicle
    distance: float
    load_factor: float = 1.0
    terrain_factor: float = 1.0

    class Config:
        schema_extra = {
            "example": {
                "vehicle": {
                    "id": "truck-001",
                    "type": "truck",
                    "capacity": 1000,
                    "max_range": 500,
                    "speed": 80,
                    "cost_per_km": 1.2,
                    "emissions_per_km": 0.8,
                    "location": (13.404954, 52.520008),
                    "fuel_type": "diesel"
                },
                "distance": 150,
                "load_factor": 0.8,
                "terrain_factor": 1.2
            }
        }


class EmissionsComparisonRequest(BaseModel):
    """Request model for emissions comparison."""
    route: Dict
    vehicle_options: List[Vehicle]

    class Config:
        schema_extra = {
            "example": {
                "route": {
                    "distance": 150,
                    "origin": (13.404954, 52.520008),
                    "destination": (11.576124, 48.137154)
                },
                "vehicle_options": [
                    {
                        "id": "truck-001",
                        "type": "truck",
                        "capacity": 1000,
                        "max_range": 500,
                        "speed": 80,
                        "cost_per_km": 1.2,
                        "emissions_per_km": 0.8,
                        "location": (13.404954, 52.520008),
                        "fuel_type": "diesel"
                    },
                    {
                        "id": "truck-002",
                        "type": "truck",
                        "capacity": 1000,
                        "max_range": 400,
                        "speed": 70,
                        "cost_per_km": 1.0,
                        "emissions_per_km": 0.5,
                        "location": (13.404954, 52.520008),
                        "fuel_type": "electric"
                    }
                ]
            }
        }


# Get a multimodal planner instance
def get_multimodal_planner():
    """Dependency for multimodal planner."""
    return MultiModalPlanner()


# Get a transportation network analyzer instance
def get_network_analyzer():
    """Dependency for transportation network analyzer."""
    return TransportationNetworkAnalyzer()


# Get a traffic simulator instance
def get_traffic_simulator():
    """Dependency for traffic simulator."""
    return TrafficSimulator()


# Get an emissions calculator instance
def get_emissions_calculator():
    """Dependency for emissions calculator."""
    return EmissionsCalculator()


@router.post("/route", response_model=Dict)
async def plan_route(
    request: RouteRequest,
    planner: MultiModalPlanner = Depends(get_multimodal_planner)
):
    """Plan a multimodal route between origin and destination."""
    try:
        route = planner.plan_route(
            origin=request.origin,
            destination=request.destination,
            allowed_modes=request.allowed_modes,
            preferences=request.preferences
        )
        return route
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/compare-routes", response_model=Dict)
async def compare_routes(
    request: CompareRoutesRequest,
    planner: MultiModalPlanner = Depends(get_multimodal_planner)
):
    """Compare different multimodal routes between origin and destination."""
    try:
        df = planner.compare_routes(
            origin=request.origin,
            destination=request.destination,
            mode_combinations=request.mode_combinations
        )
        
        # Convert DataFrame to dict
        return {"comparisons": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/network/metrics", response_model=Dict)
async def get_network_metrics(
    request: NetworkMetricsRequest,
    analyzer: TransportationNetworkAnalyzer = Depends(get_network_analyzer)
):
    """Calculate metrics for a transportation network."""
    try:
        metrics = analyzer.calculate_network_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/network/critical-links", response_model=List[List[str]])
async def identify_critical_links(
    request: NetworkMetricsRequest,
    analyzer: TransportationNetworkAnalyzer = Depends(get_network_analyzer),
    top_n: int = Query(10, description="Number of critical links to identify")
):
    """Identify critical links in a transportation network."""
    try:
        links = analyzer.identify_critical_links(top_n=top_n)
        return links
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/traffic/simulate", response_model=Dict)
async def simulate_traffic(
    request: TrafficSimulationRequest,
    simulator: TrafficSimulator = Depends(get_traffic_simulator)
):
    """Simulate traffic for a route."""
    try:
        result = simulator.simulate_traffic(
            origin=request.origin,
            destination=request.destination,
            departure_time=request.departure_time
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/traffic/congestion", response_model=Dict)
async def analyze_congestion(
    simulator: TrafficSimulator = Depends(get_traffic_simulator),
    time_period: Optional[str] = Query(None, description="Time period to analyze"),
    congestion_threshold: float = Query(0.7, description="Congestion threshold")
):
    """Analyze network congestion."""
    try:
        result = simulator.analyze_congestion(
            time_period=time_period,
            congestion_threshold=congestion_threshold
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/emissions/calculate", response_model=float)
async def calculate_emissions(
    request: EmissionsCalculationRequest,
    calculator: EmissionsCalculator = Depends(get_emissions_calculator)
):
    """Calculate emissions for a route with a specific vehicle."""
    try:
        emissions = calculator.calculate_route_emissions(
            vehicle=request.vehicle,
            distance=request.distance,
            load_factor=request.load_factor,
            terrain_factor=request.terrain_factor
        )
        return emissions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/emissions/compare", response_model=Dict)
async def compare_vehicle_emissions(
    request: EmissionsComparisonRequest,
    calculator: EmissionsCalculator = Depends(get_emissions_calculator)
):
    """Compare emissions for different vehicle options on a route."""
    try:
        df = calculator.compare_emissions(
            route=request.route,
            vehicle_options=request.vehicle_options
        )
        
        # Convert DataFrame to dict
        return {"comparisons": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/emissions/fleet", response_model=Dict)
async def calculate_fleet_emissions(
    fleet: List[Vehicle],
    routes: List[Route],
    calculator: EmissionsCalculator = Depends(get_emissions_calculator)
):
    """Calculate total emissions for a fleet of vehicles."""
    try:
        result = calculator.calculate_fleet_emissions(
            fleet=fleet,
            routes=routes
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 