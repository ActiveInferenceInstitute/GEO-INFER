"""Unit tests for nested messaging routing and protocols.

Exercises ``geo_infer_space.nested.messaging.routing`` (MessageRouter,
RoutingStrategy, RouteMetric, Route) and ``...messaging.protocols``
(MessageProtocol hierarchy) against actual source behavior, including
verified quirks:

- HIERARCHICAL/GEOGRAPHIC delegate to the shortest-path finder and
  LOAD_BALANCED delegates to the least-congested finder, so the returned
  ``Route.strategy`` carries the delegated tag, not the requested one.
- The route cache keys on ``(source, destination, strategy)`` only:
  node/edge load updates and ``metric`` changes never invalidate it, while
  topology mutations and ``clear_cache()`` do.
"""

import pytest

from geo_infer_space.nested.messaging.message_broker import Message, MessageType
from geo_infer_space.nested.messaging.protocols import (
    BatchProtocol,
    FireAndForgetProtocol,
    MessageProtocol,
    ProtocolConfig,
    ProtocolType,
    PublishSubscribeProtocol,
    RequestResponseProtocol,
    StreamingProtocol,
)
from geo_infer_space.nested.messaging.routing import (
    MessageRouter,
    Route,
    RouteMetric,
    RouteSegment,
    RoutingStrategy,
)


def make_router(name: str = "router") -> MessageRouter:
    """Fresh router with three nodes on a line A-B-C (distance 1.0 each)."""
    router = MessageRouter(name=name)
    for node in ("A", "B", "C"):
        router.add_node(node)
    router.add_edge("A", "B", distance=1.0, latency=0.1, cost=1.0)
    router.add_edge("B", "C", distance=1.0, latency=0.1, cost=1.0)
    return router


def add_triangle(router: MessageRouter, boundary_ab: bool = False) -> MessageRouter:
    """Add a direct A-C edge (distance 2.5) so two A-C paths compete.

    With ``boundary_ab`` the A-B edge crosses boundary ``sector-7``: under
    BOUNDARY_AWARE the 2-hop path costs 2*1.0 + 1.0 = 3.0 while the direct
    edge stays 2.5, so the strategy must flip to [A, C].
    """
    router.add_edge(
        "A",
        "B",
        distance=1.0,
        latency=0.1,
        cost=1.0,
        crosses_boundary=boundary_ab,
        boundary_id="sector-7" if boundary_ab else None,
    )
    router.add_edge("A", "C", distance=2.5, latency=1.0, cost=2.0)
    return router


def make_metric_router(name: str = "metrics") -> MessageRouter:
    """Diamond S-{X,Y}-T where DISTANCE, COST and LATENCY disagree.

    Path totals (distance, cost, latency, reliability-product, min-bw):
    direct S-T: 5.0, 1.0, 10.0, 1.0, 100.0
    via X:      4.0, 12.0, 4.0, 0.64, 50.0
    via Y:      8.0, 4.0, 2.0, 0.25, 10.0
    """
    router = MessageRouter(name=name)
    for node in ("S", "X", "Y", "T"):
        router.add_node(node)
    router.add_edge(
        "S",
        "T",
        distance=5.0,
        latency=10.0,
        cost=1.0,
        reliability=1.0,
        bandwidth=100.0,
    )
    router.add_edge(
        "S",
        "X",
        distance=2.0,
        latency=2.0,
        cost=6.0,
        reliability=0.8,
        bandwidth=50.0,
    )
    router.add_edge(
        "X",
        "T",
        distance=2.0,
        latency=2.0,
        cost=6.0,
        reliability=0.8,
        bandwidth=50.0,
    )
    router.add_edge(
        "S",
        "Y",
        distance=4.0,
        latency=1.0,
        cost=2.0,
        reliability=0.5,
        bandwidth=10.0,
    )
    router.add_edge(
        "Y",
        "T",
        distance=4.0,
        latency=1.0,
        cost=2.0,
        reliability=0.5,
        bandwidth=10.0,
    )
    return router


class _FakeBroker:
    """In-memory broker double recording protocol send/response calls."""

    def __init__(self) -> None:
        self.sent: list = []
        self.responses: list = []
        self._next_id = 0

    def send_message(self, sender_id, recipient_id, payload, **kwargs):
        self._next_id += 1
        message_id = f"msg-{self._next_id}"
        self.sent.append(
            {
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "payload": payload,
                **kwargs,
            }
        )
        return message_id

    def send_response(self, original_message, payload, status="success"):
        self.responses.append({"original": original_message, "payload": payload})
        return f"resp-{len(self.responses)}"


