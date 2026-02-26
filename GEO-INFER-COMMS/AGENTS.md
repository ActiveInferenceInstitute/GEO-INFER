# GEO-INFER-COMMS: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-COMMS** module provides communication and messaging capabilities for agents, enabling alert systems, notification delivery, and inter-agent communication in geospatial contexts.

## Agent Capabilities

### 1. Alert Broadcasting

```python
from geo_infer_comms import AlertBroadcaster

# Broadcast geospatial alerts
broadcaster = AlertBroadcaster()

alert = broadcaster.broadcast(
    alert_type="emergency",
    message="Flash flood warning in effect",
    affected_area=flood_zone_polygon,
    channels=["sms", "email", "push", "sirens"],
    priority="critical")

print(f"Recipients reached: {alert.recipients_count}")
print(f"Delivery rate: {alert.delivery_success_rate}%")```

### 2. Location-Based Notifications

```python
from geo_infer_comms import LocationNotifier

# Send location-triggered notifications
notifier = LocationNotifier()

notification = notifier.send(
    target_users=subscribed_users,
    trigger_zone=geofence_polygon,
    message="You are entering a protected area",
    trigger_type="enter")

print(f"Active geofences: {notifier.active_geofences}")
print(f"Triggered notifications: {notification.count}")```

### 3. Inter-Agent Communication

```python
from geo_infer_comms import AgentMessenger

# Enable agent-to-agent communication
messenger = AgentMessenger()

# Send message to other agents
message = messenger.send(
    from_agent="sensor_agent_001",
    to_agents=["analysis_agent", "dashboard_agent"],
    payload={
        "type": "observation",
        "location": (37.7749, -122.4194),
        "data": sensor_reading
    },
    delivery="guaranteed")

# Subscribe to topics
messenger.subscribe(
    topics=["weather_updates", "traffic_incidents"],
    callback=handle_message)
```

### 4. Multi-Channel Delivery

```python
from geo_infer_comms import MultiChannelDelivery

# Deliver across multiple channels
delivery = MultiChannelDelivery()

result = delivery.send(
    message="Infrastructure maintenance scheduled",
    recipients=affected_residents,
    channels={
        "email": {"template": "maintenance_notice"},
        "sms": {"max_length": 160},
        "push": {"action_buttons": ["details", "dismiss"]}
    },
    scheduling="immediate")

print(f"Channel delivery: {result.channel_stats}")```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **Alert Broadcasting** | ✅ Ready | Emergency alerts |
| **Location Notifications** | ✅ Ready | Geofence-triggered msgs |
| **Agent Messaging** | ✅ Ready | Inter-agent communication |
| **Multi-Channel** | ✅ Ready | SMS, email, push, etc. |

### Aspirational/Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **CommunicationsAgent** | 🔮 High | Autonomous messaging |
| **TranslationAgent** | 🔮 Medium | Multi-language support |
| **PrioritizationAgent** | 🔮 Medium | Smart message routing |

## Integration with Agent Framework

```mermaid
graph TD
    subgraph Communication_Layer
        ALERT[Alert Broadcaster]
        NOTIFY[Location Notifier]
        MESSENGER[Agent Messenger]
        CHANNEL[Multi-Channel]
    end
    
    subgraph Agents
        EMERGENCY[Emergency Agent]
        MONITOR[Monitoring Agent]
        PUBLIC[Public Info Agent]
    end
    
    EMERGENCY --> ALERT
    MONITOR --> NOTIFY
    PUBLIC --> CHANNEL
    MESSENGER -.-> EMERGENCY
    MESSENGER -.-> MONITOR
    MESSENGER -.-> PUBLIC```

## Use Cases

### 1. Emergency Alert System

```python
from geo_infer_comms import EmergencyAlertSystem

eas = EmergencyAlertSystem(jurisdiction="county")

# Issue emergency alert
eas.issue_alert(
    type="AMBER",
    description="Missing child alert",
    search_area=search_polygon,
    vehicle_description="Blue sedan, CA plate ABC123",
    broadcast_radius_miles=50)
```

### 2. Real-Time Status Updates

```python
from geo_infer_comms import StatusUpdater

updater = StatusUpdater()

# Stream status updates to subscribers
updater.stream_updates(
    event="music_festival",
    update_types=["crowd", "traffic", "weather"],
    frequency_seconds=60)
```

---

This AGENTS.md documents how GEO-INFER-COMMS provides communication capabilities for agents.

**Last Updated**: 2026-02-25

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
