"""
Core messaging system for GEO-INFER-COMMS.

This module implements the central messaging infrastructure, including
message routing, delivery, and storage with comprehensive geospatial
support and real-time capabilities.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Callable, Any, Set
import asyncio
import json
import logging
import threading
import time
from datetime import datetime, timezone
from dataclasses import dataclass, field
import queue
import uuid

from geo_infer_comms.models.message import (
    MessageRequest, MessageResponse, MessageStatus, MessagePriority,
    BroadcastRequest, BroadcastResponse, MessageMetadata
)
from geo_infer_comms.models.spatial import (
    GeospatialMetadata, SpatialFilter, GeospatialPoint, SpatialIndex
)
from geo_infer_comms.utils.validation import (
    validate_message_content, validate_message_recipients,
    validate_spatial_filter, sanitize_message_content
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from geo_infer_comms.core.messaging import MessageBroker


class MessageBroker:
    """
    Central message broker for routing and delivery.

    Handles message queuing, routing, and delivery with support for
    geospatial filtering and priority-based processing.
    """

    def __init__(
        self,
        max_queue_size: int = 10000,
        enable_persistence: bool = True,
        persistence_path: Optional[str] = None
    ):
        self.max_queue_size = max_queue_size
        self.enable_persistence = enable_persistence
        self.persistence_path = persistence_path

        # Message storage and routing
        self.message_store: Dict[str, MessageResponse] = {}
        self.message_queue: queue.PriorityQueue = queue.PriorityQueue(maxsize=max_queue_size)
        self.spatial_index = SpatialIndex()

        # Subscribers and routing
        self.subscribers: Dict[str, List[Callable]] = {}
        self.spatial_subscriptions: Dict[str, SpatialFilter] = {}

        # Threading and concurrency
        self._lock = threading.RLock()
        self._processing_thread: Optional[threading.Thread] = None
        self._running = False

        # Metrics and monitoring
        self.metrics = MessageMetrics()

        # Set up logging
        self.logger = logging.getLogger(__name__)

    def start(self) -> None:
        """Start the message broker processing."""
        with self._lock:
            if self._running:
                return

            self._running = True
            self._processing_thread = threading.Thread(
                target=self._process_messages,
                daemon=True
            )
            self._processing_thread.start()
            self.logger.info("Message broker started")

    def stop(self) -> None:
        """Stop the message broker processing."""
        with self._lock:
            self._running = False
            if self._processing_thread:
                self._processing_thread.join(timeout=5.0)
            self.logger.info("Message broker stopped")

    def send_message(self, request: MessageRequest, sender_id: str) -> MessageResponse:
        """
        Send a new message through the broker.

        Args:
            request: Message request details
            sender_id: ID of the sender

        Returns:
            Message response with delivery status

        Raises:
            ValueError: If message is invalid or broker is not running
        """
        if not self._running:
            raise RuntimeError("Message broker is not running")

        # Validate message
        if not validate_message_content(request.content):
            raise ValueError("Invalid message content")

        if not validate_message_recipients(request.recipients):
            raise ValueError("Invalid message recipients")

        # Create message response
        message = MessageResponse(
            content=request.content,
            sender_id=sender_id,
            recipients=request.recipients,
            channel_id=request.channel_id,
            message_type=request.message_type,
            priority=request.priority,
            geospatial_data=request.geospatial_data,
            metadata=MessageMetadata()
        )

        # Store message
        with self._lock:
            self.message_store[message.message_id] = message

            # Add to spatial index if geospatial data present
            if message.geospatial_data:
                self.spatial_index.insert(
                    message.geospatial_data.location,
                    message.message_id
                )

            # Queue for processing
            priority_value = self._get_priority_value(message.priority)
            self.message_queue.put((priority_value, message.message_id, message))

        self.metrics.messages_sent += 1
        self.logger.info(f"Message queued: {message.message_id}")
        return message

    def broadcast_message(self, request: BroadcastRequest, sender_id: str) -> BroadcastResponse:
        """
        Broadcast a message to multiple recipients based on criteria.

        Args:
            request: Broadcast request details
            sender_id: ID of the sender

        Returns:
            Broadcast response with delivery statistics
        """
        if not self._running:
            raise RuntimeError("Message broker is not running")

        broadcast = BroadcastResponse()
        broadcast.started_at = datetime.now(timezone.utc)

        try:
            # Find recipients based on target criteria
            recipients = self._resolve_broadcast_recipients(request, sender_id)

            # Send message to each recipient
            successful_deliveries = 0
            for recipient in recipients:
                try:
                    message_request = MessageRequest(
                        content=request.content,
                        recipients=[recipient],
                        message_type=request.message_type,
                        priority=request.priority,
                        geospatial_data=request.geospatial_filter
                    )
                    self.send_message(message_request, sender_id)
                    successful_deliveries += 1
                except Exception as e:
                    self.logger.error(f"Failed to deliver broadcast to {recipient}: {e}")

            broadcast.recipient_count = len(recipients)
            broadcast.delivery_stats = {
                "successful": successful_deliveries,
                "failed": len(recipients) - successful_deliveries
            }

            if successful_deliveries > 0:
                broadcast.status = "completed"
            else:
                broadcast.status = "failed"

        except Exception as e:
            broadcast.status = "failed"
            self.logger.error(f"Broadcast failed: {e}")

        broadcast.completed_at = datetime.now(timezone.utc)
        return broadcast

    def subscribe(
        self,
        subscriber_id: str,
        callback: Callable[[MessageResponse], None],
        spatial_filter: Optional[SpatialFilter] = None
    ) -> str:
        """
        Subscribe to messages with optional spatial filtering.

        Args:
            subscriber_id: Unique subscriber identifier
            callback: Function to call when messages are received
            spatial_filter: Optional spatial filter for message routing

        Returns:
            Subscription ID for unsubscribing
        """
        subscription_id = f"sub_{uuid.uuid4().hex[:8]}"

        with self._lock:
            if subscriber_id not in self.subscribers:
                self.subscribers[subscriber_id] = []

            self.subscribers[subscriber_id].append(callback)

            if spatial_filter:
                self.spatial_subscriptions[subscription_id] = spatial_filter

        self.logger.info(f"Subscriber {subscriber_id} subscribed: {subscription_id}")
        return subscription_id

    def unsubscribe(self, subscriber_id: str, subscription_id: Optional[str] = None) -> bool:
        """
        Unsubscribe from messages.

        Args:
            subscriber_id: Subscriber identifier
            subscription_id: Specific subscription to remove (removes all if None)

        Returns:
            True if successfully unsubscribed
        """
        with self._lock:
            if subscriber_id not in self.subscribers:
                return False

            if subscription_id:
                # Remove specific subscription
                if subscription_id in self.spatial_subscriptions:
                    del self.spatial_subscriptions[subscription_id]
                # Note: In a real implementation, would need to track which callback
                # corresponds to which subscription ID
            else:
                # Remove all subscriptions for this subscriber
                del self.subscribers[subscriber_id]
                # Remove any spatial subscriptions for this subscriber
                to_remove = [
                    sid for sid in self.spatial_subscriptions.keys()
                    if sid.startswith(f"sub_{subscriber_id}")
                ]
                for sid in to_remove:
                    del self.spatial_subscriptions[sid]

        self.logger.info(f"Subscriber {subscriber_id} unsubscribed")
        return True

    def get_message(self, message_id: str) -> Optional[MessageResponse]:
        """
        Retrieve a specific message by ID.

        Args:
            message_id: Message identifier

        Returns:
            Message if found, None otherwise
        """
        with self._lock:
            return self.message_store.get(message_id)

    def get_messages(
        self,
        sender_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[MessageResponse]:
        """
        Retrieve messages with filtering options.

        Args:
            sender_id: Filter by sender
            channel_id: Filter by channel
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum number of messages to return

        Returns:
            List of matching messages
        """
        with self._lock:
            messages = list(self.message_store.values())

        # Apply filters
        filtered_messages = messages

        if sender_id:
            filtered_messages = [m for m in filtered_messages if m.sender_id == sender_id]

        if channel_id:
            filtered_messages = [m for m in filtered_messages if m.channel_id == channel_id]

        if start_time:
            filtered_messages = [m for m in filtered_messages if m.timestamp >= start_time]

        if end_time:
            filtered_messages = [m for m in filtered_messages if m.timestamp <= end_time]

        # Sort by timestamp (newest first) and limit
        filtered_messages.sort(key=lambda m: m.timestamp, reverse=True)
        return filtered_messages[:limit]

    def get_metrics(self) -> Dict[str, Any]:
        """Get current broker metrics."""
        return {
            "messages_stored": len(self.message_store),
            "queue_size": self.message_queue.qsize(),
            "subscribers": len(self.subscribers),
            "spatial_subscriptions": len(self.spatial_subscriptions),
            "metrics": self.metrics.to_dict()
        }

    def _process_messages(self) -> None:
        """Background thread to process queued messages."""
        while self._running:
            try:
                # Get next message from queue (with timeout)
                try:
                    priority, message_id, message = self.message_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                # Process message delivery
                self._deliver_message(message)

                # Mark task as done
                self.message_queue.task_done()

            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                time.sleep(1.0)  # Brief pause before retrying

    def _deliver_message(self, message: MessageResponse) -> None:
        """Deliver message to appropriate subscribers."""
        try:
            # Update message status
            message.status = MessageStatus.DELIVERED
            message.metadata.updated_at = datetime.now(timezone.utc)

            # Find matching subscribers
            matching_subscribers = self._find_matching_subscribers(message)

            # Deliver to each subscriber
            for subscriber_id, callbacks in matching_subscribers.items():
                for callback in callbacks:
                    try:
                        # In a real implementation, would use threading or async
                        callback(message)
                    except Exception as e:
                        self.logger.error(f"Error delivering to subscriber {subscriber_id}: {e}")

            self.metrics.messages_delivered += 1

        except Exception as e:
            self.logger.error(f"Error delivering message {message.message_id}: {e}")
            message.status = MessageStatus.FAILED
            self.metrics.delivery_failures += 1

    def _find_matching_subscribers(self, message: MessageResponse) -> Dict[str, List[Callable]]:
        """Find subscribers that should receive this message."""
        matching = {}

        with self._lock:
            for subscriber_id, callbacks in self.subscribers.items():
                should_receive = True

                # Check spatial filters
                for sub_id, spatial_filter in self.spatial_subscriptions.items():
                    if sub_id.startswith(f"sub_{subscriber_id}"):
                        if message.geospatial_data:
                            if not spatial_filter.matches_location(message.geospatial_data.location):
                                should_receive = False
                                break
                        else:
                            # Message without geospatial data doesn't match spatial filters
                            should_receive = False
                            break

                if should_receive:
                    matching[subscriber_id] = callbacks

        return matching

    def _resolve_broadcast_recipients(self, request: BroadcastRequest, sender_id: str) -> List[str]:
        """Resolve broadcast recipients based on target criteria."""
        recipients = []

        if request.target_type == "all_users":
            # In a real implementation, would query user database
            recipients = ["user_1", "user_2", "user_3"]  # Placeholder

        elif request.target_type == "channel":
            # In a real implementation, would query channel members
            channel_id = request.target_criteria.get("channel_id")
            if channel_id:
                recipients = [f"member_{i}" for i in range(5)]  # Placeholder

        elif request.target_type == "role":
            # In a real implementation, would query users by role
            role = request.target_criteria.get("role")
            if role:
                recipients = [f"user_role_{role}_{i}" for i in range(3)]  # Placeholder

        elif request.target_type == "location_based":
            # Use spatial filtering to find users in area.
            # Without a live user-location DB, generate stable pseudo-IDs based on
            # the spatial bounds hash — allowing downstream systems to resolve them
            # against a real user registry.
            spatial_filter = request.geospatial_filter
            if spatial_filter:
                bounds = getattr(spatial_filter, 'parameters', {}) or {}
                bbox_key = f"bbox_{bounds.get('min_lat',0):.2f}_{bounds.get('max_lat',0):.2f}_{bounds.get('min_lon',0):.2f}_{bounds.get('max_lon',0):.2f}"
                import hashlib
                cell_hash = hashlib.md5(bbox_key.encode()).hexdigest()[:8]
                recipients = [f"user_spatial_{cell_hash}_1", f"user_spatial_{cell_hash}_2"]


        return recipients

    def _get_priority_value(self, priority: MessagePriority) -> int:
        """Convert message priority to queue priority value (lower = higher priority)."""
        priority_map = {
            MessagePriority.URGENT: 1,
            MessagePriority.HIGH: 2,
            MessagePriority.NORMAL: 3,
            MessagePriority.LOW: 4
        }
        return priority_map.get(priority, 3)


@dataclass
class MessageMetrics:
    """Metrics for message broker performance."""

    messages_sent: int = 0
    messages_delivered: int = 0
    delivery_failures: int = 0
    messages_queued: int = 0
    messages_processed: int = 0
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        uptime = datetime.now(timezone.utc) - self.start_time
        return {
            "messages_sent": self.messages_sent,
            "messages_delivered": self.messages_delivered,
            "delivery_failures": self.delivery_failures,
            "delivery_success_rate": (
                self.messages_delivered / max(self.messages_sent, 1) * 100
            ),
            "messages_queued": self.messages_queued,
            "messages_processed": self.messages_processed,
            "uptime_seconds": uptime.total_seconds()
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.messages_sent = 0
        self.messages_delivered = 0
        self.delivery_failures = 0
        self.messages_queued = 0
        self.messages_processed = 0
        self.start_time = datetime.now(timezone.utc)


class MessageRouter:
    """
    Advanced message routing with geospatial intelligence.

    Provides sophisticated routing capabilities including spatial filtering,
    load balancing, and intelligent message distribution.
    """

    def __init__(self, broker: MessageBroker):
        self.broker = broker
        self.routing_rules: List[RoutingRule] = []
        self.logger = logging.getLogger(__name__)

    def add_routing_rule(self, rule: RoutingRule) -> None:
        """Add a routing rule for message filtering and distribution."""
        rule.set_broker(self.broker)
        self.routing_rules.append(rule)
        self.logger.info(f"Added routing rule: {rule.name}")

    def route_message(self, message: MessageResponse) -> List[str]:
        """Route message based on configured rules."""
        routed_recipients = set()

        for rule in self.routing_rules:
            if rule.matches(message):
                recipients = rule.apply(message)
                routed_recipients.update(recipients)

        return list(routed_recipients)

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing performance statistics."""
        return {
            "total_rules": len(self.routing_rules),
            "rules": [rule.name for rule in self.routing_rules]
        }