class TestPathfinding:
    """Basic path correctness: paths, unreachable, unknown, self-route."""

    def test_finds_two_hop_path_on_line_graph(self) -> None:
        router = make_router()
        route = router.find_route("A", "C")
        assert route is not None
        assert route.get_path() == ["A", "B", "C"]
        assert route.hop_count == 2
        assert route.total_distance == pytest.approx(2.0)
        assert route.strategy is RoutingStrategy.SHORTEST_PATH

    def test_unreachable_node_returns_none(self) -> None:
        router = make_router()
        router.add_node("ISLAND")  # no edges
        assert router.find_route("A", "ISLAND") is None

    def test_unknown_node_returns_none(self) -> None:
        router = make_router()
        assert router.find_route("A", "GHOST") is None
        assert router.find_route("GHOST", "A") is None

    def test_self_route_has_zero_segments(self) -> None:
        router = make_router()
        route = router.find_route("A", "A")
        assert route is not None
        assert route.segments == []
        assert route.hop_count == 0
        assert route.get_path() == []
        assert route.total_distance == 0.0
        assert not route.crosses_boundaries()

    def test_one_way_edge_is_respected(self) -> None:
        router = make_router()
        router.add_node("D")
        router.add_edge("D", "A", distance=1.0, bidirectional=False)
        # D -> A exists, A -> D does not.
        assert router.find_route("A", "D") is None
        back = router.find_route("D", "A")
        assert back is not None
        assert back.get_path() == ["D", "A"]


class TestStrategySelection:
    """Per-strategy routing, delegation tags, congestion and boundaries."""

    def test_every_strategy_returns_a_route(self) -> None:
        router = add_triangle(make_router())
        for strategy in RoutingStrategy:
            route = router.find_route("A", "C", strategy=strategy, use_cache=False)
            assert route is not None, f"{strategy} returned no route"
            assert route.source == "A"
            assert route.destination == "C"
            assert route.get_path()[0] == "A"
            assert route.get_path()[-1] == "C"

    def test_delegated_strategies_carry_delegated_tag(self) -> None:
        """Source delegates finders, so Route.strategy is the delegated tag.

        _find_hierarchical_path and _find_geographic_path call
        _find_shortest_path; _find_load_balanced_path calls
        _find_least_congested_path. Only SHORTEST_PATH, LEAST_CONGESTED and
        BOUNDARY_AWARE stamp their own tag on the returned Route.
        """
        router = add_triangle(make_router())
        delegation = {
            RoutingStrategy.SHORTEST_PATH: RoutingStrategy.SHORTEST_PATH,
            RoutingStrategy.HIERARCHICAL: RoutingStrategy.SHORTEST_PATH,
            RoutingStrategy.GEOGRAPHIC: RoutingStrategy.SHORTEST_PATH,
            RoutingStrategy.LEAST_CONGESTED: RoutingStrategy.LEAST_CONGESTED,
            RoutingStrategy.LOAD_BALANCED: RoutingStrategy.LEAST_CONGESTED,
            RoutingStrategy.BOUNDARY_AWARE: RoutingStrategy.BOUNDARY_AWARE,
        }
        for requested, expected_tag in delegation.items():
            route = router.find_route("A", "C", strategy=requested, use_cache=False)
            assert route is not None
            assert route.strategy is expected_tag, requested

    def test_delegated_strategy_failure_returns_none(self) -> None:
        router = add_triangle(make_router())
        assert (
            router.find_route("A", "GHOST", strategy=RoutingStrategy.HIERARCHICAL)
            is None
        )
        assert (
            router.find_route("A", "GHOST", strategy=RoutingStrategy.LOAD_BALANCED)
            is None
        )

    def test_least_congested_reroutes_after_load(self) -> None:
        """Load updates do not invalidate the cache; clear_cache() must."""
        router = add_triangle(make_router())
        before = router.find_route("A", "C", strategy=RoutingStrategy.LEAST_CONGESTED)
        assert before is not None
        assert before.get_path() == ["A", "B", "C"]

        router.update_node_load("B", 10.0)
        stale = router.find_route("A", "C", strategy=RoutingStrategy.LEAST_CONGESTED)
        # Cache quirk: same cached object is returned despite the load change.
        assert stale is before
        assert stale.get_path() == ["A", "B", "C"]

        router.clear_cache()
        after = router.find_route("A", "C", strategy=RoutingStrategy.LEAST_CONGESTED)
        assert after is not None
        # distance*(1+load) on the 2-hop path: 1 + 11 = 12 > 2.5 direct.
        assert after.get_path() == ["A", "C"]

    def test_boundary_aware_avoids_boundary_edge(self) -> None:
        """2.5 direct beats 3.0 doubled 2-hop for BOUNDARY_AWARE only.

        Under plain DISTANCE the 2-hop path (2.0) still beats the direct
        edge (2.5), so the two strategies must pick different paths.
        """
        router = add_triangle(make_router(), boundary_ab=True)
        plain = router.find_route("A", "C")
        assert plain is not None
        assert plain.get_path() == ["A", "B", "C"]
        assert plain.crosses_boundaries()
        assert plain.get_boundary_crossings() == ["sector-7"]

        boundary_route = router.find_route(
            "A", "C", strategy=RoutingStrategy.BOUNDARY_AWARE
        )
        assert boundary_route is not None
        assert boundary_route.get_path() == ["A", "C"]
        assert boundary_route.total_distance == pytest.approx(2.5)
        assert not boundary_route.crosses_boundaries()
        assert boundary_route.get_boundary_crossings() == []


