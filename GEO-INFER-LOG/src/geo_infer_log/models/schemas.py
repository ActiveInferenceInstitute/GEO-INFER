"""
Data schemas for the GEO-INFER-LOG module.

This module defines the data structures used across the logistics and
supply chain optimization components.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon


class VehicleType(str, Enum):
    """Types of vehicles for routing and fleet management."""
    TRUCK = "truck"
    VAN = "van"
    CAR = "car"
    BIKE = "bike"
    DRONE = "drone"
    TRAIN = "train"
    SHIP = "ship"
    AIRPLANE = "airplane"


class FuelType(str, Enum):
    """Types of fuel/energy for vehicles."""
    DIESEL = "diesel"
    GASOLINE = "gasoline"
    ELECTRIC = "electric"
    HYBRID = "hybrid"
    HYDROGEN = "hydrogen"
    LNG = "lng"  # Liquefied Natural Gas
    CNG = "cng"  # Compressed Natural Gas


class DeliveryStatus(str, Enum):
    """Status values for delivery tracking."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"


class Vehicle(BaseModel):
    """Model representing a vehicle for routing and fleet management."""
    id: str
    type: VehicleType
    capacity: float = Field(..., description="Cargo capacity in kg or m³")
    max_range: float = Field(..., description="Maximum range in km")
    speed: float = Field(..., description="Average speed in km/h")
    cost_per_km: float = Field(..., description="Operating cost per kilometer")
    emissions_per_km: float = Field(..., description="Emissions in kg CO2e per km")
    location: Tuple[float, float] = Field(..., description="Current (lon, lat) coordinates")
    fuel_type: FuelType = Field(default=FuelType.DIESEL)
    fuel_capacity: Optional[float] = Field(default=None, description="Fuel capacity in liters or kWh")
    fuel_level: Optional[float] = Field(default=None, description="Current fuel level")
    maintenance_status: Optional[str] = Field(default=None)
    available: bool = Field(default=True, description="Whether vehicle is available for assignments")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "truck-001",
                "type": "truck",
                "capacity": 1000,
                "max_range": 500,
                "speed": 80,
                "cost_per_km": 1.2,
                "emissions_per_km": 0.8,
                "location": (13.404954, 52.520008),
                "fuel_type": "diesel",
                "fuel_capacity": 200,
                "fuel_level": 150,
                "maintenance_status": "good",
                "available": True
            }
        }


class Location(BaseModel):
    """Model representing a geographic location with metadata."""
    name: str
    coordinates: Tuple[float, float] = Field(..., description="(lon, lat) coordinates")
    address: Optional[str] = None
    type: str = Field(..., description="Type of location (e.g., depot, customer, supplier)")
    time_windows: Optional[List[Tuple[datetime, datetime]]] = Field(
        default=None, 
        description="Time windows when location is accessible"
    )
    service_time: Optional[int] = Field(
        default=None,
        description="Time in minutes required for service at this location"
    )
    priority: Optional[int] = Field(
        default=None,
        description="Priority of this location (lower is higher priority)"
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "Customer A",
                "coordinates": (13.4050, 52.5200),
                "address": "123 Main St, Berlin, Germany",
                "type": "customer",
                "time_windows": [
                    ("2023-01-01T09:00:00", "2023-01-01T12:00:00"),
                    ("2023-01-01T14:00:00", "2023-01-01T17:00:00")
                ],
                "service_time": 15,
                "priority": 1
            }
        }


class Shipment(BaseModel):
    """Model representing a shipment to be delivered."""
    id: str
    origin: Location
    destination: Location
    weight: float = Field(..., description="Weight in kg")
    volume: float = Field(..., description="Volume in m³")
    deadline: Optional[datetime] = None
    priority: int = Field(default=3, description="Priority (1=highest, 5=lowest)")
    status: DeliveryStatus = DeliveryStatus.PENDING
    special_requirements: Optional[List[str]] = None
    assigned_vehicle: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "shipment-123",
                "origin": {
                    "name": "Warehouse B",
                    "coordinates": (13.4050, 52.5200),
                    "type": "warehouse"
                },
                "destination": {
                    "name": "Customer C",
                    "coordinates": (13.5050, 52.4200),
                    "type": "customer"
                },
                "weight": 150,
                "volume": 0.8,
                "deadline": "2023-01-02T12:00:00",
                "priority": 2,
                "status": "pending",
                "special_requirements": ["refrigeration", "fragile"],
                "assigned_vehicle": None
            }
        }


