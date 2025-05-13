"""
Transportation planning components for the GEO-INFER-LOG module.

This module provides classes for multimodal transportation planning,
transportation network analysis, and emissions calculation.
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
from typing import Dict, List, Optional, Tuple, Union
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt

from geo_infer_log.models.schemas import VehicleType, FuelType, Vehicle, Route


class MultiModalPlanner:
    """Plans and optimizes multimodal transportation."""
    
    def __init__(self):
        """Initialize a multimodal transportation planner."""
        self.networks = {}  # mode -> network graph
        self.transfer_points = []  # List of transfer points between modes
    
    def load_network(self, mode: str, network_file: str) -> None:
        """Load a transportation network for a specific mode.
        
        Args:
            mode: Transportation mode
            network_file: Path to network file
        """
        # Load network from file
        network = nx.read_gpickle(network_file)
        self.networks[mode] = network
    
    def add_transfer_point(self, 
                          location: Tuple[float, float],
                          name: str,
                          modes: List[str],
                          transfer_time: Dict[Tuple[str, str], int]) -> None:
        """Add a transfer point between transportation modes.
        
        Args:
            location: (lon, lat) of transfer point
            name: Name of transfer point
            modes: List of modes available at this point
            transfer_time: Dict of (from_mode, to_mode) -> transfer time in minutes
        """
        transfer_point = {
            "location": location,
            "name": name,
            "modes": modes,
            "transfer_time": transfer_time
        }
        self.transfer_points.append(transfer_point)
        
        # Connect transfer point to mode networks
        for mode in modes:
            if mode in self.networks:
                # Find nearest node in the mode network
                # This is a simplified placeholder
                pass
    
    def plan_route(self,
                  origin: Tuple[float, float],
                  destination: Tuple[float, float],
                  allowed_modes: List[str],
                  preferences: Dict = None) -> Dict:
        """Plan a multimodal route between origin and destination.
        
        Args:
            origin: (lon, lat) of origin
            destination: (lon, lat) of destination
            allowed_modes: List of allowed transportation modes
            preferences: Dict of routing preferences
            
        Returns:
            Dictionary with route information
        """
        if not preferences:
            preferences = {
                "cost_weight": 1.0,
                "time_weight": 1.0,
                "emissions_weight": 1.0,
                "transfers_weight": 1.0
            }
        
        # Build multimodal graph
        multimodal_graph = self._build_multimodal_graph(allowed_modes)
        
        # Find nearest nodes to origin and destination
        origin_nodes = {}
        destination_nodes = {}
        
        for mode in allowed_modes:
            if mode in self.networks:
                # Find nearest nodes in each mode network
                # This is a simplified placeholder
                origin_nodes[mode] = list(self.networks[mode].nodes())[0]
                destination_nodes[mode] = list(self.networks[mode].nodes())[-1]
        
        # Find optimal path in multimodal graph
        # This is a simplified placeholder implementation
        
        # Prepare route segments
        segments = [
            {
                "mode": "car",
                "origin": origin,
                "destination": (8.6821, 50.1109),  # Frankfurt
                "distance": 150,
                "time": 90,
                "cost": 45,
                "emissions": 24
            },
            {
                "mode": "train",
                "origin": (8.6821, 50.1109),  # Frankfurt
                "destination": destination,
                "distance": 200,
                "time": 120,
                "cost": 60,
                "emissions": 10
            }
        ]
        
        # Calculate totals
        total_distance = sum(segment["distance"] for segment in segments)
        total_time = sum(segment["time"] for segment in segments)
        total_cost = sum(segment["cost"] for segment in segments)
        total_emissions = sum(segment["emissions"] for segment in segments)
        
        return {
            "segments": segments,
            "total_distance": total_distance,
            "total_time": total_time,
            "total_cost": total_cost,
            "total_emissions": total_emissions,
            "num_transfers": len(segments) - 1
        }
    
    def _build_multimodal_graph(self, modes: List[str]) -> nx.DiGraph:
        """Build a multimodal graph combining specified mode networks.
        
        Args:
            modes: List of transportation modes to include
            
        Returns:
            Multimodal directed graph
        """
        # Create a new graph for multimodal network
        multimodal_graph = nx.DiGraph()
        
        # Add all mode networks
        for mode in modes:
            if mode in self.networks:
                for node, data in self.networks[mode].nodes(data=True):
                    multimodal_graph.add_node(f"{mode}_{node}", **data, mode=mode)
                
                for u, v, data in self.networks[mode].edges(data=True):
                    multimodal_graph.add_edge(f"{mode}_{u}", f"{mode}_{v}", **data, mode=mode)
        
        # Add transfer edges between networks
        for transfer in self.transfer_points:
            modes = transfer["modes"]
            for from_mode in modes:
                for to_mode in modes:
                    if from_mode != to_mode:
                        # Add edge between nearest nodes in the two mode networks
                        # This is a simplified placeholder
                        transfer_time = transfer["transfer_time"].get((from_mode, to_mode), 15)
                        pass
        
        return multimodal_graph
    
    def compare_routes(self,
                      origin: Tuple[float, float],
                      destination: Tuple[float, float],
                      mode_combinations: List[List[str]]) -> pd.DataFrame:
        """Compare different multimodal routes between origin and destination.
        
        Args:
            origin: (lon, lat) of origin
            destination: (lon, lat) of destination
            mode_combinations: List of mode combinations to compare
            
        Returns:
            DataFrame with route comparisons
        """
        comparisons = []
        
        for modes in mode_combinations:
            route = self.plan_route(origin, destination, modes)
            
            comparisons.append({
                "modes": "-".join(modes),
                "total_distance": route["total_distance"],
                "total_time": route["total_time"],
                "total_cost": route["total_cost"],
                "total_emissions": route["total_emissions"],
                "num_transfers": route["num_transfers"]
            })
        
        return pd.DataFrame(comparisons)


class TransportationNetworkAnalyzer:
    """Analyzes transportation networks and flows."""
    
    def __init__(self):
        """Initialize a transportation network analyzer."""
        self.network = None
        self.flow_data = None
    
    def load_network(self, network_file: str) -> None:
        """Load a transportation network from a file.
        
        Args:
            network_file: Path to network file
        """
        self.network = nx.read_gpickle(network_file)
    
    def load_flow_data(self, flow_file: str) -> None:
        """Load transportation flow data from a file.
        
        Args:
            flow_file: Path to flow data file
        """
        # Load flow data from file
        # This is a simplified placeholder
        self.flow_data = pd.DataFrame()
    
    def calculate_network_metrics(self) -> Dict:
        """Calculate metrics for the transportation network.
        
        Returns:
            Dictionary with network metrics
        """
        if not self.network:
            raise ValueError("Network must be loaded before calculating metrics")
            
        # Calculate basic network metrics
        metrics = {
            "num_nodes": self.network.number_of_nodes(),
            "num_edges": self.network.number_of_edges(),
            "density": nx.density(self.network),
            "diameter": nx.diameter(self.network) if nx.is_strongly_connected(self.network) else float('inf'),
            "average_shortest_path_length": nx.average_shortest_path_length(self.network) 
                if nx.is_strongly_connected(self.network) else float('inf'),
            "average_degree": sum(dict(self.network.degree()).values()) / self.network.number_of_nodes()
                if self.network.number_of_nodes() > 0 else 0
        }
        
        # Calculate centrality measures
        centrality = nx.betweenness_centrality(self.network)
        metrics["max_betweenness_centrality"] = max(centrality.values()) if centrality else 0
        metrics["average_betweenness_centrality"] = sum(centrality.values()) / len(centrality) if centrality else 0
        
        return metrics
    
    def identify_critical_links(self, top_n: int = 10) -> List[Tuple[str, str]]:
        """Identify critical links in the transportation network.
        
        Args:
            top_n: Number of critical links to identify
            
        Returns:
            List of critical link tuples (u, v)
        """
        if not self.network:
            raise ValueError("Network must be loaded before identifying critical links")
            
        # Calculate edge betweenness centrality
        edge_centrality = nx.edge_betweenness_centrality(self.network)
        
        # Sort by centrality and return top links
        critical_links = sorted(edge_centrality.items(), key=lambda x: x[1], reverse=True)
        return [link for link, _ in critical_links[:top_n]]
    
    def analyze_flow(self) -> Dict:
        """Analyze transportation flow in the network.
        
        Returns:
            Dictionary with flow analysis results
        """
        if not self.network or not self.flow_data:
            raise ValueError("Network and flow data must be loaded before analysis")
            
        # Analyze flow patterns
        # This is a simplified placeholder
        
        return {
            "total_flow": 0,
            "max_flow": 0,
            "congestion_points": []
        }
    
    def visualize_network(self, 
                         with_flow: bool = False, 
                         highlight_critical: bool = False) -> None:
        """Visualize the transportation network.
        
        Args:
            with_flow: Whether to visualize flow data
            highlight_critical: Whether to highlight critical links
        """
        if not self.network:
            raise ValueError("Network must be loaded before visualization")
            
        # Create a plot
        plt.figure(figsize=(12, 10))
        
        # Draw the network
        pos = nx.spring_layout(self.network)
        nx.draw_networkx_nodes(self.network, pos, node_size=50)
        nx.draw_networkx_edges(self.network, pos, width=1, alpha=0.5)
        
        if highlight_critical:
            # Highlight critical links
            critical_links = self.identify_critical_links()
            nx.draw_networkx_edges(self.network, pos, edgelist=critical_links, 
                                  width=3, edge_color='red')
        
        if with_flow and self.flow_data is not None:
            # Visualize flow data
            # This is a simplified placeholder
            pass
        
        plt.title("Transportation Network")
        plt.axis('off')
        plt.tight_layout()


class TrafficSimulator:
    """Simulates traffic patterns and congestion."""
    
    def __init__(self, network: Optional[nx.DiGraph] = None):
        """Initialize a traffic simulator.
        
        Args:
            network: Transportation network graph
        """
        self.network = network
        self.time_periods = []
        self.edge_speeds = {}  # (u, v) -> speed by time period
    
    def load_network(self, network_file: str) -> None:
        """Load a transportation network from a file.
        
        Args:
            network_file: Path to network file
        """
        self.network = nx.read_gpickle(network_file)
    
    def set_time_periods(self, periods: List[str]) -> None:
        """Set time periods for traffic simulation.
        
        Args:
            periods: List of time period labels
        """
        self.time_periods = periods
        
        # Initialize speeds for all edges and time periods
        if self.network:
            for u, v in self.network.edges():
                self.edge_speeds[(u, v)] = {period: 0 for period in periods}
    
    def set_edge_speeds(self, 
                       edge: Tuple[str, str], 
                       speeds: Dict[str, float]) -> None:
        """Set speeds for an edge by time period.
        
        Args:
            edge: Edge tuple (u, v)
            speeds: Dict of time period -> speed in km/h
        """
        if edge not in self.network.edges():
            raise ValueError(f"Edge {edge} not in network")
            
        for period, speed in speeds.items():
            if period not in self.time_periods:
                raise ValueError(f"Time period {period} not defined")
                
            self.edge_speeds[edge][period] = speed
    
    def simulate_traffic(self, 
                        origin: str, 
                        destination: str,
                        departure_time: str) -> Dict:
        """Simulate traffic for a route from origin to destination.
        
        Args:
            origin: Origin node
            destination: Destination node
            departure_time: Departure time period
            
        Returns:
            Dictionary with simulation results
        """
        if not self.network:
            raise ValueError("Network must be loaded before simulation")
            
        if departure_time not in self.time_periods:
            raise ValueError(f"Time period {departure_time} not defined")
        
        # Create a copy of the network with speeds for the departure time
        temp_network = self.network.copy()
        
        for u, v, data in temp_network.edges(data=True):
            speed = self.edge_speeds.get((u, v), {}).get(departure_time, data.get('free_flow_speed', 50))
            
            # Calculate travel time based on speed and distance
            distance = data.get('distance', 1)
            travel_time = (distance / speed) * 60 if speed > 0 else float('inf')  # minutes
            
            temp_network[u][v]['travel_time'] = travel_time
        
        # Find shortest path based on travel time
        try:
            path = nx.shortest_path(temp_network, origin, destination, weight='travel_time')
            travel_time = nx.shortest_path_length(temp_network, origin, destination, weight='travel_time')
            distance = sum(temp_network[u][v].get('distance', 0) for u, v in zip(path[:-1], path[1:]))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            path = []
            travel_time = float('inf')
            distance = 0
        
        return {
            "path": path,
            "travel_time": travel_time,
            "distance": distance,
            "departure_time": departure_time,
            "estimated_arrival_time": None  # Would calculate based on departure time
        }
    
    def analyze_congestion(self, 
                          time_period: str = None,
                          congestion_threshold: float = 0.7) -> Dict:
        """Analyze network congestion.
        
        Args:
            time_period: Time period to analyze (None for all periods)
            congestion_threshold: Threshold ratio of flow/capacity for congestion
            
        Returns:
            Dictionary with congestion analysis results
        """
        if not self.network:
            raise ValueError("Network must be loaded before analysis")
            
        periods = [time_period] if time_period else self.time_periods
        
        congestion_results = {}
        for period in periods:
            # Calculate congestion metrics
            # This is a simplified placeholder
            congestion_results[period] = {
                "congested_edges": [],
                "congestion_ratio": 0.0
            }
        
        return congestion_results


class EmissionsCalculator:
    """Calculates transportation emissions."""
    
    def __init__(self):
        """Initialize an emissions calculator."""
        # Default emissions factors by vehicle type and fuel type (kg CO2e per km)
        self.emissions_factors = {
            (VehicleType.TRUCK, FuelType.DIESEL): 0.9,
            (VehicleType.TRUCK, FuelType.ELECTRIC): 0.2,
            (VehicleType.VAN, FuelType.DIESEL): 0.5,
            (VehicleType.VAN, FuelType.ELECTRIC): 0.15,
            (VehicleType.CAR, FuelType.GASOLINE): 0.2,
            (VehicleType.CAR, FuelType.ELECTRIC): 0.1,
            (VehicleType.BIKE, FuelType.ELECTRIC): 0.01,
            (VehicleType.BIKE, None): 0.0,
            (VehicleType.TRAIN, FuelType.ELECTRIC): 0.05,
            (VehicleType.SHIP, FuelType.DIESEL): 0.4,
            (VehicleType.AIRPLANE, FuelType.JET_FUEL): 2.0
        }
    
    def set_emissions_factor(self, 
                           vehicle_type: VehicleType, 
                           fuel_type: Optional[FuelType],
                           factor: float) -> None:
        """Set an emissions factor for a vehicle and fuel type.
        
        Args:
            vehicle_type: Type of vehicle
            fuel_type: Type of fuel (None for non-motorized)
            factor: Emissions factor in kg CO2e per km
        """
        self.emissions_factors[(vehicle_type, fuel_type)] = factor
    
    def calculate_route_emissions(self, 
                               vehicle: Vehicle, 
                               distance: float,
                               load_factor: float = 1.0,
                               terrain_factor: float = 1.0) -> float:
        """Calculate emissions for a route with a specific vehicle.
        
        Args:
            vehicle: Vehicle to use for calculation
            distance: Route distance in km
            load_factor: Factor for vehicle load (1.0 = full load)
            terrain_factor: Factor for terrain (1.0 = flat terrain)
            
        Returns:
            Emissions in kg CO2e
        """
        # Get base emissions factor
        base_factor = self.emissions_factors.get(
            (vehicle.type, vehicle.fuel_type),
            vehicle.emissions_per_km  # Fallback to vehicle's own factor
        )
        
        # Apply adjustment factors
        adjusted_factor = base_factor * load_factor * terrain_factor
        
        # Calculate total emissions
        emissions = distance * adjusted_factor
        
        return emissions
    
    def compare_emissions(self, 
                        route: Dict, 
                        vehicle_options: List[Vehicle]) -> pd.DataFrame:
        """Compare emissions for different vehicle options on a route.
        
        Args:
            route: Route information with distance
            vehicle_options: List of vehicle options to compare
            
        Returns:
            DataFrame with emissions comparison
        """
        distance = route.get("distance", 0)
        
        comparisons = []
        for vehicle in vehicle_options:
            emissions = self.calculate_route_emissions(vehicle, distance)
            
            comparisons.append({
                "vehicle_id": vehicle.id,
                "vehicle_type": vehicle.type,
                "fuel_type": vehicle.fuel_type,
                "emissions": emissions,
                "emissions_per_km": emissions / distance if distance > 0 else 0
            })
        
        return pd.DataFrame(comparisons)
    
    def calculate_fleet_emissions(self, 
                               fleet: List[Vehicle],
                               routes: List[Route]) -> Dict:
        """Calculate total emissions for a fleet of vehicles.
        
        Args:
            fleet: List of vehicles in the fleet
            routes: List of routes assigned to vehicles
            
        Returns:
            Dictionary with emissions statistics
        """
        vehicle_map = {vehicle.id: vehicle for vehicle in fleet}
        
        emissions = []
        for route in routes:
            if route.vehicle_id in vehicle_map:
                vehicle = vehicle_map[route.vehicle_id]
                route_emissions = self.calculate_route_emissions(vehicle, route.total_distance)
                
                emissions.append({
                    "route_id": route.id,
                    "vehicle_id": vehicle.id,
                    "distance": route.total_distance,
                    "emissions": route_emissions
                })
        
        emissions_df = pd.DataFrame(emissions) if emissions else pd.DataFrame()
        
        return {
            "total_emissions": emissions_df["emissions"].sum() if not emissions_df.empty else 0,
            "total_distance": emissions_df["distance"].sum() if not emissions_df.empty else 0,
            "average_emissions_per_km": (emissions_df["emissions"].sum() / emissions_df["distance"].sum() 
                                      if not emissions_df.empty and emissions_df["distance"].sum() > 0 else 0),
            "emissions_by_vehicle": emissions_df.groupby("vehicle_id")["emissions"].sum().to_dict() 
                                  if not emissions_df.empty else {}
        } 