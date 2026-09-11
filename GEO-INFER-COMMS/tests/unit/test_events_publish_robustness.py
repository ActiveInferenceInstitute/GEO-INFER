"""Regression tests for event publishing robustness (GS-228).

Covers:
- Flat-key geospatial contexts ({"latitude", "longitude"}) are spatially
  indexed, the same way nested {"location": {...}} contexts are.
- A filtered subscription receives flat-key published events.
- Malformed geospatial contexts raise ValueError before any state mutation,
  leaving events, metrics, and the spatial index consistent.
"""

import pytest

from geo_infer_comms.core.events import EventManager
from geo_infer_comms.models.message import (
    EventPublishRequest,
    EventSubscriptionRequest,
)


@pytest.fixture()
def event_manager():
    manager = EventManager(enable_persistence=False)
    manager.start()
    try:
        yield manager
    finally:
        manager.stop()


def _publish(em: EventManager, geospatial_context):
    request = EventPublishRequest(
        event_type="data_update",
        payload={"temperature": 21.5},
        source="unit-test",
        geospatial_context=geospatial_context,
    )
    return em.publish_event(request)


def _index_ids(em: EventManager):
    return {event_id for ids in em.spatial_index._index.values() for event_id in ids}


def test_flat_key_context_is_spatially_indexed(event_manager):
    event = _publish(event_manager, {"latitude": 52.0, "longitude": 13.4})

    assert event.event_id in _index_ids(event_manager)
    assert event.event_id in event_manager.events


def test_nested_location_context_is_spatially_indexed(event_manager):
    event = _publish(
        event_manager,
        {"location": {"latitude": 48.85, "longitude": 2.35}},
    )

    assert event.event_id in _index_ids(event_manager)


def test_flat_key_publish_reaches_filtered_subscription(event_manager):
    received = []
    event_manager.subscribe_to_events(
        "unit-subscriber",
        EventSubscriptionRequest(event_types=["data_update"]),
        received.append,
    )

    event = _publish(event_manager, {"latitude": 41.9, "longitude": 12.5})

    # Bounded wait: delivery happens on the manager's processing thread.
    for _ in range(200):
        if received:
            break
        import time

        time.sleep(0.01)

    assert received, "flat-key event was never delivered to subscriber"
    assert received[0].event_id == event.event_id

    # The filter path accepts the same flat shape for geospatial filters.
    from geo_infer_comms.core.events import EventFilter

    event_filter = EventFilter(event_manager)
    assert event_filter._apply_geospatial_filter(
        received[0],
        {
            "bbox": {
                "min_lon": 12.0,
                "max_lon": 13.0,
                "min_lat": 41.0,
                "max_lat": 42.0,
            }
        },
    )


@pytest.mark.parametrize(
    "context",
    [
        # Nested location missing latitude (pre-fix: uncaught KeyError).
        {"location": {"longitude": 13.4}},
        # Nested location missing longitude.
        {"location": {"latitude": 52.0}},
        # Flat context with only one coordinate.
        {"latitude": 52.0},
        # Non-numeric coordinates.
        {"latitude": "not-a-number", "longitude": 13.4},
    ],
)
def test_malformed_context_raises_before_state_mutation(event_manager, context):
    with pytest.raises(ValueError):
        _publish(event_manager, context)

    # Nothing was stored, queued, indexed, or counted.
    assert not event_manager.events
    assert not _index_ids(event_manager)
    assert event_manager.metrics.events_published == 0


def test_malformed_context_error_mentions_module(event_manager):
    with pytest.raises(ValueError, match="geo_infer_comms.events"):
        _publish(event_manager, {"location": {"longitude": 1.0}})


def test_valid_context_without_coordinates_still_publishes(event_manager):
    event = _publish(event_manager, {"region": "eu-central"})

    assert event.event_id in event_manager.events
    assert event.event_id not in _index_ids(event_manager)
    assert event_manager.metrics.events_published == 1
