# Mobility Analysis with H3

This document explores how H3's unique properties make it particularly well-suited for mobility and movement pattern analysis, providing methodologies, examples, and best practices.

## Introduction

Movement data analysis is one of the most powerful applications of the H3 geospatial indexing system. The consistent neighbor relationships and uniform distance properties of hexagonal cells provide significant advantages for analyzing flows, trajectories, connectivity, and accessibility patterns.

## Advantages of H3 for Mobility Analysis

### Uniform Distance Properties

H3's hexagonal grid structure provides consistent distance relationships between neighboring cells. Unlike square grids where diagonal neighbors are ~1.4x farther than orthogonal neighbors, all six adjacent hexagons are equidistant from the center hexagon. This property makes H3 ideal for:

- Travel time calculations
- Service area delineation
- Flow pattern identification
- Isochrone generation

### Consistent Connectivity

The edge-sharing property of hexagons creates a consistent adjacency pattern, which is particularly valuable for:

- Network analysis
- Route optimization
- Accessibility modeling
- Movement flow visualization

### Multi-resolution Capability

H3's hierarchical structure enables analysis at multiple spatial scales, facilitating:

- Progressive refinement of movement corridors
- Hierarchical clustering of movement patterns
- Multi-scale accessibility analysis
- Computational optimization for large-scale mobility studies

## Core Movement Analysis Techniques

### Trajectory Binning

Converting raw GPS trajectories into sequences of H3 cells simplifies analysis and reduces computational complexity:

```python
# Python example: Convert GPS trajectory to H3 sequence
import h3
import pandas as pd

def trajectory_to_h3_sequence(points, resolution=9):
    """Convert a sequence of lat/lng points to H3 cell sequence."""
    h3_cells = [h3.latlng_to_cell(lat, lng, resolution) for lat, lng in points]
    
    # Remove consecutive duplicates (stationary periods)
    unique_sequence = []
    for cell in h3_cells:
        if not unique_sequence or unique_sequence[-1] != cell:
            unique_sequence.append(cell)
            
    return unique_sequence

# Example usage with trajectory data
trajectory_data = pd.read_csv('vehicle_trajectories.csv')
trajectories = {}

for vehicle_id, group in trajectory_data.groupby('vehicle_id'):
    points = list(zip(group['latitude'], group['longitude']))
    trajectories[vehicle_id] = trajectory_to_h3_sequence(points)
```

This binning approach:
- Reduces data volume while preserving movement patterns
- Creates a discrete representation amenable to pattern mining
- Normalizes trajectories for comparison
- Enables efficient storage and query of movement data

### Origin-Destination Analysis

H3 cells provide a natural binning structure for origin-destination matrices:

```python
# Python example: Generate OD matrix from movement data
def create_od_matrix(trajectories, time_window=None):
    """
    Create an origin-destination matrix from trajectory data.
    
    Parameters:
        trajectories: Dict of vehicle_id -> h3_sequence
        time_window: Optional time filter
    
    Returns:
        Dictionary with (origin, destination) tuples as keys and counts as values
    """
    od_matrix = {}
    
    for vehicle_id, h3_sequence in trajectories.items():
        if len(h3_sequence) < 2:
            continue
            
        # For simplicity, use first and last points
        # More sophisticated approaches could segment trajectories
        origin = h3_sequence[0]
        destination = h3_sequence[-1]
        
        od_pair = (origin, destination)
        od_matrix[od_pair] = od_matrix.get(od_pair, 0) + 1
    
    return od_matrix

# Aggregate to higher resolution for visualization
def aggregate_od_matrix(od_matrix, target_resolution=7):
    """Aggregate OD matrix to a coarser resolution."""
    aggregated = {}
    
    for (orig, dest), count in od_matrix.items():
        orig_parent = h3.cell_to_parent(orig, target_resolution)
        dest_parent = h3.cell_to_parent(dest, target_resolution)
        od_pair = (orig_parent, dest_parent)
        
        aggregated[od_pair] = aggregated.get(od_pair, 0) + count
    
    return aggregated
```

These OD matrices can reveal:
- Major movement corridors
- Commuting patterns
- Spatial interaction strength
- Underserved origin-destination pairs

