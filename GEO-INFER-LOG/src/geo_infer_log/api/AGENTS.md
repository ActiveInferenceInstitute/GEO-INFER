# Agent
: api ## Scope
 This directory contains api components for the module. It provides 38 classes and 14 functions. ## Classes
 and Functions ### DeliveryOptimizationReques
t
 Request model for delivery optimization. ### ScheduleReques
t
 Request model for delivery scheduling. ### ServiceAreaReques
t
 Request model for service area definition. ### CoverageAnalysisReques
t
 Request model for service area coverage analysis. ### RescheduleReques
t
 Request model for delivery rescheduling. ### Confi
g
 ### Confi
g
 ### Confi
g
 ### Confi
g
 ### Confi
g
 ### RouteReques
t
 Request model for route optimization. ### VehicleRegistratio
n
 Request model for vehicle registration. ### VRPReques
t
 Request model for vehicle routing problem. ### Confi
g
 ### Confi
g
 ### Confi
g
 ### NetworkReques
t
 Request model for supply chain network operations. ### FlowOptimizationReques
t
 Request model for supply chain flow optimization. ### DisruptionAnalysisReques
t
 Request model for supply chain disruption analysis. ### FacilityLocationReques
t
 Request model for facility location optimization. ### NetworkOptimizationReques
t
 Request model for network design optimization. ### Confi
g
 ### Confi
g
 ### Confi
g
 ### Confi
g
 ### Confi
g
 ### RouteReques
t
 Request model for multimodal route planning. ### CompareRoutesReques
t
 Request model for route comparison. ### NetworkMetricsReques
t
 Request model for network metrics calculation. ### TrafficSimulationReques
t
 Request model for traffic simulation. ### EmissionsCalculationReques
t
 Request model for emissions calculation. ### EmissionsComparisonReques
t
 Request model for emissions comparison. ### Confi
g
 ### Confi
g
 ### Confi
g
 ### Confi
g
 ### Confi
g
 ### Confi
g
 ### get_last_mile_route
r
 `get_last_mile_router()` Dependency for last-mile router. ### get_delivery_schedule
r
 `get_delivery_scheduler(router: LastMileRouter)` Dependency for delivery scheduler. ### get_service_area_analyze
r
 `get_service_area_analyzer()` Dependency for service area analyzer. ### get_route_optimize
r
 `get_route_optimizer()` Dependency for route optimizer. ### get_fleet_manage
r
 `get_fleet_manager()` Dependency for fleet manager. ### get_vehicle_route
r
 `get_vehicle_router()` Dependency for vehicle router. ### get_supply_chain_mode
l
 `get_supply_chain_model()` Dependency for supply chain model. ### get_resilience_analyze
r
 `get_resilience_analyzer(model: SupplyChainModel)` Dependency for resilience analyzer. ### get_network_optimize
r
 `get_network_optimizer()` Dependency for network optimizer. ### get_facility_locato
r
 `get_facility_locator()` Dependency for facility locator. ### get_multimodal_planne
r
 `get_multimodal_planner()` Dependency for multimodal planner. ### get_network_analyze
r
 `get_network_analyzer()` Dependency for transportation network analyzer. ### get_traffic_simulato
r
 `get_traffic_simulator()` Dependency for traffic simulator. ### get_emissions_calculato
r
 `get_emissions_calculator()` Dependency for emissions calculator. ## Capabilities
 - **38 classes** for core functionality - **14 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-LOG/src/geo_infer_log/api` - **Type**: Directory Node 