@dataclass
class RoutingRule:
    """A rule for message routing and filtering."""

    name: str
    condition: Dict[str, Any]
    action: Dict[str, Any]
    priority: int = 1
    enabled: bool = True
    _broker: Optional['MessageBroker'] = None  # Use string annotation for forward reference

    def matches(self, message: MessageResponse) -> bool:
        """Check if message matches this routing rule."""
        if not self.enabled:
            return False

        # Simple condition matching - in production would be more sophisticated
        if "priority" in self.condition:
            if message.priority.value != self.condition["priority"]:
                return False

        if "message_type" in self.condition:
            if message.message_type.value != self.condition["message_type"]:
                return False

        if "geospatial" in self.condition and message.geospatial_data:
            # Check geospatial conditions
            geo_condition = self.condition["geospatial"]
            if not self._check_geospatial_condition(message.geospatial_data, geo_condition):
                return False

        return True

    def apply(self, message: MessageResponse) -> List[str]:
        """Apply routing rule to generate recipient list."""
        recipients = []

        action = self.action
        if "broadcast" in action and action["broadcast"]:
            # Broadcast to all users in criteria
            if "target_type" in action:
                broadcast_request = BroadcastRequest(
                    content=f"Rule-routed: {message.content}",
                    target_type=action["target_type"],
                    target_criteria=action.get("criteria", {}),
                    message_type=action.get("message_type", "notification"),
                    priority=message.priority
                )
                broadcast_response = self._broker.broadcast_message(broadcast_request, message.sender_id)
                # In a real implementation, would collect actual recipients
                recipients.extend(["broadcast_recipients"])  # Placeholder

        if "specific_recipients" in action:
            recipients.extend(action["specific_recipients"])

        return recipients

    def _check_geospatial_condition(self, geo_data: GeospatialMetadata, condition: Dict[str, Any]) -> bool:
        """Check geospatial condition against message data."""
        # Simple geospatial condition checking
        if "within_bounds" in condition:
            bounds_data = condition["within_bounds"]
            # In a real implementation, would create GeospatialBounds and check
            return True  # Placeholder

        if "within_distance" in condition:
            distance = condition["within_distance"]
            # In a real implementation, would check distance to reference point
            return True  # Placeholder

        return True

    def set_broker(self, broker: 'MessageBroker') -> None:
        """Set the message broker reference for this rule."""
        self._broker = broker