### Flow Mapping

Visualizing movement between H3 cells:

```python
# Python example: Generate flow lines for visualization
def generate_flow_lines(od_matrix, min_count=10):
    """Generate GeoJSON flow lines from an OD matrix."""
    features = []
    
    for (origin, destination), count in od_matrix.items():
        if count < min_count:
            continue
            
        # Get centers of origin and destination cells
        origin_center = h3.cell_to_latlng(origin)
        dest_center = h3.cell_to_latlng(destination)
        
        # Create line feature
        feature = {
            "type": "Feature",
            "properties": {
                "origin": origin,
                "destination": destination,
                "count": count,
                "weight": min(1.0, count / 100)  # Normalize for visualization
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [origin_center[1], origin_center[0]],  # [lng, lat] format
                    [dest_center[1], dest_center[0]]
                ]
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }
```

These flow maps can be enhanced with:
- Line width proportional to flow volume
- Color coding by time of day
- Directional arrows
- Animated temporal patterns

### Movement Pattern Mining

Identifying recurring patterns in trajectory data:

```python
# Python example: Identify common movement sequences
from collections import Counter

def identify_common_sequences(trajectories, min_length=3, min_count=5):
    """Identify common movement sequences in trajectory data."""
    # Extract all subsequences of at least min_length
    all_subsequences = []
    
    for vehicle_id, h3_sequence in trajectories.items():
        for i in range(len(h3_sequence) - min_length + 1):
            subsequence = tuple(h3_sequence[i:i+min_length])
            all_subsequences.append(subsequence)
    
    # Count occurrences of each subsequence
    sequence_counts = Counter(all_subsequences)
    
    # Filter by minimum occurrence threshold
    common_sequences = {seq: count for seq, count in sequence_counts.items() 
                        if count >= min_count}
    
    return common_sequences
```

This approach can reveal:
- Common routes
- Typical travel patterns
- Anomalous movements
- Recurring mobility behaviors

## Advanced Mobility Metrics

### Accessibility Analysis

Measuring accessibility to services or opportunities:

```python
# Python example: Calculate accessibility to services
def calculate_accessibility(population_cells, service_cells, max_distance=3):
    """
    Calculate accessibility to services for population cells.
    
    Parameters:
        population_cells: Dict of h3_index -> population count
        service_cells: Dict of h3_index -> service capacity
        max_distance: Maximum H3 grid distance to consider
    
    Returns:
        Dict of h3_index -> accessibility score
    """
    accessibility = {}
    
    for pop_cell, population in population_cells.items():
        if population == 0:
            continue
            
        # Get all service cells within max_distance
        nearby_cells = h3.grid_disk(pop_cell, max_distance)
        
        # Calculate accessibility with distance decay
        access_score = 0
        for nearby_cell in nearby_cells:
            if nearby_cell in service_cells:
                distance = h3.grid_distance(pop_cell, nearby_cell)
                # Simple distance decay function (1/d^2)
                decay_factor = 1.0 / max(1, distance * distance)
                access_score += service_cells[nearby_cell] * decay_factor
        
        # Normalize by population
        accessibility[pop_cell] = access_score / population
    
    return accessibility
```

This methodology can be extended to:
- Multi-modal accessibility
- Temporal accessibility variations
- Comparative accessibility analysis
- Equity analysis

### Movement Entropy

Measuring predictability and diversity of movement patterns:

```python
# Python example: Calculate movement entropy
import numpy as np
import math

def calculate_movement_entropy(trajectories):
    """Calculate entropy of movement patterns for each origin cell."""
    # Create origin -> destinations mapping
    origin_destinations = {}
    
    for vehicle_id, h3_sequence in trajectories.items():
        for i in range(len(h3_sequence) - 1):
            origin = h3_sequence[i]
            destination = h3_sequence[i + 1]
            
            if origin not in origin_destinations:
                origin_destinations[origin] = []
            
            origin_destinations[origin].append(destination)
    
    # Calculate entropy for each origin
    entropy = {}
    for origin, destinations in origin_destinations.items():
        # Count occurrences of each destination
        dest_counts = Counter(destinations)
        total = len(destinations)
        
        # Calculate entropy using Shannon formula
        h = 0
        for dest, count in dest_counts.items():
            probability = count / total
            h -= probability * math.log2(probability)
        
        entropy[origin] = h
    
    return entropy
```

