"""End-to-end integration tests for GEO-INFER-COMMS.

Exercise the full system surface (GeospatialCommunicationSystem) the way a
consumer would: start the system, subscribe, send messages, create
notifications, and drive an alert through its rule — then stop cleanly.
"""
import time

from geo_infer_comms import GeospatialCommunicationSystem
from geo_infer_comms.core.notifications import AlertRule
from geo_infer_comms.models.message import MessageStatus, NotificationStatus


def _wait_until(predicate, timeout: float = 5.0) -> bool:
    """Poll a condition until it holds or the deadline passes."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(0.05)
    return predicate()


class TestCommsEndToEnd:
    def test_message_delivery_through_running_system(self) -> None:
        system = GeospatialCommunicationSystem(config={"enable_persistence": False})
        received: list = []

        system.start()
        try:
            system.message_broker.subscribe("e2e_user", received.append)
            message = system.send_message(
                content="hello end-to-end", recipients=["e2e_user"]
            )

            assert _wait_until(lambda: len(received) >= 1), (
                "message was never delivered to the subscriber callback"
            )
            assert received[0].message_id == message.message_id
            assert received[0].content == "hello end-to-end"
            assert received[0].status == MessageStatus.DELIVERED
        finally:
            system.stop()

    def test_notification_and_alert_flow(self) -> None:
        system = GeospatialCommunicationSystem(config={"enable_persistence": False})
        system.start()
        try:
            notification = system.create_notification(
                title="Maintenance",
                content="Scheduled maintenance tonight",
                recipients=["ops@geo-infer.org"],
                notification_type="info",
                priority="normal",
                delivery_method=["in_app"],
            )
            assert _wait_until(
                lambda: notification.status == NotificationStatus.SENT
            ), "notification was not delivered by the background delivery thread"

            rule = AlertRule(
                name="overheat",
                description="temperature above threshold",
                conditions={"temperature": {"min": 35.0}},
                alert_title="High Temperature",
                alert_content="Temperature exceeded safe threshold",
                recipients=["ops@geo-infer.org"],
                delivery_methods=["in_app"],
                cooldown_period=3600,
            )
            rule_id = system.alert_system.create_alert_rule(rule)
            alert = system.alert_system.trigger_alert(
                rule_id, {"temperature": 38.5}
            )

            assert alert is not None
            assert alert.rule_id == rule_id
            assert rule.last_triggered is not None
            # Second trigger inside the cooldown window must be suppressed
            assert system.alert_system.trigger_alert(
                rule_id, {"temperature": 40.0}
            ) is None
            assert system.alert_system.get_alert_history(rule_id=rule_id)
        finally:
            system.stop()

    def test_full_pipeline_metrics_update(self) -> None:
        system = GeospatialCommunicationSystem(config={"enable_persistence": False})
        system.start()
        try:
            system.send_message(content="metric probe", recipients=["metrics_user"])
            system.publish_event(
                event_type="system_alert",
                payload={"alert_level": "info", "message": "probe"},
                source="integration_test",
            )

            metrics = system.get_comprehensive_metrics()
            assert metrics["message_metrics"]["metrics"]["messages_sent"] >= 1
            assert metrics["event_metrics"]["metrics"]["events_published"] >= 1
            assert metrics["system_health"]["status"] == "healthy"
        finally:
            system.stop()