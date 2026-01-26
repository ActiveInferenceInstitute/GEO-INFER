# api
 ## Overview
 This directory contains api components. It includes 4 Python modules. ## Components
 ### deliver
y
.py API endpoints for last-mile delivery in GEO-INFER-LOG. **Classes**: `DeliveryOptimizationRequest`, `ScheduleRequest`, `ServiceAreaRequest`, `CoverageAnalysisRequest`, `RescheduleRequest`, `Config`, `Config`, `Config`, `Config`, `Config` **Functions**: `get_last_mile_router`, `get_delivery_scheduler`, `get_service_area_analyzer` ### route
s
.py API endpoints for route optimization in GEO-INFER-LOG. **Classes**: `RouteRequest`, `VehicleRegistration`, `VRPRequest`, `Config`, `Config`, `Config` **Functions**: `get_route_optimizer`, `get_fleet_manager`, `get_vehicle_router` ### supply_chai
n
.py API endpoints for supply chain functionality in GEO-INFER-LOG. **Classes**: `NetworkRequest`, `FlowOptimizationRequest`, `DisruptionAnalysisRequest`, `FacilityLocationRequest`, `NetworkOptimizationRequest`, `Config`, `Config`, `Config`, `Config`, `Config` **Functions**: `get_supply_chain_model`, `get_resilience_analyzer`, `get_network_optimizer`, `get_facility_locator` ### transpor
t
.py API endpoints for multimodal transportation planning in GEO-INFER-LOG. **Classes**: `RouteRequest`, `CompareRoutesRequest`, `NetworkMetricsRequest`, `TrafficSimulationRequest`, `EmissionsCalculationRequest`, `EmissionsComparisonRequest`, `Config`, `Config`, `Config`, `Config`, `Config`, `Config` **Functions**: `get_multimodal_planner`, `get_network_analyzer`, `get_traffic_simulator`, `get_emissions_calculator` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 