Higher entropy values indicate:
- More diverse and unpredictable movement patterns
- Areas with multiple common destinations
- Lower routine behavior

### Isolation Metrics

Measuring spatial isolation based on movement patterns:

```python
# Python example: Calculate isolation metrics
def calculate_isolation(od_matrix):
    """Calculate isolation metrics based on movement patterns."""
    # Create dictionaries to track inbound and outbound movements
    inbound = {}
    outbound = {}
    
    for (origin, destination), count in od_matrix.items():
        if origin not in outbound:
            outbound[origin] = 0
        outbound[origin] += count
        
        if destination not in inbound:
            inbound[destination] = 0
        inbound[destination] += count
    
    # Calculate the ratio of internal movements
    isolation = {}
    for cell in set(inbound.keys()) | set(outbound.keys()):
        internal_count = od_matrix.get((cell, cell), 0)
        total_outbound = outbound.get(cell, 0)
        total_inbound = inbound.get(cell, 0)
        
        if total_outbound + total_inbound > 0:
            isolation[cell] = internal_count / (total_outbound + total_inbound)
        else:
            isolation[cell] = 0
    
    return isolation
```

This metric identifies:
- Self-contained communities
- Isolated neighborhoods
- Mobility-constrained areas
- Transportation barriers

## Temporal Movement Analysis

### Time-based Binning

Analyzing movement patterns across time periods:

```python
# Python example: Time-based movement analysis
def analyze_temporal_patterns(trajectory_data, resolution=9):
    """Analyze movement patterns by time of day."""
    # Define time bins
    time_bins = {
        'morning': (6, 10),   # 6 AM - 10 AM
        'midday': (10, 15),   # 10 AM - 3 PM
        'evening': (15, 19),  # 3 PM - 7 PM
        'night': (19, 6)      # 7 PM - 6 AM
    }
    
    # Create time-specific OD matrices
    temporal_od = {period: {} for period in time_bins}
    
    for _, row in trajectory_data.iterrows():
        hour = row['timestamp'].hour
        lat, lng = row['latitude'], row['longitude']
        vehicle_id = row['vehicle_id']
        h3_cell = h3.latlng_to_cell(lat, lng, resolution)
        
        # Determine which time period this falls into
        for period, (start, end) in time_bins.items():
            if start <= hour < end or (period == 'night' and (hour >= start or hour < end)):
                # Add to the appropriate temporal OD matrix
                # Implementation would need to track previous positions
                # This is a simplified placeholder
                pass
    
    return temporal_od
```

This approach enables:
- Peak vs. off-peak pattern comparison
- Weekday vs. weekend analysis
- Seasonal variation detection
- Temporal anomaly identification

### Dwell Time Analysis

Measuring how long objects remain in specific areas:

```python
# Python example: Calculate dwell times
def calculate_dwell_times(trajectory_data, resolution=9):
    """Calculate dwell times in each H3 cell."""
    dwell_times = {}
    
    # Group by vehicle ID
    for vehicle_id, group in trajectory_data.groupby('vehicle_id'):
        # Sort by timestamp
        group = group.sort_values('timestamp')
        
        # Convert to H3 cells with timestamps
        cell_times = []
        for _, row in group.iterrows():
            lat, lng = row['latitude'], row['longitude']
            h3_cell = h3.latlng_to_cell(lat, lng, resolution)
            timestamp = row['timestamp']
            cell_times.append((h3_cell, timestamp))
        
        # Calculate time spent in each cell
        for i in range(len(cell_times) - 1):
            current_cell, current_time = cell_times[i]
            next_cell, next_time = cell_times[i + 1]
            
            # If stayed in same cell
            if current_cell == next_cell:
                duration = (next_time - current_time).total_seconds() / 60  # minutes
                
                if current_cell not in dwell_times:
                    dwell_times[current_cell] = []
                
                dwell_times[current_cell].append(duration)
    
    # Calculate statistics for each cell
    dwell_stats = {}
    for cell, durations in dwell_times.items():
        dwell_stats[cell] = {
            'mean': np.mean(durations),
            'median': np.median(durations),
            'min': np.min(durations),
            'max': np.max(durations),
            'count': len(durations)
        }
    
    return dwell_stats
```

