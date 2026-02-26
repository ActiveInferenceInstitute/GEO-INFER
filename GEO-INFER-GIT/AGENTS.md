# GEO-INFER-GIT: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-GIT** module provides version control and collaboration capabilities for agents, enabling automated change tracking, versioning of geospatial data, and coordinated development workflows.

## Agent Capabilities

### 1. Version Control Operations

```python
from geo_infer_git import VersionController

# Initialize version control for agent
versioning = VersionController(repo_path="./my_project")

# Agent commits changes
versioning.commit(
    changes=modified_files,
    message="Agent-generated spatial analysis update",
    author="GeoAgent <agent@geo-infer.org>")

# Track modification history
history = versioning.get_history(file_path="spatial_data.geojson")```

### 2. Change Detection

```python
from geo_infer_git import ChangeTracker

# Monitor for changes
tracker = ChangeTracker(watch_path="./data")

# Detect spatial data modifications
changes = tracker.detect_changes()
for change in changes:
    print(f"Modified: {change.file_path}")
    print(f"Type: {change.change_type}") 

# added, modified, deleted
    print(f"Diff: {change.diff_summary}")```

### 3. Geospatial Data Versioning

```python
from geo_infer_git import SpatialDataVersioner

# Version geospatial datasets
versioner = SpatialDataVersioner()

# Create versioned snapshot of spatial data
version = versioner.snapshot(
    data_path="./regions.geojson",
    metadata={
        "source": "census_2025",
        "resolution": "block_group",
        "crs": "EPSG:4326"
    })

# Compare versions
diff = versioner.compare(version_a="v1.0", version_b="v1.1")
print(f"Features added: {diff.features_added}")
print(f"Features modified: {diff.features_modified}")```

### 4. Multi-Agent Collaboration

```python
from geo_infer_git import CollaborationManager

# Coordinate multiple agents working on same data
collab = CollaborationManager(project="urban_analysis")

# Register agent
collab.register_agent(agent_id="agent_001", role="data_processor")

# Lock file for exclusive access
with collab.lock("shared_data.geojson"):
   

# Agent performs exclusive operations
    process_data()

# Merge changes from multiple agents
collab.merge_agent_changes(
    source_agent="agent_001",
    target_branch="main")
```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **Version Control** | ✅ Ready | Git integration for agents |
| **Change Tracking** | ✅ Ready | Automated change detection |
| **Collaboration** | ✅ Ready | Multi-agent coordination |
| **Data Versioning** | ✅ Ready | Geospatial data snapshots |
| **History Management** | ✅ Ready | Change history and audit |

### Aspirational/Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **AutoVersioningAgent** | 🔮 High | Automatic semantic versioning |
| **MergeResolutionAgent** | 🔮 High | AI-powered conflict resolution |
| **BranchingStrategyAgent** | 🔮 Medium | Optimized branching decisions |

## Agent Workflow Integration

```mermaid
graph TD
    subgraph Agent_Workflow
        A1[Agent 1: Data Collection] --> COMMIT1[Commit Changes]
        A2[Agent 2: Analysis] --> COMMIT2[Commit Changes]
        A3[Agent 3: Validation] --> COMMIT3[Commit Changes]
    end
    
    subgraph Version_Control
        COMMIT1 --> BRANCH1[Feature Branch 1]
        COMMIT2 --> BRANCH2[Feature Branch 2]
        COMMIT3 --> BRANCH3[Feature Branch 3]
        BRANCH1 --> MERGE[Merge to Main]
        BRANCH2 --> MERGE
        BRANCH3 --> MERGE
    end
    
    subgraph Collaboration
        MERGE --> RESOLVE[Conflict Resolution]
        RESOLVE --> MAIN[Main Branch]
    end```

## Use Cases

### 1. Automated Data Pipeline Versioning

```python
from geo_infer_git import VersionController
from geo_infer_agent import DataPipelineAgent

class VersionedPipelineAgent(DataPipelineAgent):
    def __init__(self):
        super().__init__()
        self.versioning = VersionController()
    
    def process_and_version(self, input_data):
       

# Process data
        output = self.process(input_data)
        
       

# Save and version results
        self.save(output, "results/analysis.geojson")
        self.versioning.commit(
            message=f"Pipeline run: {self.run_id}",
            changes=["results/analysis.geojson"]
        )
        
        return output```

### 2. Collaborative Spatial Analysis

```python
from geo_infer_git import CollaborationManager

# Multiple agents collaborate on spatial analysis
collab = CollaborationManager(project="city_planning")

# Agent A: Land use analysis
agent_a.analyze_land_use()
collab.push_changes(agent_id="land_use_agent")

# Agent B: Traffic analysis  
agent_b.analyze_traffic()
collab.push_changes(agent_id="traffic_agent")

# Merge and validate
collab.merge_all()
validation_agent.validate_combined_results()```

### 3. Data Provenance Tracking

```python
from geo_infer_git import ProvenanceTracker

tracker = ProvenanceTracker()

# Track data lineage
tracker.record_transformation(
    input_files=["raw_data.csv"],
    output_files=["processed.geojson"],
    transformation="spatial_join",
    agent_id="processing_agent")

# Query provenance
lineage = tracker.get_lineage("processed.geojson")
print(f"Origin: {lineage.origin}")
print(f"Transformations: {lineage.transformations}")```

---

This AGENTS.md documents how GEO-INFER-GIT provides version control and collaboration capabilities for agents.

**Last Updated**: 2026-02-25

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