class TestMetricOrdering:
    """Metric-dependent winners plus Route aggregate arithmetic."""

    def test_distance_and_cost_and_latency_pick_different_paths(self) -> None:
        by_metric = {}
        for metric in (RouteMetric.DISTANCE, RouteMetric.COST, RouteMetric.LATENCY):
            router = make_metric_router()
            route = router.find_route("S", "T", metric=metric)
            assert route is not None
            by_metric[metric] = route.get_path()

        # distance: 4.0 via X < 5.0 direct < 8.0 via Y
        assert by_metric[RouteMetric.DISTANCE] == ["S", "X", "T"]
        # cost: 1.0 direct < 4.0 via Y < 12.0 via X
        assert by_metric[RouteMetric.COST] == ["S", "T"]
        # latency: 2.0 via Y < 4.0 via X < 10.0 direct
        assert by_metric[RouteMetric.LATENCY] == ["S", "Y", "T"]

    def test_hop_count_minimizes_segments(self) -> None:
        router = make_metric_router()
        route = router.find_route("S", "T", metric=RouteMetric.HOP_COUNT)
        assert route is not None
        assert route.get_path() == ["S", "T"]
        assert route.hop_count == 1

    def test_reliability_metric_prefers_highest_reliability(self) -> None:
        """Weights are (1 - reliability), so 1.0 edges cost 0.

        Direct (1.0, 1.0) totals 0.0 vs 0.4 via X and 1.0 via Y.
        """
        router = make_metric_router()
        route = router.find_route("S", "T", metric=RouteMetric.RELIABILITY)
        assert route is not None
        assert route.get_path() == ["S", "T"]
        # Same graph under DISTANCE picks the X path instead.
        distance_route = make_metric_router().find_route("S", "T")
        assert distance_route is not None
        assert distance_route.get_path() == ["S", "X", "T"]

    def test_bandwidth_metric_falls_back_to_distance(self) -> None:
        router = make_metric_router()
        route = router.find_route("S", "T", metric=RouteMetric.BANDWIDTH)
        assert route is not None
        assert route.get_path() == ["S", "X", "T"]

    def test_route_aggregates_sum_min_product_and_len(self) -> None:
        """Route.__post_init__ aggregates its segments: sums, min, product."""
        route = Route(
            route_id="fixture",
            source="S",
            destination="T",
            segments=[
                RouteSegment(
                    from_node="S",
                    to_node="X",
                    distance=3.0,
                    latency=1.5,
                    bandwidth=10.0,
                    reliability=0.5,
                    cost=2.0,
                ),
                RouteSegment(
                    from_node="X",
                    to_node="T",
                    distance=4.0,
                    latency=0.5,
                    bandwidth=100.0,
                    reliability=0.9,
                    cost=3.0,
                ),
            ],
        )
        assert route.total_distance == pytest.approx(7.0)
        assert route.total_latency == pytest.approx(2.0)
        assert route.total_cost == pytest.approx(5.0)
        assert route.min_bandwidth == pytest.approx(10.0)
        assert route.reliability == pytest.approx(0.45)
        assert route.hop_count == 2
        assert route.get_path() == ["S", "X", "T"]

    def test_empty_route_keeps_defaults(self) -> None:
        route = Route(route_id="empty", source="A", destination="A")
        assert route.hop_count == 0
        assert route.min_bandwidth == float("inf")
        assert route.reliability == 1.0
        assert route.total_distance == 0.0