Dwell time analysis reveals:
- Activity hotspots
- Traffic congestion areas
- Popular destinations
- Potential service locations

## Case Studies

### Ride-sharing Service Optimization

Uber has leveraged H3 for ride-sharing optimization through several key analyses:

1. **Supply-Demand Balancing**
   ```python
   # Python example: Calculate supply-demand balance
   def calculate_balance(driver_locations, rider_requests, resolution=8):
       """Calculate supply-demand balance by H3 cell."""
       # Count drivers per cell
       driver_counts = Counter([
           h3.latlng_to_cell(lat, lng, resolution) 
           for lat, lng in driver_locations
       ])
       
       # Count ride requests per cell
       request_counts = Counter([
           h3.latlng_to_cell(lat, lng, resolution) 
           for lat, lng in rider_requests
       ])
       
       # Calculate balance (positive = excess supply, negative = excess demand)
       balance = {}
       all_cells = set(driver_counts.keys()) | set(request_counts.keys())
       
       for cell in all_cells:
           supply = driver_counts.get(cell, 0)
           demand = request_counts.get(cell, 0)
           balance[cell] = supply - demand
       
       return balance
   ```

2. **Dynamic Pricing Zones**
   - H3 cells provide natural boundaries for surge pricing
   - Consistent hexagonal shape makes pricing zones intuitive
   - Hierarchical structure enables adaptive zone sizing based on density

3. **Driver Positioning Recommendations**
   - K-ring analyses identify areas with high demand but low supply
   - Hierarchical data aggregation enables real-time model serving
   - Cell-based movement patterns predict future demand hotspots

### Urban Transportation Planning

Cities can utilize H3 for transportation planning:

1. **Mode Share Analysis**
   ```python
   # Python example: Calculate transportation mode share
   def calculate_mode_share(trip_data, resolution=8):
       """Calculate transportation mode share by H3 cell."""
       # Group trips by origin cell and transportation mode
       mode_counts = {}
       
       for _, trip in trip_data.iterrows():
           origin_lat, origin_lng = trip['origin_lat'], trip['origin_lng']
           mode = trip['mode']  # e.g., 'car', 'transit', 'bike', 'walk'
           
           origin_cell = h3.latlng_to_cell(origin_lat, origin_lng, resolution)
           
           if origin_cell not in mode_counts:
               mode_counts[origin_cell] = Counter()
           
           mode_counts[origin_cell][mode] += 1
       
       # Calculate mode share percentages
       mode_share = {}
       for cell, counts in mode_counts.items():
           total = sum(counts.values())
           mode_share[cell] = {mode: count/total for mode, count in counts.items()}
       
       return mode_share
   ```

2. **Transit Coverage Analysis**
   - H3's k-ring operations efficiently identify areas within walking distance of transit
   - Multi-resolution analysis highlights coverage gaps at different scales
   - Hexagonal binning creates natural service areas for transit planning

3. **Infrastructure Investment Prioritization**
   - Flow mapping reveals high-volume corridors
   - Accessibility metrics identify underserved areas
   - Temporal analysis highlights peak-hour bottlenecks

### Supply Chain Optimization

Logistics companies use H3 to optimize supply chains:

1. **Warehouse Placement**
   ```python
   # Python example: Optimize warehouse placement
   def optimize_warehouse_placement(delivery_locations, n_warehouses=5, resolution=7):
       """Find optimal warehouse locations using H3-based clustering."""
       # Bin delivery locations into H3 cells
       delivery_cells = Counter([
           h3.latlng_to_cell(lat, lng, resolution) 
           for lat, lng in delivery_locations
       ])
       
       # Convert to weighted centroids for clustering
       weighted_points = []
       for cell, count in delivery_cells.items():
           lat, lng = h3.cell_to_latlng(cell)
           for _ in range(count):
               weighted_points.append((lat, lng))
       
       # Use K-means clustering to find optimal locations
       # (Simplified - in practice, would use actual K-means)
       
       return optimal_locations
   ```

