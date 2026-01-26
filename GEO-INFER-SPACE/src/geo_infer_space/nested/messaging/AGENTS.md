# Agent
: messaging ## Scope
 This directory contains messaging components for the module. It provides 20 classes and 0 functions. ## Classes
 and Functions ### MessageTyp
e
 Types of messages in the system. ### MessagePriorit
y
 Message priority levels. ### MessageStatu
s
 Message delivery status. ### Messag
e
 Represents a message in the system. **Methods**: - `is_expired() -> bool`: Check if message has expired. - `can_retry() -> bool`: Check if message can be retried. - `to_dict() -> Dict[str, Any]`: Convert message to dictionary. ### MessageHandle
r
 Represents a message handler. **Methods**: - `can_handle(message: Message) -> bool`: Check if this handler can process the message. ### H3MessageBroke
r
 message broker for H3 nested systems. **Methods**: - `start()`: Start the message broker. - `stop()`: Stop the message broker. - `register_handler(system_id: str, handler_function: Callable[[Message], Any], message_types: Optional[Set[MessageType]], sender_filters: Optional[Set[str]], is_async: bool) -> str`: Register a message handler for a system. - `unregister_handler(handler_id: str)`: Unregister a message handler. - `send_message(sender_id: str, recipient_id: str, payload: Any, message_type: MessageType, priority: MessagePriority, ttl: Optional[timedelta], requires_response: bool, **kwargs) -> str`: Send a message. - `broadcast_message(sender_id: str, payload: Any, message_type: MessageType, priority: MessagePriority, ttl: Optional[timedelta], **kwargs) -> List[str]`: Broadcast message to all systems. - `multicast_message(sender_id: str, recipient_ids: List[str], payload: Any, message_type: MessageType, priority: MessagePriority, ttl: Optional[timedelta], **kwargs) -> List[str]`: Multicast message to specific recipients. - `send_response(original_message: Message, payload: Any, status: str) -> str`: Send response to a message. - `get_message_status(message_id: str) -> Optional[MessageStatus]`: Get status of a message. - `get_message_history(system_id: Optional[str], message_type: Optional[MessageType], limit: int) -> List[Dict[str, Any]]`: Get message history. - `get_statistics() -> Dict[str, Any]`: Get broker statistics. ### ProtocolTyp
e
 Types of communication protocols. ### MessageForma
t
 Message format types. ### ProtocolConfi
g
 Configuration for a message protocol. ### MessageProtoco
l
 Abstract base class for message protocols. **Methods**: - `send_message(sender_id: str, recipient_id: str, payload: Any, **kwargs) -> str`: Send a message using this protocol. - `handle_message(message, **kwargs) -> Any`: Handle an incoming message. - `create_session(session_id: str, participants: List[str], **kwargs) -> bool`: Create a protocol session. - `close_session(session_id: str) -> bool`: Close a protocol session. - `get_statistics() -> Dict[str, Any]`: Get protocol statistics. ### RequestResponseProtoco
l
 Request-Response protocol implementation. **Methods**: - `send_message(sender_id: str, recipient_id: str, payload: Any, **kwargs) -> str`: Send a request message. - `handle_message(message, **kwargs) -> Any`: Handle incoming request or response. - `cleanup_expired_requests()`: Clean up expired requests. ### PublishSubscribeProtoco
l
 Publish-Subscribe protocol implementation. **Methods**: - `subscribe(subscriber_id: str, topic: str) -> bool`: Subscribe to a topic. - `unsubscribe(subscriber_id: str, topic: str) -> bool`: Unsubscribe from a topic. - `send_message(sender_id: str, recipient_id: str, payload: Any, **kwargs) -> str`: Publish a message to a topic. - `handle_message(message, **kwargs) -> Any`: Handle incoming published message. ### FireAndForgetProtoco
l
 Fire-and-Forget protocol implementation. **Methods**: - `send_message(sender_id: str, recipient_id: str, payload: Any, **kwargs) -> str`: Send a fire-and-forget message. - `handle_message(message, **kwargs) -> Any`: Handle incoming fire-and-forget message. ### StreamingProtoco
l
 Streaming protocol implementation. **Methods**: - `create_stream(stream_id: str, sender_id: str, recipient_id: str, **kwargs) -> bool`: Create a streaming session. - `send_message(sender_id: str, recipient_id: str, payload: Any, **kwargs) -> str`: Send a message in a stream. - `close_stream(stream_id: str) -> bool`: Close a stream. - `handle_message(message, **kwargs) -> Any`: Handle incoming stream message. ### BatchProtoco
l
 Batch protocol implementation. **Methods**: - `send_message(sender_id: str, recipient_id: str, payload: Any, **kwargs) -> str`: Add message to batch. - `handle_message(message, **kwargs) -> Any`: Handle incoming batch message. - `flush_all_batches()`: Flush all pending batches. ### RoutingStrateg
y
 Routing strategies for message delivery. ### RouteMetri
c
 Metrics for route evaluation. ### RouteSegmen
t
 Represents a segment of a routing path. ### Rout
e
 Represents a routing path. **Methods**: - `get_path() -> List[str]`: Get the node path for this route. - `crosses_boundaries() -> bool`: Check if route crosses any boundaries. - `get_boundary_crossings() -> List[str]`: Get list of boundary IDs crossed by this route. ### MessageRoute
r
 message router for H3 nested systems. **Methods**: - `add_node(node_id: str, properties: Optional[Dict[str, Any]])`: Add a node to the routing network. - `add_edge(from_node: str, to_node: str, distance: float, latency: float, bandwidth: float, reliability: float, cost: float, bidirectional: bool, crosses_boundary: bool, boundary_id: Optional[str])`: Add an edge to the routing network. - `remove_edge(from_node: str, to_node: str, bidirectional: bool)`: Remove an edge from the routing network. - `find_route(source: str, destination: str, strategy: RoutingStrategy, metric: RouteMetric, use_cache: bool) -> Optional[Route]`: Find a route between source and destination. - `update_node_load(node_id: str, load: float)`: Update load for a node. - `update_edge_load(from_node: str, to_node: str, load: float)`: Update load for an edge. - `get_routing_statistics() -> Dict[str, Any]`: Get routing statistics. - `clear_cache()`: Clear the route cache. ## Capabilities
 - **20 classes** for core functionality ## Integration
 - **Location**: `src/geo_infer_space/nested/messaging` - **Type**: Directory Node 