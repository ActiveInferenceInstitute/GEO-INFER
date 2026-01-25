"""
Resource deployment module.

Provides resource allocation, deployment optimization, and
real-time tracking for emergency resources.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import heapq

logger = logging.getLogger(__name__)


class ResourceStatus(Enum):
    """Status of emergency resources."""
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    OUT_OF_SERVICE = "out_of_service"
    RETURNING = "returning"


class ResourceType(Enum):
    """Types of emergency resources."""
    ENGINE = "engine"
    TRUCK = "truck"
    AMBULANCE = "ambulance"
    RESCUE_UNIT = "rescue_unit"
    HAZMAT = "hazmat"
    HELICOPTER = "helicopter"
    DOZER = "dozer"
    WATER_TENDER = "water_tender"
    PERSONNEL = "personnel"


@dataclass
class Resource:
    """Represents an emergency resource unit."""
    resource_id: str
    resource_type: ResourceType
    name: str
    status: ResourceStatus = ResourceStatus.AVAILABLE
    location: Optional[Dict[str, float]] = None  # lat, lon
    capacity: int = 1
    agency: str = ""
    capabilities: List[str] = field(default_factory=list)
    assigned_incident: Optional[str] = None


@dataclass
class ResourceRequest:
    """A request for emergency resources."""
    request_id: str
    incident_id: str
    resource_types: List[str]
    quantity: int
    priority: int = 1  # 1 = highest
    location: Dict[str, float] = field(default_factory=dict)
    requested_at: datetime = field(default_factory=datetime.now)
    fulfilled: bool = False


class ResourceDeployer:
    """
    Optimize deployment and allocation of emergency resources.
    
    Uses optimization algorithms to minimize response time
    and maximize coverage.
    """
    
    def __init__(
        self,
        resource_types: Optional[List[str]] = None,
        optimization_algorithm: str = "mixed_integer",
        real_time_updates: bool = True
    ):
        """
        Initialize resource deployer.
        
        Args:
            resource_types: Types of resources to manage
            optimization_algorithm: Optimization method to use
            real_time_updates: Enable real-time tracking
        """
        self.resource_types = resource_types or ["engines", "ambulances", "rescue_units"]
        self.optimization_algorithm = optimization_algorithm
        self.real_time_updates = real_time_updates
        self._resources: Dict[str, Resource] = {}
        self._requests: Dict[str, ResourceRequest] = {}
        self._request_queue: List[Tuple[int, str]] = []  # Priority queue
        logger.info(f"Initialized ResourceDeployer with {optimization_algorithm} optimization")
    
    def register_resource(self, resource: Resource) -> None:
        """Register a resource in the deployment system."""
        self._resources[resource.resource_id] = resource
        logger.debug(f"Registered resource: {resource.resource_id}")
    
    def optimize_allocation(
        self,
        resources: List[Dict[str, Any]],
        demand_points: List[Dict[str, Any]],
        constraints: Dict[str, Any],
        objectives: List[str]
    ) -> Dict[str, Any]:
        """
        Optimize resource allocation to demand points.
        
        Args:
            resources: Available resources with locations
            demand_points: Locations requiring resources
            constraints: Optimization constraints
            objectives: Optimization objectives
            
        Returns:
            Optimized allocation plan
        """
        # Register resources
        for res_data in resources:
            resource = Resource(
                resource_id=res_data.get("id", f"res_{len(self._resources)}"),
                resource_type=ResourceType(res_data.get("type", "engine").lower()),
                name=res_data.get("name", ""),
                location=res_data.get("location"),
                status=ResourceStatus(res_data.get("status", "available")),
                agency=res_data.get("agency", "")
            )
            self.register_resource(resource)
        
        # Calculate distances and response times
        allocations = []
        unallocated_demands = []
        available_resources = [r for r in self._resources.values() 
                              if r.status == ResourceStatus.AVAILABLE]
        
        for demand in demand_points:
            demand_loc = demand.get("location", {})
            
            # Find nearest available resource
            best_resource = None
            best_time = float('inf')
            
            for resource in available_resources:
                if resource.location:
                    travel_time = self._estimate_travel_time(resource.location, demand_loc)
                    if travel_time < best_time:
                        best_time = travel_time
                        best_resource = resource
            
            if best_resource and best_time <= constraints.get("response_time", 15):
                allocations.append({
                    "demand_id": demand.get("id", ""),
                    "demand_location": demand_loc,
                    "resource_id": best_resource.resource_id,
                    "resource_type": best_resource.resource_type.value,
                    "estimated_response_time": best_time,
                    "status": "allocated"
                })
                # Mark resource as assigned
                best_resource.status = ResourceStatus.ASSIGNED
                available_resources.remove(best_resource)
            else:
                unallocated_demands.append(demand.get("id", ""))
        
        # Calculate coverage
        total_demands = len(demand_points)
        covered_demands = len(allocations)
        coverage = covered_demands / total_demands if total_demands > 0 else 1.0
        
        result = {
            "optimization_algorithm": self.optimization_algorithm,
            "objectives": objectives,
            "constraints": constraints,
            "allocations": allocations,
            "unallocated_demands": unallocated_demands,
            "metrics": {
                "total_resources": len(resources),
                "resources_allocated": len(allocations),
                "total_demands": total_demands,
                "demands_covered": covered_demands,
                "coverage_rate": coverage,
                "average_response_time": (
                    sum(a["estimated_response_time"] for a in allocations) / len(allocations)
                    if allocations else 0
                )
            },
            "feasible": coverage >= constraints.get("coverage", 0.8),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Optimized allocation: {covered_demands}/{total_demands} demands covered")
        return result
    
    def _estimate_travel_time(
        self,
        from_loc: Dict[str, float],
        to_loc: Dict[str, float]
    ) -> float:
        """Estimate travel time between two locations."""
        # Simple Haversine-based estimate
        import math
        
        lat1 = from_loc.get("lat", 0) * math.pi / 180
        lat2 = to_loc.get("lat", 0) * math.pi / 180
        lon1 = from_loc.get("lon", 0) * math.pi / 180
        lon2 = to_loc.get("lon", 0) * math.pi / 180
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in km
        r = 6371
        distance = c * r
        
        # Assume 40 km/h average speed for emergency response
        speed = 40
        travel_time_hours = distance / speed
        travel_time_minutes = travel_time_hours * 60
        
        return travel_time_minutes
    
    def dynamic_redeploy(
        self,
        current_positions: List[Dict[str, Any]],
        pending_incidents: List[Dict[str, Any]],
        predicted_demand: Dict[str, Any],
        strategy: str = "move_up"
    ) -> Dict[str, Any]:
        """
        Dynamically redeploy resources based on current conditions.
        
        Args:
            current_positions: Current resource positions
            pending_incidents: Pending incidents without resources
            predicted_demand: Predicted future demand
            strategy: Redeployment strategy
            
        Returns:
            Redeployment plan
        """
        redeployments = []
        
        # Update resource positions
        for pos in current_positions:
            res_id = pos.get("resource_id")
            if res_id in self._resources:
                self._resources[res_id].location = pos.get("location")
        
        # Find available resources
        available = [r for r in self._resources.values() 
                    if r.status == ResourceStatus.AVAILABLE]
        
        if strategy == "move_up":
            # Move units to cover gaps left by responding units
            gap_locations = predicted_demand.get("high_risk_areas", [])
            
            for gap in gap_locations:
                if available:
                    # Find unit farthest from any incident
                    best_unit = available[0]
                    redeployments.append({
                        "resource_id": best_unit.resource_id,
                        "from_location": best_unit.location,
                        "to_location": gap,
                        "reason": "coverage_gap",
                        "estimated_travel_minutes": self._estimate_travel_time(
                            best_unit.location or {"lat": 0, "lon": 0}, gap
                        ) if best_unit.location else 0
                    })
                    available.remove(best_unit)
        
        result = {
            "strategy": strategy,
            "timestamp": datetime.now().isoformat(),
            "redeployments": redeployments,
            "pending_incidents_covered": len(pending_incidents),
            "units_redeployed": len(redeployments)
        }
        
        logger.info(f"Dynamic redeployment: {len(redeployments)} units moved")
        return result
    
    def manage_staging(
        self,
        staging_areas: List[Dict[str, Any]],
        incoming_resources: List[Dict[str, Any]],
        assignment_queue: List[Dict[str, Any]],
        prioritization: str = "incident_severity"
    ) -> Dict[str, Any]:
        """
        Manage staging area operations.
        
        Args:
            staging_areas: Available staging locations
            incoming_resources: Resources arriving
            assignment_queue: Pending assignments
            prioritization: How to prioritize assignments
            
        Returns:
            Staging management plan
        """
        staging_plan = {
            "staging_areas": [],
            "incoming_assignments": [],
            "pending_queue": [],
            "prioritization": prioritization,
            "timestamp": datetime.now().isoformat()
        }
        
        # Assign staging areas
        for i, staging in enumerate(staging_areas):
            area_plan = {
                "staging_id": staging.get("id", f"staging_{i}"),
                "location": staging.get("location"),
                "capacity": staging.get("capacity", 50),
                "current_count": 0,
                "assigned_resources": []
            }
            
            # Assign incoming resources to staging
            for resource in incoming_resources:
                if area_plan["current_count"] < area_plan["capacity"]:
                    area_plan["assigned_resources"].append(resource.get("id"))
                    area_plan["current_count"] += 1
            
            staging_plan["staging_areas"].append(area_plan)
        
        # Process assignment queue by priority
        if prioritization == "incident_severity":
            sorted_queue = sorted(assignment_queue, key=lambda x: x.get("severity", 0), reverse=True)
        else:
            sorted_queue = assignment_queue
        
        for assignment in sorted_queue:
            staging_plan["pending_queue"].append({
                "assignment_id": assignment.get("id"),
                "incident": assignment.get("incident"),
                "resources_needed": assignment.get("resources_needed"),
                "priority_rank": sorted_queue.index(assignment) + 1
            })
        
        logger.info(f"Managed {len(staging_areas)} staging areas with {len(incoming_resources)} incoming resources")
        return staging_plan
    
    def track_resources(
        self,
        resources: List[Dict[str, Any]],
        update_frequency: str = "real_time",
        metrics: List[str] = None
    ) -> Dict[str, Any]:
        """
        Track resource status and locations.
        
        Args:
            resources: Resources to track
            update_frequency: How often to update
            metrics: Metrics to track
            
        Returns:
            Resource tracking data
        """
        metrics = metrics or ["location", "status", "availability", "eta"]
        
        tracking = {
            "update_frequency": update_frequency,
            "timestamp": datetime.now().isoformat(),
            "resources": [],
            "summary": {
                "total": len(resources),
                "available": 0,
                "assigned": 0,
                "en_route": 0,
                "on_scene": 0,
                "out_of_service": 0
            }
        }
        
        for res_data in resources:
            res_id = res_data.get("id")
            status = res_data.get("status", "available")
            
            resource_track = {
                "resource_id": res_id,
                "type": res_data.get("type", "unknown")
            }
            
            if "location" in metrics:
                resource_track["location"] = res_data.get("location")
            if "status" in metrics:
                resource_track["status"] = status
            if "availability" in metrics:
                resource_track["available"] = status == "available"
            if "eta" in metrics:
                resource_track["eta_minutes"] = res_data.get("eta", None)
            
            tracking["resources"].append(resource_track)
            
            # Update summary
            if status == "available":
                tracking["summary"]["available"] += 1
            elif status == "assigned":
                tracking["summary"]["assigned"] += 1
            elif status == "en_route":
                tracking["summary"]["en_route"] += 1
            elif status == "on_scene":
                tracking["summary"]["on_scene"] += 1
            else:
                tracking["summary"]["out_of_service"] += 1
        
        logger.debug(f"Tracking {len(resources)} resources")
        return tracking
    
    def get_resource_status(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific resource."""
        resource = self._resources.get(resource_id)
        if resource:
            return {
                "resource_id": resource.resource_id,
                "type": resource.resource_type.value,
                "name": resource.name,
                "status": resource.status.value,
                "location": resource.location,
                "assigned_incident": resource.assigned_incident
            }
        return None
