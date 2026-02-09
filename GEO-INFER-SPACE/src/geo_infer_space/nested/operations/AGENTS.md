# Agent
: operations

## Scope
 This directory contains operations components for the module. It provides 15 classes and 0 functions.

## Classes
 and Functions

### AggregationFunction
 Types of aggregation functions.

### AggregationScope
 Scope of aggregation operations.

### AggregationRule
 Defines rules for data aggregation.

**Methods**:
- `apply(cells: List, context: Optional[Dict[str, Any]]) -> Dict[str, Any]`: Apply aggregation rule to cells.

### AggregationResult
 Result of an aggregation operation.

### H3AggregationEngine
 aggregation engine for H3 nested systems.

**Methods**:
- `add_rule(rule: AggregationRule) -> str`: Add an aggregation rule.
- `remove_rule(rule_id: str) -> bool`: Remove an aggregation rule.
- `aggregate_data(nested_grid, system_id: Optional[str], rule_ids: Optional[List[str]], **kwargs) -> AggregationResult`: Aggregate data in a nested grid system.
- `get_aggregation_statistics() -> Dict[str, Any]`: Get aggregation engine statistics.

### LumpingStrategy
 Strategies for lumping H3 cells.

### SimilarityMetric
 Metrics for measuring cell similarity.

### LumpingCriterion
 Defines criteria for lumping cells.

**Methods**:
- `evaluate(cell1, cell2) -> float`: Evaluate criterion for two cells.

### LumpingResult
 Result of a lumping operation.

### H3LumpingEngine
 lumping engine for H3 nested systems.

**Methods**:
- `add_criterion(criterion: LumpingCriterion) -> str`: Add a lumping criterion.
- `remove_criterion(criterion_id: str) -> bool`: Remove a lumping criterion.
- `lump_cells(nested_grid, strategy: LumpingStrategy, system_id: Optional[str], **kwargs) -> LumpingResult`: Lump cells in a nested grid system.
- `get_lumping_statistics() -> Dict[str, Any]`: Get lumping engine statistics.

### SplittingStrategy
 Strategies for splitting H3 cells.

### SplittingCriterion
 Criteria for determining when to split cells.

### SplittingRule
 Defines rules for splitting cells.

**Methods**:
- `should_split(cell, context: Optional[Dict[str, Any]]) -> bool`: Determine if a cell should be split based on this rule.

### SplittingResult
 Result of a splitting operation.

### H3SplittingEngine
 splitting engine for H3 nested systems.

**Methods**:
- `add_rule(rule: SplittingRule) -> str`: Add a splitting rule.
- `remove_rule(rule_id: str) -> bool`: Remove a splitting rule.
- `split_cells(nested_grid, strategy: SplittingStrategy, system_id: Optional[str], **kwargs) -> SplittingResult`: Split cells in a nested grid system.
- `get_splitting_statistics() -> Dict[str, Any]`: Get splitting engine statistics.

## Capabilities

- **15 classes** for core functionality

## Integration

- **Location**: `src/geo_infer_space/nested/operations`
- **Type**: Directory Node
