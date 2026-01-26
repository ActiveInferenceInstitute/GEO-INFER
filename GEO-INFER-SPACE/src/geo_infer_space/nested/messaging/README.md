# messaging
 ## Overview
 This directory contains messaging components. It includes 3 Python modules. ## Components
 ### message_broke
r
.py Message Broker for H3 Nested Systems. **Classes**: `MessageType`, `MessagePriority`, `MessageStatus`, `Message`, `MessageHandler`, `H3MessageBroker` ### protocol
s
.py Message Protocols for H3 Nested Systems. **Classes**: `ProtocolType`, `MessageFormat`, `ProtocolConfig`, `MessageProtocol`, `RequestResponseProtocol`, `PublishSubscribeProtocol`, `FireAndForgetProtocol`, `StreamingProtocol`, `BatchProtocol` ### routin
g
.py Message Routing for H3 Nested Systems. **Classes**: `RoutingStrategy`, `RouteMetric`, `RouteSegment`, `Route`, `MessageRouter` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 