2. **Route Optimization**
   - H3 grid networks simplify routing problems
   - Hierarchical structure enables multi-scale route planning
   - Cell-based demand forecasting improves delivery efficiency

3. **Service Territory Design**
   - Equal-sized hexagons create balanced service territories
   - Compaction operations optimize territory boundaries
   - Multi-resolution approach balances workload across territories

## Integration with Machine Learning

### Movement Feature Engineering

H3 cells provide a natural structure for generating features for mobility models:

```python
# Python example: Generate features for mobility prediction
def generate_mobility_features(trajectories, resolution=9):
    """Generate features for mobility prediction models."""
    features = {}
    
    for vehicle_id, h3_sequence in trajectories.items():
        for i in range(len(h3_sequence) - 1):
            origin = h3_sequence[i]
            
            # Skip if we've already processed this origin
            if origin in features:
                continue
                
            # Get surrounding context (k-ring)
            surrounding_cells = h3.grid_disk(origin, 1)
            
            # Count transitions to each neighbor
            transitions = Counter(h3_sequence[i+1] for i in range(len(h3_sequence)-1) 
                                 if h3_sequence[i] == origin)
            
            # Calculate transition probabilities
            total_transitions = sum(transitions.values())
            transition_probs = {dest: count/total_transitions 
                               for dest, count in transitions.items()}
            
            # Create feature vector
            feature_vector = []
            
            # Add transition probabilities for each neighbor
            for neighbor in surrounding_cells:
                feature_vector.append(transition_probs.get(neighbor, 0))
            
            # Add additional features (could include time of day, etc.)
            # ...
            
            features[origin] = feature_vector
    
    return features
```

### Spatial-Temporal Models

H3's structure is particularly well-suited for spatial-temporal modeling:

```python
# Python example: Prepare data for spatial-temporal model
def prepare_st_model_data(trajectory_data, resolution=9, time_steps=3):
    """Prepare data for a spatial-temporal model."""
    # Group trajectories by time bins
    time_binned_data = {}
    
    for timestamp, group in trajectory_data.groupby(pd.Grouper(key='timestamp', freq='1H')):
        cell_counts = Counter([
            h3.latlng_to_cell(row['latitude'], row['longitude'], resolution)
            for _, row in group.iterrows()
        ])
        time_binned_data[timestamp] = cell_counts
    
    # Sort time bins
    sorted_times = sorted(time_binned_data.keys())
    
    # Create sequences for each cell
    cell_sequences = {}
    all_cells = set()
    
    for t in sorted_times:
        all_cells.update(time_binned_data[t].keys())
    
    for cell in all_cells:
        cell_sequences[cell] = [
            time_binned_data[t].get(cell, 0) for t in sorted_times
        ]
    
    # Create sliding windows for sequence prediction
    model_data = []
    for cell, sequence in cell_sequences.items():
        for i in range(len(sequence) - time_steps):
            x = sequence[i:i+time_steps]
            y = sequence[i+time_steps]
            
            # Add spatial context from neighbors
            neighbors = h3.grid_disk(cell, 1) - {cell}
            neighbor_features = []
            
            for neighbor in neighbors:
                if neighbor in cell_sequences:
                    neighbor_seq = cell_sequences[neighbor]
                    if i+time_steps < len(neighbor_seq):
                        neighbor_features.extend(neighbor_seq[i:i+time_steps])
                    else:
                        neighbor_features.extend([0] * time_steps)
                else:
                    neighbor_features.extend([0] * time_steps)
            
            model_data.append((cell, x + neighbor_features, y))
    
    return model_data
```

### Mobility Graph Networks

H3 provides a natural structure for graph-based mobility modeling:

```python
# Python example: Create mobility graph from trajectory data
def create_mobility_graph(trajectories):
    """Create a graph representation of mobility patterns."""
    # Count transitions between cells
    edges = Counter()
    
    for vehicle_id, h3_sequence in trajectories.items():
        for i in range(len(h3_sequence) - 1):
            origin = h3_sequence[i]
            destination = h3_sequence[i + 1]
            
            if origin != destination:  # Ignore self-loops for simplicity
                edges[(origin, destination)] += 1
    
    # Create networkx graph
    import networkx as nx
    G = nx.DiGraph()
    
    # Add nodes (H3 cells)
    all_cells = set()
    for (origin, destination), _ in edges.items():
        all_cells.add(origin)
        all_cells.add(destination)
    
    for cell in all_cells:
        # Add node with geographic properties
        lat, lng = h3.cell_to_latlng(cell)
        G.add_node(cell, latitude=lat, longitude=lng)
    
    # Add edges with weights
    for (origin, destination), count in edges.items():
        G.add_edge(origin, destination, weight=count)
    
    return G
```

These graph representations enable:
- Community detection to identify mobility regions
- Centrality measures to find critical corridors
- Path analysis for flow optimization
- Graph neural networks for predictive modeling

## Best Practices for Mobility Analysis with H3

### Resolution Selection

The choice of H3 resolution significantly impacts mobility analysis:

| Resolution | Approximate Cell Size | Typical Mobility Applications |
|------------|----------------------|------------------------------|
| 7 | 1.22 km | Regional transportation planning |
| 8 | 461 m | City-level traffic analysis |
| 9 | 174 m | Neighborhood-level movement patterns |
| 10 | 66 m | Detailed street-level flow analysis |
| 11 | 25 m | Pedestrian movement analysis |

Guidelines for resolution selection:
1. **Match to movement speed**: Higher resolutions for slower movement (walking), lower for faster (driving)
2. **Consider data volume**: Each resolution step increases data volume by ~7x
3. **Account for GPS accuracy**: Resolution should not exceed the accuracy of source data
4. **Align with analysis goals**: Strategic planning can use coarser resolutions than operational analysis

### Data Processing Pipelines

Efficient mobility data pipelines with H3:

1. **Ingestion**
   - Convert raw GPS points to H3 indices on ingestion
   - Store both raw coordinates and H3 indices for flexibility
   - Consider multi-resolution storage for different analysis needs

2. **Processing**
   - Use hierarchical aggregation for scalable processing
   - Leverage H3's compact_cellsion capabilities for storage efficiency
   - Process at the finest resolution needed, then aggregate as required

3. **Analysis**
   - Start with coarse resolution exploratory analysis
   - Drill down to finer resolutions for specific areas of interest
   - Leverage H3's consistent properties for statistical analysis

4. **Visualization**
   - Use resolution appropriate to the zoom level
   - Leverage hierarchical structure for adaptive visualizations
   - Consider visual saliency when choosing display resolution

### Performance Optimization

Techniques for optimizing H3-based mobility analysis:

1. **Indexing Strategies**
   - Use hexagon multi-resolution indexing for spatial queries
   - Create compound indexes for spatial-temporal queries
   - Consider specialized spatial indexes for database implementations

2. **Distributed Processing**
   - H3 cells provide natural partitioning keys for parallel processing
   - Use resolution hierarchy for MapReduce-style aggregations
   - Implement locality-aware processing to leverage spatial coherence

3. **Approximation Techniques**
   - Use compact_cellsed representations for large spatial extents
   - Implement progressive refinement for interactive applications
   - Consider statistical sampling for massive trajectory datasets

## Conclusion

H3's unique properties make it exceptionally well-suited for mobility and movement pattern analysis. The consistent neighbor relationships, uniform distance properties, and hierarchical structure provide a solid foundation for understanding, visualizing, and predicting how people and goods move through space.

By leveraging H3 for mobility analysis, organizations can gain deeper insights into movement patterns, optimize transportation networks, and develop more effective mobility solutions.

## References

1. [Uber Engineering Blog: H3 for Movement Analysis](https://www.uber.com/blog/h3/)
2. [H3 Documentation: Movement Analysis](https://h3geo.org/docs/highlights/movement/)
3. [Mobility Data Specification](https://github.com/openmobilityfoundation/mobility-data-specification)
4. [CARTO Mobility Analysis with H3](https://carto.com/blog/mobility-analysis-with-h3/)
5. [Traffic Analysis with H3](https://docs.h3geo.org/tutorials/traffic-analysis/) 