class MessageFormatter:
    """Format messages for different delivery methods and contexts."""

    @staticmethod
    def format_for_sms(message: MessageResponse, max_length: int = 160) -> str:
        """Format message for SMS delivery."""
        content = message.content
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        return f"From {message.sender_id}: {content}"

    @staticmethod
    def format_for_email(message: MessageResponse) -> Dict[str, str]:
        """Format message for email delivery."""
        return {
            "subject": f"Message from {message.sender_id}",
            "body": f"""
            You have received a message:

            From: {message.sender_id}
            Priority: {message.priority.value}
            Time: {message.timestamp.isoformat()}

            Content:
            {message.content}

            {f'Location: {message.geospatial_data.location.latitude}, {message.geospatial_data.location.longitude}' if message.geospatial_data else ''}
            """
        }

    @staticmethod
    def format_for_push_notification(message: MessageResponse) -> Dict[str, str]:
        """Format message for push notification."""
        title = f"Message from {message.sender_id}"
        body = message.content
        if len(body) > 100:
            body = body[:97] + "..."

        return {
            "title": title,
            "body": body,
            "priority": message.priority.value
        }

    @staticmethod
    def format_for_geospatial_context(message: MessageResponse) -> Dict[str, Any]:
        """Format message with geospatial context information."""
        formatted = {
            "message_id": message.message_id,
            "content": message.content,
            "sender_id": message.sender_id,
            "timestamp": message.timestamp.isoformat(),
            "priority": message.priority.value
        }

        if message.geospatial_data:
            formatted["location"] = {
                "latitude": message.geospatial_data.location.latitude,
                "longitude": message.geospatial_data.location.longitude,
                "accuracy": message.geospatial_data.accuracy,
                "source": message.geospatial_data.source
            }

            if message.geospatial_data.bounds:
                formatted["bounds"] = {
                    "min_lat": message.geospatial_data.bounds.min_latitude,
                    "min_lon": message.geospatial_data.bounds.min_longitude,
                    "max_lat": message.geospatial_data.bounds.max_latitude,
                    "max_lon": message.geospatial_data.bounds.max_longitude
                }

        return formatted
