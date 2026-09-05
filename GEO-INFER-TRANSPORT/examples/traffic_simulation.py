#!/usr/bin/env python3
"""
GEO-INFER-TRANSPORT Example: Traffic Simulation and Forecasting

Demonstrates traffic simulation (BPR delay), congestion modeling,
incident detection, and EWMA forecasting using the real TrafficAnalyzer
API. Runs entirely offline on synthetic data.
"""

from geo_infer_transport import TrafficAnalyzer, TransportNetwork


def main() -> None:
    """Run the traffic simulation example."""
    print("=" * 60)
    print("GEO-INFER-TRANSPORT: Traffic Simulation Example")
    print("=" * 60)

    network = TransportNetwork(network_type="road", modes=["car"])
    network.build_from_edges(
        [
            {"id": "e1", "from": "A", "to": "B", "length_m": 500, "speed_limit": 50},
            {"id": "e2", "from": "B", "to": "C", "length_m": 700, "speed_limit": 40},
            {"id": "e3", "from": "A", "to": "C", "length_m": 1100, "speed_limit": 60},
        ]
    )

    analyzer = TrafficAnalyzer(model_type="bpr", time_resolution="15min")

    # 1. Simulate one hour of traffic released from an OD demand matrix
    demand = {"matrix": [[0, 900], [600, 0]]}
    simulation = analyzer.simulate_traffic(
        network=network,
        demand_matrix=demand,
        simulation_hours=1,
        time_step_seconds=60,
    )
    print("\n--- Simulation (1h @ 60s steps) ---")
    print(f"Total trips: {simulation['statistics']['total_trips']}")
    print(f"Completed trips: {simulation['statistics']['completed_trips']}")
    final_step = simulation["results"][-1]
    print(
        f"Final state: {final_step['vehicles_in_network']} vehicles in network, "
        f"congestion={final_step['congestion_level']}"
    )

    # 2. Congestion modeling with the BPR function
    congestion = analyzer.model_congestion(
        network_flows={"e1": 1500, "e2": 2200, "e3": 800},
        capacity_data={"e1": 2000, "e2": 2000, "e3": 2000},
        algorithm="bpr",
    )
    print("\n--- BPR Congestion ---")
    for seg in congestion["segments"]:
        print(
            f"  {seg['segment_id']}: v/c={seg['vc_ratio']:.2f}, "
            f"delay={seg['delay_factor']:.2f}, condition={seg['condition']}"
        )

    # 3. Incident detection against a historical baseline
    incidents = analyzer.detect_incidents(
        current_data={"e1": {"speed": 22}, "e2": {"speed": 38}},
        historical_baseline={"e1": {"speed": 48}, "e2": {"speed": 40}},
    )
    print("\n--- Incidents ---")
    for inc in incidents:
        print(f"  {inc['segment_id']}: {inc['severity']} (deviation {inc['deviation']:.0%})")

    # 4. EWMA forecast with confidence intervals
    forecast = analyzer.forecast_traffic(
        historical_data=[
            {"volume": 800}, {"volume": 850}, {"volume": 900},
            {"volume": 950}, {"volume": 1000}, {"volume": 1080},
        ],
        forecast_horizon="1h",
    )
    print("\n--- Forecast (EWMA, 1h horizon) ---")
    for point in forecast["forecasts"][:4]:
        print(
            f"  +{point['time_offset_minutes']:>3}min: "
            f"{point['predicted_volume']} veh "
            f"[{point['confidence_lower']}, {point['confidence_upper']}]"
        )

    print("\nExample complete.")


if __name__ == "__main__":
    main()

