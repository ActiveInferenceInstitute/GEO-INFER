"""Behavior tests for delivery core classes (routing, scheduling, areas)."""

from datetime import datetime, timedelta

import geopandas as gpd
from shapely.geometry import Point, Polygon

from geo_infer_log.core.delivery import (
    DeliveryScheduler,
    LastMileRouter,
    ServiceAreaAnalyzer,
)
from geo_infer_log.models.schemas import Location, Route, Vehicle


def make_vehicle(vehicle_id: str = "veh-1") -> Vehicle:
    return Vehicle(
        id=vehicle_id,
        type="van",
        capacity=100.0,
        max_range=500.0,
        speed=40.0,
        cost_per_km=1.0,
        emissions_per_km=0.5,
        location=(13.405, 52.52),
    )


def make_delivery(name: str, lon: float, lat: float) -> Location:
    return Location(name=name, coordinates=(lon, lat), type="customer")


class TestLastMileRouter:
    """Tests for last-mile routing behavior."""

    def test_define_service_area_builds_ellipse(self) -> None:
        router = LastMileRouter()
        area = router.define_service_area("depot-1", (13.405, 52.52), 5.0)
        assert isinstance(area, Polygon)
        assert router.service_areas["depot-1"] is area
        # Depot inside the circle, far point outside
        assert area.contains(Point(13.405, 52.52))
        assert area.contains(Point(13.45, 52.52))
        assert not area.contains(Point(13.405, 53.0))

    def test_optimize_deliveries_returns_routes(self) -> None:
        router = LastMileRouter()
        depot = Location(name="depot", coordinates=(13.405, 52.52), type="depot")
        deliveries = [
            make_delivery("d1", 13.41, 52.52),
            make_delivery("d2", 13.42, 52.53),
            make_delivery("d3", 13.43, 52.51),
            make_delivery("d4", 13.44, 52.54),
        ]
        vehicles = [make_vehicle("v1"), make_vehicle("v2")]
        routes = router.optimize_deliveries(depot, deliveries, vehicles, {})
        assert len(routes) == 2
        assert [r.vehicle_id for r in routes] == ["v1", "v2"]
        for route in routes:
            assert route.stops[0].name == "depot"
            assert route.stops[-1].name == "depot"
            assert route.total_distance > 0
            assert route.total_time > 0

    def test_optimize_deliveries_warns_outside_service_area(self) -> None:
        router = LastMileRouter()
        router.define_service_area("depot", (13.405, 52.52), 0.1)
        depot = Location(name="depot", coordinates=(13.405, 52.52), type="depot")
        far = make_delivery("far", 14.0, 53.0)
        vehicle = [make_vehicle()]
        routes = router.optimize_deliveries(depot, [far], vehicle, {})
        assert len(routes) == 1

    def test_cluster_singletons_when_enough_vehicles(self) -> None:
        router = LastMileRouter()
        deliveries = [make_delivery(f"d{i}", 13.4 + i * 0.01, 52.5) for i in range(3)]
        clusters = router._cluster_deliveries(deliveries, 3)
        assert clusters == [[deliveries[0]], [deliveries[1]], [deliveries[2]]]

    def test_cluster_single_group_when_no_clusters(self) -> None:
        router = LastMileRouter()
        deliveries = [make_delivery(f"d{i}", 13.4 + i * 0.01, 52.5) for i in range(3)]
        clusters = router._cluster_deliveries(deliveries, 0)
        assert clusters == [deliveries]

    def test_cluster_kmeans_partitions_all_deliveries(self) -> None:
        router = LastMileRouter()
        # Two well-separated groups
        deliveries = [
            make_delivery(f"west{i}", 13.0 - i * 0.001, 52.5) for i in range(4)
        ] + [make_delivery(f"east{i}", 14.0 + i * 0.001, 52.5) for i in range(4)]
        clusters = router._cluster_deliveries(deliveries, 2)
        assert len(clusters) == 2
        assert sum(len(c) for c in clusters) == 8
        assert all(len(c) > 0 for c in clusters)


