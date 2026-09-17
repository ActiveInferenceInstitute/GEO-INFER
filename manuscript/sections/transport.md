## GEO-INFER-TRANSPORT — Transportation Planning and Traffic Analysis

GEO-INFER-TRANSPORT provides transportation planning and traffic analysis for geospatial systems (per its `README.md`). Its package `geo_infer_transport` is the most compact in the M-Z range alongside ORG and REQ — a single `core/` subpackage plus `__init__.py` at approximately 2,270 lines of Python — focusing the module on five well-defined engines rather than broad surface area.

The public interface, verified from `__init__.py`, exports five classes, one per transport concern: `TransportNetwork` for representing network topology (nodes, edges, modes) that the other engines operate on; `RoutingEngine` for path computation across that network; `TrafficAnalyzer` for flow and congestion analysis; `AccessibilityAnalyzer` for measuring how reachable destinations are from locations — a canonical geospatial-transport question; and `TransitOptimizer` for improving public-transit service configurations.

The test census counts 10 test files with 30 test classes and 113 test functions, dense relative to the module's size: each engine carries both unit-level and scenario-level coverage, giving the smallest transport module in the framework a test-to-code ratio comparable to modules several times larger.

Under the root README's Module Themes, TRANSPORT belongs to Spatial & Place-based together with SPACE, PLACE, TIME, MARINE, and WATER. Its role there is the mobility layer: PLACE analyzes what a region contains, SPACE indexes where things are, and TRANSPORT models how people and goods move between them. Its network structures also provide the corridors along which other modules — RISK's exposure models, TIME's event detection — can be spatially conditioned.
