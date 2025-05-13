"""
API endpoints for last-mile delivery in GEO-INFER-LOG.

This module provides FastAPI endpoints for last-mile delivery functionality,
service area analysis, and delivery scheduling.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime

from geo_infer_log.models.schemas import Vehicle, Location, Route, RoutingParameters
from geo_infer_log.core.delivery import LastMileRouter, DeliveryScheduler, ServiceAreaAnalyzer


router = APIRouter(
    prefix="/delivery",
    tags=["delivery"],
    responses={404: {"description": "Not found"}},
)


class DeliveryOptimizationRequest(BaseModel):
    """Request model for delivery optimization."""
    depot: Location
    deliveries: List[Location]
    vehicles: List[Vehicle]
    constraints: Dict = Field(default_factory=dict)

    class Config:
        schema_extra = {
            "example": {
                "depot": {
                    "name": "Berlin Warehouse",
                    "coordinates": (13.404954, 52.520008),
                    "type": "depot"
                },
                "deliveries": [
                    {
                        "name": "Customer A",
                        "coordinates": (13.5, 52.5),
                        "type": "customer",
                        "service_time": 15,
                        "priority": 1
                    },
                    {
                        "name": "Customer B",
                        "coordinates": (13.4, 52.4),
                        "type": "customer",
                        "service_time": 10,
                        "priority": 2
                    }
                ],
                "vehicles": [
                    {
                        "id": "truck-001",
                        "type": "truck",
                        "capacity": 1000,
                        "max_range": 500,
                        "speed": 80,
                        "cost_per_km": 1.2,
                        "emissions_per_km": 0.8,
                        "location": (13.404954, 52.520008)
                    }
                ],
                "constraints": {
                    "max_route_duration": 480,
                    "max_stops_per_route": 20
                }
            }
        }


class ScheduleRequest(BaseModel):
    """Request model for delivery scheduling."""
    depot: Location
    deliveries: List[Location]
    vehicles: List[Vehicle]
    start_date: datetime
    end_date: datetime
    max_deliveries_per_day: int = 50

    class Config:
        schema_extra = {
            "example": {
                "depot": {
                    "name": "Berlin Warehouse",
                    "coordinates": (13.404954, 52.520008),
                    "type": "depot"
                },
                "deliveries": [
                    {
                        "name": "Customer A",
                        "coordinates": (13.5, 52.5),
                        "type": "customer",
                        "service_time": 15
                    }
                ],
                "vehicles": [
                    {
                        "id": "truck-001",
                        "type": "truck",
                        "capacity": 1000,
                        "max_range": 500,
                        "speed": 80,
                        "cost_per_km": 1.2,
                        "emissions_per_km": 0.8,
                        "location": (13.404954, 52.520008)
                    }
                ],
                "start_date": "2023-01-01T08:00:00",
                "end_date": "2023-01-07T18:00:00",
                "max_deliveries_per_day": 30
            }
        }


class ServiceAreaRequest(BaseModel):
    """Request model for service area definition."""
    depot_id: str
    depot_location: Tuple[float, float]
    max_time: Optional[int] = None
    max_distance: Optional[float] = None

    class Config:
        schema_extra = {
            "example": {
                "depot_id": "depot-001",
                "depot_location": (13.404954, 52.520008),
                "max_time": 60,  # minutes
                "max_distance": 30  # km
            }
        }


class CoverageAnalysisRequest(BaseModel):
    """Request model for service area coverage analysis."""
    service_areas: Dict[str, Dict]
    demand_points: List[Dict]

    class Config:
        schema_extra = {
            "example": {
                "service_areas": {
                    "depot-001": {
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
                },
                "demand_points": [
                    {"id": "d1", "location": (13.4, 52.5)},
                    {"id": "d2", "location": (13.6, 52.5)}
                ]
            }
        }


class RescheduleRequest(BaseModel):
    """Request model for delivery rescheduling."""
    route_id: str
    delivery_idx: int
    new_date: datetime

    class Config:
        schema_extra = {
            "example": {
                "route_id": "route-001",
                "delivery_idx": 2,
                "new_date": "2023-01-02T14:00:00"
            }
        }


# Get a last-mile router instance
def get_last_mile_router():
    """Dependency for last-mile router."""
    return LastMileRouter()


# Get a delivery scheduler instance
def get_delivery_scheduler(
    router: LastMileRouter = Depends(get_last_mile_router)
):
    """Dependency for delivery scheduler."""
    return DeliveryScheduler(router)


# Get a service area analyzer instance
def get_service_area_analyzer():
    """Dependency for service area analyzer."""
    return ServiceAreaAnalyzer()


@router.post("/optimize", response_model=List[Dict])
async def optimize_deliveries(
    request: DeliveryOptimizationRequest,
    router: LastMileRouter = Depends(get_last_mile_router)
):
    """Optimize deliveries from a depot."""
    try:
        routes = router.optimize_deliveries(
            depot=request.depot,
            deliveries=request.deliveries,
            vehicles=request.vehicles,
            constraints=request.constraints
        )
        
        # Convert route objects to dictionaries
        return [route.dict() for route in routes]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/schedule", response_model=Dict)
async def create_schedule(
    request: ScheduleRequest,
    scheduler: DeliveryScheduler = Depends(get_delivery_scheduler)
):
    """Create a delivery schedule for a date range."""
    try:
        result = scheduler.create_schedule(
            depot=request.depot,
            deliveries=request.deliveries,
            vehicles=request.vehicles,
            start_date=request.start_date,
            end_date=request.end_date,
            max_deliveries_per_day=request.max_deliveries_per_day
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/schedule/{date}", response_model=List[Dict])
async def get_daily_schedule(
    date: str,
    scheduler: DeliveryScheduler = Depends(get_delivery_scheduler)
):
    """Get the delivery schedule for a specific day."""
    try:
        # Parse date string to datetime
        date_obj = datetime.fromisoformat(date)
        routes = scheduler.get_daily_schedule(date_obj)
        
        # Convert route objects to dictionaries
        return [route.dict() for route in routes]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/schedule/vehicle/{vehicle_id}", response_model=List[Dict])
async def get_vehicle_schedule(
    vehicle_id: str,
    scheduler: DeliveryScheduler = Depends(get_delivery_scheduler)
):
    """Get the schedule for a specific vehicle."""
    try:
        routes = scheduler.get_vehicle_schedule(vehicle_id)
        
        # Convert route objects to dictionaries
        return [route.dict() for route in routes]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reschedule", response_model=Dict)
async def reschedule_delivery(
    request: RescheduleRequest,
    scheduler: DeliveryScheduler = Depends(get_delivery_scheduler)
):
    """Reschedule a delivery to a different date."""
    try:
        result = scheduler.reschedule_delivery(
            route_id=request.route_id,
            delivery_idx=request.delivery_idx,
            new_date=request.new_date
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/service-area", response_model=Dict)
async def create_service_area(
    request: ServiceAreaRequest,
    analyzer: ServiceAreaAnalyzer = Depends(get_service_area_analyzer)
):
    """Create a service area around a depot."""
    try:
        gdf = analyzer.create_service_area(
            depot_id=request.depot_id,
            depot_location=request.depot_location,
            max_time=request.max_time,
            max_distance=request.max_distance
        )
        
        # Convert GeoDataFrame to GeoJSON
        geo_json = gdf.to_json()
        
        return {
            "depot_id": request.depot_id,
            "max_time": request.max_time,
            "max_distance": request.max_distance,
            "area": geo_json
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/coverage", response_model=Dict)
async def analyze_coverage(
    request: CoverageAnalysisRequest,
    analyzer: ServiceAreaAnalyzer = Depends(get_service_area_analyzer)
):
    """Analyze coverage of demand points by service areas."""
    try:
        # This is a simplified implementation - in reality, we would need to
        # convert the GeoJSON service areas to Shapely polygons and the
        # demand points to a GeoDataFrame
        
        # Placeholder response
        return {
            "total_points": len(request.demand_points),
            "covered_points": 0,
            "uncovered_points": 0,
            "coverage_ratio": 0.0,
            "depot_coverage": {}
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 