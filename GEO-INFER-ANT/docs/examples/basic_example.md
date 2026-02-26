# Basic Example: Route Optimization on an H3 Grid

This example demonstrates using swarm agents and pheromone-based stigmergy to find efficient routes between points on an H3 hexagonal grid. The approach mirrors classical Ant Colony Optimization (ACO): agents traverse paths, deposit trail pheromone on good routes, and subsequent agents follow stronger trails.

## Problem Setup

We have a set of 10 geographic waypoints in the Seattle area. The goal is to find a short tour visiting all waypoints, using swarm-based route optimization rather than exact solvers.

```python
import numpy as np
import asyncio
from geo_infer_ant.core.stigmergy import PheromoneSystem
from geo_infer_ant.core.agent_base import SwarmAgent

# Define 10 waypoints (lat, lng) in the Seattle metro area
waypoints = np.array([
    [47.6062, -122.3321],  # Downtown Seattle
    [47.6205, -122.3493],  # Space Needle
    [47.6097, -122.3425],  # Pike Place Market
    [47.6526, -122.3482],  # Fremont
    [47.6588, -122.3130],  # University District
    [47.6232, -122.3126],  # Capitol Hill
    [47.5990, -122.3270],  # Pioneer Square
    [47.6145, -122.3145],  # First Hill
    [47.6686, -122.3840],  # Ballard
    [47.6390, -122.3561],  # Wallingford
])

n_waypoints = len(waypoints)
print(f"Optimizing route through {n_waypoints} waypoints")
```

## Building the Distance Matrix

Compute pairwise distances between all waypoints using the Haversine formula for geographic coordinates.

```python
def haversine_distance(p1: np.ndarray, p2: np.ndarray) -> float:
    """Compute distance in meters between two [lat, lng] points."""
    R = 6371000  # Earth radius in meters
    lat1, lon1 = np.radians(p1)
    lat2, lon2 = np.radians(p2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c

# Build distance matrix
distances = np.zeros((n_waypoints, n_waypoints))
for i in range(n_waypoints):
    for j in range(n_waypoints):
        if i != j:
            distances[i, j] = haversine_distance(waypoints[i], waypoints[j])

print(f"Distance matrix shape: {distances.shape}")
print(f"Max distance: {distances.max():.0f}m, Min nonzero: {distances[distances > 0].min():.0f}m")
```

## Configuring the Pheromone System

Set up a pheromone system with trail pheromone that agents deposit along their routes.

```python
pheromone = PheromoneSystem(
    spatial_resolution='h3_r8',
    pheromone_types=['trail'],
    bounds={
        'min_lat': 47.59, 'max_lat': 47.68,
        'min_lng': -122.40, 'max_lng': -122.30,
    },
    environmental_factors={
        'temperature': 15.0,
        'humidity': 70.0,
    },
)
```

## ACO Route Search

Implement the ACO loop: each ant constructs a tour, deposits pheromone proportional to tour quality, and pheromone evaporates between iterations.