class TestCacheAndStats:
    """Cache hits/misses, invalidation quirks and routing statistics."""

    def test_second_lookup_hits_cached_route(self) -> None:
        router = make_router()
        first = router.find_route("A", "C")
        assert router.cache_hits == 0
        assert router.cache_misses == 1

        second = router.find_route("A", "C")
        assert second is first
        assert router.cache_hits == 1
        assert router.cache_misses == 1
        assert first.use_count == 1
        assert first.last_used is not None

    def test_use_cache_false_bypasses_cache(self) -> None:
        router = make_router()
        cached = router.find_route("A", "C")
        assert cached is not None

        fresh = router.find_route("A", "C", use_cache=False)
        assert fresh is not cached
        assert cached.use_count == 0
        assert router.cache_misses == 2
        assert router.cache_hits == 0
        assert len(router.route_cache) == 1

    def test_add_edge_clears_cache_but_not_counters(self) -> None:
        """Topology mutations drop entries while counters keep counting."""
        router = make_router()
        router.find_route("A", "C")
        router.find_route("A", "C")
        assert router.cache_hits == 1

        router.add_edge("A", "C", distance=2.5)
        assert len(router.route_cache) == 0
        router.find_route("A", "C")
        # Still one hit total: the post-mutation lookup was a fresh miss.
        assert router.cache_hits == 1
        assert router.cache_misses == 2

    def test_clear_cache_resets_counters(self) -> None:
        router = make_router()
        router.find_route("A", "C")
        router.find_route("A", "C")

        router.clear_cache()
        assert router.cache_hits == 0
        assert router.cache_misses == 0
        assert len(router.route_cache) == 0
        router.find_route("A", "C")
        assert router.cache_misses == 1

    def test_metric_is_not_part_of_the_cache_key(self) -> None:
        """Cache quirk: (source, destination, strategy) key ignores metric.

        The second (COST) lookup is served from the DISTANCE route.
        """
        router = make_metric_router()
        distance_route = router.find_route("S", "T", metric=RouteMetric.DISTANCE)
        cost_lookup = router.find_route("S", "T", metric=RouteMetric.COST)
        assert cost_lookup is distance_route
        assert distance_route is not None
        assert distance_route.total_cost == pytest.approx(12.0)  # not 1.0

    def test_routing_statistics_shape_and_values(self) -> None:
        router = make_router(name="stat-router")
        router.find_route("A", "B")
        router.find_route("A", "B")  # cache hit: stats are not updated
        router.find_route("A", "GHOST")  # failed lookup

        stats = router.get_routing_statistics()
        assert stats["router_name"] == "stat-router"
        assert stats["total_nodes"] == 3
        assert stats["total_edges"] == 4  # two bidirectional edges, both dirs
        assert stats["cached_routes"] == 1
        assert stats["cache_hit_ratio"] == pytest.approx(1 / 3)
        assert stats["routing_stats"] == {
            "shortest_path_requests": 2,
            "shortest_path_success": 1,
            "shortest_path_failed": 1,
        }
        assert stats["average_node_load"] == 0.0
        assert isinstance(stats["updated_at"], str)

        router.update_node_load("A", 4.0)
        assert router.get_routing_statistics()["average_node_load"] == pytest.approx(
            4.0
        )