class Route(BaseModel):
    """Model representing an optimized route."""
    id: str
    vehicle_id: str
    stops: List[Location]
    departure_time: datetime
    estimated_arrival_time: datetime
    total_distance: float = Field(..., description="Total distance in km")
    total_time: float = Field(..., description="Total time in minutes")
    total_cost: float
    total_emissions: float = Field(..., description="Total emissions in kg CO2e")
    geometry: Optional[dict] = Field(
        default=None, 
        description="GeoJSON representation of route geometry"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "id": "route-456",
                "vehicle_id": "truck-001",
                "stops": [
                    {"name": "Warehouse A", "coordinates": (13.4050, 52.5200), "type": "depot"},
                    {"name": "Customer B", "coordinates": (13.5050, 52.4200), "type": "customer"},
                    {"name": "Customer C", "coordinates": (13.6050, 52.3200), "type": "customer"},
                    {"name": "Warehouse A", "coordinates": (13.4050, 52.5200), "type": "depot"}
                ],
                "departure_time": "2023-01-01T08:00:00",
                "estimated_arrival_time": "2023-01-01T16:30:00",
                "total_distance": 120,
                "total_time": 180,
                "total_cost": 144,
                "total_emissions": 96,
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [13.4050, 52.5200],
                        [13.5050, 52.4200],
                        [13.6050, 52.3200],
                        [13.4050, 52.5200]
                    ]
                }
            }
        }


class RoutingParameters(BaseModel):
    """Parameters for routing optimization."""
    weight_factor: str = Field(
        default="time",
        description="Factor to optimize for (time, distance, cost, emissions)"
    )
    avoid_highways: bool = False
    avoid_tolls: bool = False
    avoid_ferries: bool = False
    traffic_model: str = Field(
        default="best_guess",
        description="Traffic model (best_guess, optimistic, pessimistic)"
    )
    departure_time: Optional[datetime] = None
    max_stops_per_route: Optional[int] = None
    max_route_duration: Optional[int] = Field(
        default=None,
        description="Maximum route duration in minutes"
    )
    max_route_distance: Optional[float] = Field(
        default=None,
        description="Maximum route distance in km"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "weight_factor": "time",
                "avoid_highways": False,
                "avoid_tolls": True,
                "avoid_ferries": True,
                "traffic_model": "best_guess",
                "departure_time": "2023-01-01T08:00:00",
                "max_stops_per_route": 20,
                "max_route_duration": 480,
                "max_route_distance": 300
            }
        }


class FacilityLocation(BaseModel):
    """Model representing a facility location in a supply chain network."""
    id: str
    name: str
    location: Tuple[float, float] = Field(..., description="(lon, lat) coordinates")
    type: str = Field(..., description="Type of facility (warehouse, distribution center, etc.)")
    capacity: float
    operating_cost: float
    inbound_capacity: Optional[float] = None
    outbound_capacity: Optional[float] = None
    service_area: Optional[dict] = Field(
        default=None, 
        description="GeoJSON representation of service area"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "id": "dc-001",
                "name": "Berlin Distribution Center",
                "location": (13.4050, 52.5200),
                "type": "distribution_center",
                "capacity": 5000,
                "operating_cost": 10000,
                "inbound_capacity": 1000,
                "outbound_capacity": 800,
                "service_area": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [13.3, 52.4],
                            [13.5, 52.4],
                            [13.5, 52.6],
                            [13.3, 52.6],
                            [13.3, 52.4]
                        ]
                    ]
                }
            }
        }


class SupplyChainNetwork(BaseModel):
    """Model representing a supply chain network."""
    id: str
    name: str
    facilities: List[FacilityLocation]
    links: List[Dict] = Field(
        ...,
        description="List of links between facilities with transportation costs"
    )
    demand_points: Optional[List[Dict]] = None
    supply_points: Optional[List[Dict]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "network-001",
                "name": "European Distribution Network",
                "facilities": [
                    {
                        "id": "dc-001",
                        "name": "Berlin Distribution Center",
                        "location": (13.4050, 52.5200),
                        "type": "distribution_center",
                        "capacity": 5000,
                        "operating_cost": 10000
                    },
                    {
                        "id": "wh-001",
                        "name": "Munich Warehouse",
                        "location": (11.5820, 48.1351),
                        "type": "warehouse",
                        "capacity": 3000,
                        "operating_cost": 8000
                    }
                ],
                "links": [
                    {
                        "from": "dc-001",
                        "to": "wh-001",
                        "distance": 504,
                        "time": 300,
                        "cost": 600,
                        "capacity": 1000
                    }
                ],
                "demand_points": [
                    {
                        "id": "dp-001",
                        "location": (8.6821, 50.1109),
                        "demand": 200,
                        "priority": 1
                    }
                ],
                "supply_points": [
                    {
                        "id": "sp-001",
                        "location": (18.0686, 59.3293),
                        "supply": 500,
                        "reliability": 0.95
                    }
                ]
            }
        } 