```python
# ACO parameters
n_ants = 20
n_iterations = 50
alpha = 1.0          # Pheromone influence
beta = 2.0           # Distance heuristic influence
evaporation = 0.1    # Evaporation rate per iteration
q_factor = 1000.0    # Pheromone deposit scaling

# Pheromone matrix (edge-level, not spatial for this simplified example)
pheromone_matrix = np.ones((n_waypoints, n_waypoints)) * 0.1

# Heuristic: inverse distance
heuristic = np.zeros_like(distances)
for i in range(n_waypoints):
    for j in range(n_waypoints):
        if distances[i, j] > 0:
            heuristic[i, j] = 1.0 / distances[i, j]

best_tour = None
best_distance = float('inf')
distance_history = []

for iteration in range(n_iterations):
    tours = []
    tour_distances = []

    for ant in range(n_ants):
        # Construct a tour
        visited = [np.random.randint(n_waypoints)]
        unvisited = list(set(range(n_waypoints)) - set(visited))

        while unvisited:
            current = visited[-1]

            # Calculate transition probabilities
            probs = np.zeros(len(unvisited))
            for idx, next_city in enumerate(unvisited):
                tau = pheromone_matrix[current, next_city] ** alpha
                eta = heuristic[current, next_city] ** beta
                probs[idx] = tau * eta

            # Normalize probabilities
            prob_sum = probs.sum()
            if prob_sum > 0:
                probs /= prob_sum
            else:
                probs = np.ones(len(unvisited)) / len(unvisited)

            # Select next city
            choice_idx = np.random.choice(len(unvisited), p=probs)
            next_city = unvisited[choice_idx]

            visited.append(next_city)
            unvisited.remove(next_city)

        # Calculate tour distance (round trip)
        tour_dist = sum(
            distances[visited[i], visited[i + 1]]
            for i in range(len(visited) - 1)
        )
        tour_dist += distances[visited[-1], visited[0]]

        tours.append(visited)
        tour_distances.append(tour_dist)

    # Update best tour
    iteration_best_idx = np.argmin(tour_distances)
    if tour_distances[iteration_best_idx] < best_distance:
        best_distance = tour_distances[iteration_best_idx]
        best_tour = tours[iteration_best_idx]

    distance_history.append(best_distance)

    # Evaporate pheromone
    pheromone_matrix *= (1 - evaporation)

    # Deposit pheromone on all tours (amount inversely proportional to distance)
    for tour, dist in zip(tours, tour_distances):
        deposit = q_factor / dist
        for i in range(len(tour) - 1):
            pheromone_matrix[tour[i], tour[i + 1]] += deposit
            pheromone_matrix[tour[i + 1], tour[i]] += deposit
        # Close the loop
        pheromone_matrix[tour[-1], tour[0]] += deposit
        pheromone_matrix[tour[0], tour[-1]] += deposit

    if iteration % 10 == 0:
        print(f"Iteration {iteration}: best distance = {best_distance:.0f}m")

print(f"\nFinal best tour distance: {best_distance:.0f}m")
print(f"Tour order: {best_tour}")
```

## Depositing Results into the Spatial Pheromone System

After finding the best route, deposit trail pheromone along the path in the spatial pheromone system for other agents to follow.

```python
async def deposit_route():
    """Deposit pheromone along the best tour."""
    for i in range(len(best_tour)):
        current_idx = best_tour[i]
        location = waypoints[current_idx]

        # Deposit intensity proportional to position in tour
        intensity = 1.5 - (i / len(best_tour)) * 0.5

        await pheromone.deposit_pheromone(
            agent_id='route_optimizer',
            pheromone_type='trail',
            location=location,
            intensity=intensity,
        )

    # Get field statistics
    stats = pheromone.get_field_statistics('trail')
    print(f"Trail pheromone field: {stats.get('active_cells', 0)} active cells")
    print(f"Max concentration: {stats.get('max_concentration', 0):.3f}")

asyncio.run(deposit_route())
```

## Interpreting Results

The ACO algorithm converges to a near-optimal tour over iterations. Key observations:

- **Early iterations** show rapid improvement as pheromone accumulates on shorter edges.
- **Later iterations** show diminishing returns as the algorithm converges.
- The pheromone matrix reveals which edges are most favored, providing route recommendations beyond a single best tour.

```python
# Print convergence summary
improvement = distance_history[0] - distance_history[-1]
print(f"Total improvement: {improvement:.0f}m ({improvement / distance_history[0] * 100:.1f}%)")
print(f"Convergence: {distance_history[0]:.0f}m -> {distance_history[-1]:.0f}m")

# Show the named route
names = [
    "Downtown", "Space Needle", "Pike Place", "Fremont",
    "U-District", "Capitol Hill", "Pioneer Sq", "First Hill",
    "Ballard", "Wallingford",
]
route_names = [names[i] for i in best_tour]
print(f"Route: {' -> '.join(route_names)} -> {route_names[0]}")
```

## Expected Output

```
Optimizing route through 10 waypoints
Distance matrix shape: (10, 10)
Iteration 0: best distance = 18432m
Iteration 10: best distance = 14876m
Iteration 20: best distance = 13921m
Iteration 30: best distance = 13654m
Iteration 40: best distance = 13543m

Final best tour distance: 13543m
Route: Downtown -> Pike Place -> Pioneer Sq -> First Hill -> Capitol Hill -> ...
```

The exact output depends on random seed. Typical ACO convergence reduces total tour distance by 20-30% from initial random tours over 50 iterations with 20 ants.