class TestProtocols:
    """Protocol ABC contract, construction and message round-trips."""

    def test_abc_is_not_instantiable(self) -> None:
        config = ProtocolConfig(protocol_type=ProtocolType.REQUEST_RESPONSE)
        with pytest.raises(TypeError):
            MessageProtocol("abstract", config)  # type: ignore[abstract]

    def test_sending_without_broker_raises_runtime_error(self) -> None:
        for cls in (RequestResponseProtocol, FireAndForgetProtocol):
            protocol = cls(f"no-broker-{cls.__name__}")
            with pytest.raises(RuntimeError):
                protocol.send_message("a", "b", {"hello": True})

    def test_every_concrete_protocol_constructible_with_config(self) -> None:
        concrete = (
            (RequestResponseProtocol, ProtocolType.REQUEST_RESPONSE),
            (PublishSubscribeProtocol, ProtocolType.PUBLISH_SUBSCRIBE),
            (FireAndForgetProtocol, ProtocolType.FIRE_AND_FORGET),
            (StreamingProtocol, ProtocolType.STREAMING),
            (BatchProtocol, ProtocolType.BATCH),
        )
        for cls, protocol_type in concrete:
            protocol = cls(
                f"proto-{protocol_type.value}",
                ProtocolConfig(protocol_type=protocol_type),
            )
            assert protocol.config.protocol_type is protocol_type
            stats = protocol.get_statistics()
            assert stats["protocol_id"] == f"proto-{protocol_type.value}"
            assert stats["protocol_type"] == protocol_type.value
            assert stats["active_sessions"] == 0
            assert stats["statistics"]["messages_sent"] == 0

    def test_session_lifecycle_on_shared_abc_code(self) -> None:
        protocol = RequestResponseProtocol("sessions")
        assert protocol.create_session("s1", ["a", "b"]) is True
        assert protocol.create_session("s1", ["a"]) is False  # duplicate
        assert protocol.close_session("s1") is True
        assert protocol.close_session("s1") is False  # already gone
        assert protocol.get_statistics()["active_sessions"] == 0

    def test_request_response_round_trip(self) -> None:
        """Request is tracked; the correlated response clears it."""
        broker = _FakeBroker()
        protocol = RequestResponseProtocol("rr")
        protocol.message_broker = broker

        message_id = protocol.send_message("client", "service", {"q": 1})
        assert message_id == "msg-1"
        assert message_id in protocol.pending_requests
        assert broker.sent[0]["requires_response"] is True
        assert protocol.statistics["messages_sent"] == 1

        request = Message(
            message_id=message_id,
            sender_id="client",
            recipient_id="service",
            message_type=MessageType.QUERY,
            payload={"q": 1},
            requires_response=True,
            correlation_id=message_id,
        )
        acked = protocol.handle_message(request)
        assert acked == {"q": 1}
        # Request branch replies through the broker with the default payload.
        assert broker.responses[0]["payload"] == {"status": "received"}
        assert message_id in protocol.pending_requests

        response = Message(
            message_id="resp-1",
            sender_id="service",
            recipient_id="client",
            message_type=MessageType.RESPONSE,
            payload={"answer": 42},
            correlation_id=message_id,
        )
        answered = protocol.handle_message(response)
        assert answered == {"answer": 42}
        assert message_id not in protocol.pending_requests
        assert protocol.statistics["messages_received"] == 2

    def test_fire_and_forget_round_trip(self) -> None:
        broker = _FakeBroker()
        protocol = FireAndForgetProtocol("ff")
        protocol.message_broker = broker

        message_id = protocol.send_message("a", "b", "fire")
        assert message_id == "msg-1"
        assert broker.sent[0]["requires_response"] is False
        assert protocol.statistics["messages_sent"] == 1

        delivered = Message(
            message_id=message_id,
            sender_id="a",
            recipient_id="b",
            message_type=MessageType.DATA,
            payload="fire",
        )
        assert protocol.handle_message(delivered) == "fire"
        assert protocol.statistics["messages_received"] == 1

    def test_publish_subscribe_fans_out_to_subscribers(self) -> None:
        broker = _FakeBroker()
        protocol = PublishSubscribeProtocol("ps")
        protocol.message_broker = broker
        assert protocol.subscribe("sub-1", "alerts") is True
        assert protocol.subscribe("sub-2", "alerts") is True

        result = protocol.send_message("publisher", "unused", "hot", topic="alerts")
        assert result == "published_to_2_subscribers"
        assert {call["recipient_id"] for call in broker.sent} == {"sub-1", "sub-2"}
        assert protocol.statistics["messages_sent"] == 2

        assert protocol.unsubscribe("sub-1", "alerts") is True
        assert (
            protocol.send_message("publisher", "unused", "hot", topic="alerts")
            == "published_to_1_subscribers"
        )

    def test_protocol_type_members(self) -> None:
        assert {member.name: member.value for member in ProtocolType} == {
            "REQUEST_RESPONSE": "request_response",
            "PUBLISH_SUBSCRIBE": "publish_subscribe",
            "FIRE_AND_FORGET": "fire_and_forget",
            "STREAMING": "streaming",
            "BATCH": "batch",
            "GOSSIP": "gossip",
            "CONSENSUS": "consensus",
            "HEARTBEAT": "heartbeat",
        }
