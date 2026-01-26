# core
 ## Overview
 This directory contains core components. It includes 7 Python modules. ## Components
 ### channel
s
.py Channel management system for GEO-INFER-COMMS. **Classes**: `ChannelManager`, `ChannelMetrics`, `ChannelPermissionManager`, `ChannelMessageFilter`, `ChannelAnalytics` ### collaboratio
n
.py Collaboration system for GEO-INFER-COMMS. **Classes**: `CollaborationManager`, `CollaborationMetrics`, `RealTimeCollaborationEngine`, `GeospatialCollaborationCoordinator`, `CollaborationNotificationManager`, `CollaborationAnalytics` ### event
s
.py Event-driven communication system for GEO-INFER-COMMS. **Classes**: `EventManager`, `EventMetrics`, `EventProcessor`, `DataUpdateProcessor`, `SystemAlertProcessor`, `UserActionProcessor`, `SensorTriggerProcessor`, `GeospatialChangeProcessor`, `EventFilter`, `EventScheduler`, `ScheduledEvent`, `RecurringEvent`, `EventWebhookManager`, `WebhookConfig`, `WebhookDelivery` ### messagin
g
.py Core messaging system for GEO-INFER-COMMS. **Classes**: `MessageBroker`, `MessageMetrics`, `MessageRouter`, `RoutingRule`, `MessageFormatter` ### notification
s
.py Notification and alert system for GEO-INFER-COMMS. **Classes**: `NotificationManager`, `NotificationMetrics`, `AlertSystem`, `AlertRule`, `AlertResponse`, `NotificationFormatter`, `EmergencyAlertSystem`, `EmergencyAlert` ### spatial_routin
g
.py geospatial routing algorithms for GEO-INFER-COMMS. **Classes**: `AdvancedSpatialRouter`, `SpatialRoutingMetrics`, `GeospatialLoadBalancer`, `SpatialClusteringRouter`, `SpatialCluster`, `AdaptiveRoutingEngine`, `GeospatialMessageQueue`, `SpatialRoutingOptimizer` ### streamin
g
.py Real-time data streaming system for GEO-INFER-COMMS. **Classes**: `DataStream`, `StreamManager`, `StreamMetrics`, `GeospatialDataStream`, `StreamingProtocolManager`, `StreamingProtocol`, `WebSocketStreamingProtocol`, `MQTTStreamingProtocol`, `ServerSentEventsProtocol`, `StreamingAnalytics`, `StreamingOrchestrator` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 