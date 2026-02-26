---
name: geo-infer-comms
description: Communication systems for geospatial coordination. Use when implementing spatial messaging, multi-channel notifications (email/SMS/push), event streaming, spatial message routing, or subscriber management for geographic broadcasts.
prerequisites:
  required:
    - geo-infer-api
  recommended:
    - geo-infer-data
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-COMMS

## Instructions

### Core Capabilities

- **Messaging**: Subscriber registry, spatial broadcast, geo-filtered delivery
- **Notifications**: Email, SMS, push channels (all functional — no placeholders)
- **Channels**: Multi-channel routing and priority management
- **Events**: Event streaming and spatial event processing
- **Spatial routing**: Location-aware message routing with coordinate bounds
- **Collaboration**: Real-time spatial collaboration tools
- **API security**: PyJWT primary, HMAC fallback for authentication

### Key Imports

```python
from geo_infer_comms.core.messaging import MessagingService
from geo_infer_comms.core.notifications import NotificationManager
from geo_infer_comms.core.channels import ChannelRouter
from geo_infer_comms.core.events import EventStream
from geo_infer_comms.core.spatial_routing import SpatialRouter
from geo_infer_comms.core.streaming import StreamProcessor
from geo_infer_comms.api.rest_api import CommsAPI
```

## Examples

```python
from geo_infer_comms.core.messaging import MessagingService

service = MessagingService()
service.register_subscriber("user_1", region_bounds=(-90, -180, 90, 180))
service.broadcast("Alert: flood detected", region="zone_a")
```

## Guidelines

- All 4 former placeholder blocks are resolved
- Auth uses PyJWT with HMAC fallback chain
- Test: `uv run python -m pytest GEO-INFER-COMMS/tests/ -v`

### Integrations

- **EMERGENCY** → Emergency notification broadcasting
- **IOT** → Sensor alert thresholds
- **PEP** → Stakeholder engagement notifications
- **CIV** → Community geographic broadcasts
- **OPS** → System alert delivery