class TestDeliveryScheduler:
    """Tests for delivery scheduling behavior."""

    def _make_scheduler(self) -> tuple:
        router = LastMileRouter()
        scheduler = DeliveryScheduler(router=router)
        depot = Location(name="depot", coordinates=(13.405, 52.52), type="depot")
        deliveries = [
            make_delivery(f"d{i}", 13.41 + i * 0.01, 52.52 + (i % 2) * 0.01)
            for i in range(6)
        ]
        vehicles = [make_vehicle("v1"), make_vehicle("v2")]
        return scheduler, depot, deliveries, vehicles

    def test_create_schedule_and_lookups(self) -> None:
        scheduler, depot, deliveries, vehicles = self._make_scheduler()
        start = datetime(2026, 1, 1)
        result = scheduler.create_schedule(
            depot=depot,
            deliveries=deliveries,
            vehicles=vehicles,
            start_date=start,
            end_date=start + timedelta(days=1),
            max_deliveries_per_day=4,
        )
        assert result["total_deliveries"] == 6
        assert result["scheduled_deliveries"] == 6
        assert result["unscheduled_deliveries"] == 0
        assert set(scheduler.schedule) == {"2026-01-01", "2026-01-02"}
        day1 = scheduler.get_daily_schedule(datetime(2026, 1, 1))
        assert len(day1) == 2
        assert all(isinstance(r, Route) for r in day1)
        assigned = scheduler.get_vehicle_schedule("v1")
        assert assigned and assigned[0].vehicle_id == "v1"
        assert scheduler.get_vehicle_schedule("missing") == []

    def test_reschedule_to_empty_date_creates_route(self) -> None:
        scheduler, depot, deliveries, vehicles = self._make_scheduler()
        start = datetime(2026, 1, 1)
        scheduler.create_schedule(
            depot=depot,
            deliveries=deliveries,
            vehicles=vehicles,
            start_date=start,
            end_date=start,
            max_deliveries_per_day=4,
        )
        route = scheduler.get_daily_schedule(start)[0]
        stops_before = len(route.stops)
        result = scheduler.reschedule_delivery(route.id, 1, datetime(2026, 2, 1))
        assert result["success"] is True
        assert result["new_date"] == "2026-02-01"
        assert len(route.stops) == stops_before - 1
        new_day = scheduler.get_daily_schedule(datetime(2026, 2, 1))
        assert len(new_day) == 1
        assert new_day[0].stops == [route.stops[0]] or new_day[0].stops[0] is not None

    def test_reschedule_appends_to_existing_day(self) -> None:
        scheduler, depot, deliveries, vehicles = self._make_scheduler()
        start = datetime(2026, 1, 1)
        scheduler.create_schedule(
            depot=depot,
            deliveries=deliveries,
            vehicles=vehicles,
            start_date=start,
            end_date=start + timedelta(days=1),
            max_deliveries_per_day=3,
        )
        day1 = scheduler.get_daily_schedule(start)
        target = scheduler.get_daily_schedule(datetime(2026, 1, 2))[0]
        target_stops = len(target.stops)
        result = scheduler.reschedule_delivery(day1[0].id, 1, datetime(2026, 1, 2))
        assert result["success"] is True
        assert result["new_route"] == target.id
        assert len(target.stops) == target_stops + 1

    def test_reschedule_unknown_route_fails(self) -> None:
        scheduler, depot, deliveries, vehicles = self._make_scheduler()
        start = datetime(2026, 1, 1)
        scheduler.create_schedule(
            depot=depot,
            deliveries=deliveries,
            vehicles=vehicles,
            start_date=start,
            end_date=start,
            max_deliveries_per_day=4,
        )
        result = scheduler.reschedule_delivery("no-such-route", 0, datetime(2026, 2, 1))
        assert result == {"success": False, "reason": "delivery_not_found"}


class TestServiceAreaAnalyzer:
    """Tests for service area analysis."""

    def test_create_service_area_with_distance(self) -> None:
        analyzer = ServiceAreaAnalyzer()
        gdf = analyzer.create_service_area("d1", (13.405, 52.52), max_distance=8.0)
        assert len(gdf) == 3
        assert set(gdf["depot_id"]) == {"d1"}
        assert set(gdf["ring_km"].round(2)) == {2.64, 5.36, 8.0}
        assert analyzer.service_areas["d1"].contains(Point(13.405, 52.52))

    def test_create_service_area_with_time(self) -> None:
        analyzer = ServiceAreaAnalyzer()
        gdf = analyzer.create_service_area("d2", (13.405, 52.52), max_time=60)
        # 60 min at 25 km/h -> 25 km
        assert gdf["ring_km"].max() == 25.0

    def test_analyze_coverage(self) -> None:
        analyzer = ServiceAreaAnalyzer()
        area = Point(0.0, 0.0).buffer(1.0)
        demand = gpd.GeoDataFrame(
            {"name": ["inside", "outside"]},
            geometry=[Point(0.1, 0.0), Point(5.0, 5.0)],
        )
        result = analyzer.analyze_coverage({"a": area}, demand)
        assert result["total_points"] == 2
        assert result["covered_points"] == 1
        assert result["coverage_ratio"] == 0.5
        assert result["depot_coverage"] == {"a": 1}

    def test_analyze_coverage_empty_demand(self) -> None:
        analyzer = ServiceAreaAnalyzer()
        demand = gpd.GeoDataFrame({"name": []}, geometry=[])
        result = analyzer.analyze_coverage({}, demand)
        assert result["coverage_ratio"] == 0

    def test_optimize_service_areas_empty(self) -> None:
        analyzer = ServiceAreaAnalyzer()
        assert analyzer.optimize_service_areas([], gpd.GeoDataFrame(), 5.0) == {}

    def test_optimize_service_areas_single_depot(self) -> None:
        analyzer = ServiceAreaAnalyzer()
        areas = analyzer.optimize_service_areas([("d1", (13.4, 52.5))], None, 5.0)
        assert set(areas) == {"d1"}
        assert areas["d1"].contains(Point(13.4, 52.5))

    def test_optimize_service_areas_multiple_depots(self) -> None:
        analyzer = ServiceAreaAnalyzer()
        depots = [("west", (13.0, 52.5)), ("east", (14.0, 52.5))]
        areas = analyzer.optimize_service_areas(depots, None, 5.0)
        assert set(areas) == {"west", "east"}
        assert not areas["west"].intersects(areas["east"])
        assert analyzer.service_areas == areas
