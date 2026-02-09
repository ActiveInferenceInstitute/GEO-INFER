# Agent
: api

## Scope
 This directory contains api components for the module. It provides 14 classes and 1 functions.

## Classes
 and Functions

### AgentCreate
 Model for creating a agent.

### AgentAction
 Model for triggering an agent action.

### AgentMessage
 Model for agent-to-agent messages.

### AgentResponse
 Standard response model for agent operations.

### AgentInterface
 High-level interface for working with agents.

**Methods**:
- `list_agents() -> List[Dict[str, Any]]`: List all registered agents.
- `get_agent_info(agent_id: str) -> Dict[str, Any]`: Get information about an agent.
- `subscribe_to_channel(agent_id: str, channel: str) -> None`: Subscribe an agent to a channel.
- `get_agent_metrics(agent_id: str) -> Dict[str, Dict[str, Any]]`: Get metrics for an agent.
- `get_agent_health(agent_id: str) -> Dict[str, Any]`: Get health status for an agent.

### Message
 Represents an agent-to-agent message.

**Methods**:
- `is_expired() -> bool`: Check if the message has expired.
- `to_dict() -> Dict[str, Any]`: Convert message to a dictionary.
- `from_dict(cls, data: Dict[str, Any]) -> 'Message'`: Create a message from a dictionary.

### MessagingService
 Agent-to-agent messaging service.

**Methods**:
- `register_agent(agent_id: str)`: Register an agent with the messaging service.
- `unregister_agent(agent_id: str)`: Unregister an agent from the messaging service.
- `subscribe(agent_id: str, channel: str)`: Subscribe an agent to a channel.
- `unsubscribe(agent_id: str, channel: str)`: Unsubscribe an agent from a channel.
- `register_message_callback(agent_id: str, callback: Callable[[Message], None])`: Register a callback for when an agent receives a message.

### MetricType
 Enum for different metric types.

### Metric
 Base class for a telemetry metric.

**Methods**:
- `to_dict() -> Dict[str, Any]`: Convert metric to a dictionary.

### CounterMetric
 A metric that monotonically increases.

**Methods**:
- `increment(amount: int)`: Increment the counter.
- `to_dict() -> Dict[str, Any]`: Convert to dictionary.

### GaugeMetric
 A metric that can go up or down.

**Methods**:
- `set(value: float)`: Set the gauge value.
- `increment(amount: float)`: Increment the gauge.
- `decrement(amount: float)`: Decrement the gauge.
- `to_dict() -> Dict[str, Any]`: Convert to dictionary.

### HistogramMetric
 A metric that tracks the distribution of values.

**Methods**:
- `record(value: float)`: Record a value in the histogram.
- `mean() -> Optional[float]`: Calculate the mean of recorded values.
- `to_dict() -> Dict[str, Any]`: Convert to dictionary.

### TimerMetric
 A metric that measures duration.

**Methods**:
- `start()`: Start the timer.
- `stop() -> float`: Stop the timer and record the duration.
- `to_dict() -> Dict[str, Any]`: Convert to dictionary.

### TelemetryService
 Service for collecting and reporting agent telemetry.

**Methods**:
- `register_counter(name: str, description: str, agent_id: Optional[str], tags: Optional[Dict[str, str]]) -> CounterMetric`: Register a counter metric.
- `register_gauge(name: str, description: str, agent_id: Optional[str], tags: Optional[Dict[str, str]]) -> GaugeMetric`: Register a gauge metric.
- `register_histogram(name: str, description: str, agent_id: Optional[str], tags: Optional[Dict[str, str]]) -> HistogramMetric`: Register a histogram metric.
- `register_timer(name: str, description: str, agent_id: Optional[str], tags: Optional[Dict[str, str]]) -> TimerMetric`: Register a timer metric.
- `update_health(agent_id: str, status: str, details: Optional[Dict[str, Any]])`: Update health status for an agent.
- `get_metrics(agent_id: Optional[str]) -> Dict[str, Dict[str, Any]]`: Get all metrics, optionally filtered by agent ID.
- `get_health_status(agent_id: Optional[str]) -> Dict[str, Dict[str, Any]]`: Get health status for agents.
- `register_metric_callback(metric_name: str, callback: Callable[[str, Metric], None])`: Register a callback to be called when a metric is updated.

### start_api_server
 `start_api_server(host: str, port: int)` Start the API server.

## Capabilities

- **14 classes** for core functionality
- **1 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-AGENT/src/geo_infer_agent/api`
- **Type**: Directory Node
