# utils
 ## Overview
 This directory contains utils components. It includes 4 Python modules. ## Components
 ### conversio
n
.py Conversion utility functions for GEO-INFER-LOG. **Functions**: `km_to_miles`, `miles_to_km`, `meters_to_feet`, `feet_to_meters`, `km_per_hour_to_mph`, `mph_to_km_per_hour`, `liters_to_gallons`, `gallons_to_liters`, `kg_to_pounds`, `pounds_to_kg`, `cubic_meters_to_cubic_feet`, `cubic_feet_to_cubic_meters`, `celsius_to_fahrenheit`, `fahrenheit_to_celsius`, `minutes_to_hours`, `hours_to_minutes` ### ge
o
.py Geographic utility functions for GEO-INFER-LOG. **Functions**: `haversine_distance`, `get_bbox`, `coords_to_geojson`, `points_to_gdf`, `route_to_linestring`, `create_buffer`, `calculate_route_distance`, `get_centroid`, `within_distance` ### optimizatio
n
.py Optimization utility functions for GEO-INFER-LOG. **Functions**: `solve_tsp`, `solve_vrp`, `distance_callback`, `time_callback`, `distance_callback`, `time_callback`, `demand_callback` ### visualizatio
n
.py Visualization utility functions for GEO-INFER-LOG. **Functions**: `plot_route`, `plot_network`, `plot_service_area`, `create_interactive_map` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 