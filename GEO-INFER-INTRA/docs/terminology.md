# GEO-INFER Terminology Glossary

This document serves as the central glossary for geospatial and active inference terminology used throughout the GEO-INFER framework. Consistent terminology is essential for clear communication across modules and documentation.

## Geospatial Terminology

### A

**Adjacency** - The spatial relationship between features that share a common boundary or are connected in some way.

**Aggregation (Spatial)** - The process of combining multiple spatial features into a single unit based on specified criteria.

**Antimeridian** - The 180° meridian (longitude) where the eastern and western hemispheres meet, also known as the International Date Line.

### B

**Bounding Box** - A rectangular area defined by minimum and maximum coordinates (typically as [min_lat, min_lon, max_lat, max_lon]) that encloses a geographic feature.

**Buffer** - A zone of specified width around a point, line, or polygon feature.

### C

**Centroid** - The geometric center of a spatial feature.

**Choropleth Map** - A thematic map where areas are shaded according to a statistical variable.

**Cloud Optimized GeoTIFF (COG)** - A GeoTIFF file organized to enable efficient remote access and partial file retrieval.

**Coordinate Reference System (CRS)** - A framework that defines how coordinates relate to positions on the Earth's surface; specified by datum, projection, and units.

**Coordinates** - Numeric values that define a position in space, typically as [latitude, longitude] in GEO-INFER.

### D

**Datum** - A reference framework for defining coordinates on the Earth's surface.

**Digital Elevation Model (DEM)** - A 3D representation of terrain elevation.

**Dissolve** - A GIS operation that removes boundaries between adjacent polygons that share a specified attribute.

### E

**EPSG Code** - A standardized identifier for coordinate reference systems (e.g., EPSG:4326 for WGS84).

**Edge** - A line connecting two nodes in a spatial network.

**Equidistant Projection** - A map projection that preserves distances from one or two points to all other points.

### F

**Feature** - An object that represents a real-world entity with geometry and attributes.

**Feature Collection** - A set of features, typically in formats like GeoJSON.

### G

**Geocoding** - The process of converting addresses to geographic coordinates.

**Geodesic** - The shortest path between two points on a curved surface, such as the Earth.

**Geodetic Datum** - A reference coordinate system and set of parameters that define the shape of the Earth.

**GeoJSON** - A format for encoding geographic data structures using JavaScript Object Notation.

**GeoPackage** - An open, standards-based, platform-independent, portable, self-describing, compact format for transferring geospatial information.

**GeoTIFF** - A TIFF file format that includes spatial reference information.

### H

**H3** - A hierarchical hexagonal geospatial indexing system developed by Uber.

**Heat Map** - A visualization technique that shows the density or intensity of point data using color gradients.

### I

**Interpolation (Spatial)** - The process of estimating unknown values at unsampled locations based on known values at sampled locations.

**Isochrone** - A line connecting points that can be reached in the same amount of time from a given location.

### K

**Kriging** - A geostatistical method for spatial interpolation that uses weighted averages.

### L

**Latitude** - The angular distance north or south of the equator, measured in degrees.

**Longitude** - The angular distance east or west of the Prime Meridian, measured in degrees.

### M

**Map Algebra** - A set of operations for analyzing and manipulating raster data.

**Map Projection** - A systematic transformation of coordinates from the Earth's curved surface to a flat map.

**Mercator Projection** - A cylindrical map projection that preserves angles and shapes but distorts area and distance.

### N

**NetCDF** - Network Common Data Form, a set of software libraries and machine-independent data formats for array-oriented scientific data.

**Node** - A point where two or more edges meet in a spatial network.

### O

**OGC (Open Geospatial Consortium)** - An international organization that develops open standards for geospatial content and services.

**Overlay** - A GIS operation that combines multiple spatial datasets.

### P

**Polygon** - A closed shape defined by a connected sequence of coordinates.

**Projection** - The process of transforming locations on Earth's curved surface to a flat map.

### Q

**QuadTree** - A tree data structure used to partition a two-dimensional space by recursively subdividing it into four quadrants.

### R

**Raster** - A spatial data model that represents the world as a grid of cells of equal size.

**Reverse Geocoding** - The process of converting geographic coordinates to a human-readable address.

**R-Tree** - A spatial index structure designed for efficient querying of spatial data.

### S

**Shapefile** - A vector data storage format for storing the location, shape, and attributes of geographic features.

**Spatial Index** - A data structure that improves the efficiency of spatial queries.

**Spatial Join** - An operation that appends attributes from one feature to another based on spatial relationship.

**STAC (SpatioTemporal Asset Catalog)** - A specification for cataloging spatiotemporal data.

### T

**Tessellation** - The division of a surface into a collection of non-overlapping geometric shapes.

**Topology** - The spatial relationships between connecting or adjacent features.

### U

**UTM (Universal Transverse Mercator)** - A conformal projection divided into 60 zones, each 6 degrees of longitude wide.

### V

**Vector** - A spatial data model that represents geographic features as points, lines, and polygons.

**Voronoi Diagram** - A partitioning of a plane into regions based on distance to a specified set of points.

### W

**Web Mercator** - A variant of the Mercator projection commonly used in web mapping applications (EPSG:3857).

**WGS84** - World Geodetic System 1984, a standard coordinate reference system (EPSG:4326).

**WKT (Well-Known Text)** - A text markup language for representing vector geometry.

## Active Inference Terminology

### A

**Action** - An intervention that an agent can make to change its environment or internal state.

**Active Inference** - A framework derived from the free energy principle that describes perception, learning, and decision-making as processes of minimizing variational free energy.

**Agency** - The capacity of an entity to act in its environment based on its beliefs and preferences.

### B

**Bayesian Inference** - A method of statistical inference that updates the probability of a hypothesis as more evidence becomes available.

**Belief** - A probabilistic representation of the agent's understanding of hidden states of the world.

**Belief Updating** - The process of revising beliefs based on new evidence.

### C

**Counterfactual** - A hypothetical scenario that has not occurred but could potentially occur.

### E

**Epistemic Value** - The information gain or reduction in uncertainty from an action or observation.

**Expected Free Energy (EFE)** - A quantity that agents minimize when selecting policies, comprising epistemic and pragmatic value.

### F

**Free Energy** - In active inference, a functional that provides an upper bound on surprise; minimizing free energy is equivalent to maximizing model evidence.

**Free Energy Principle (FEP)** - A principle stating that self-organizing systems resist a natural tendency to disorder by minimizing the difference between their model of the world and their sensory experience.

### G

**Generative Model** - A probabilistic model that captures how hidden states generate observations; includes prior beliefs, likelihood (observation model), and transition dynamics.

### H

**Hidden State** - Unobservable variables in the environment that the agent must infer from sensory observations.

### I

**Inference** - The process of estimating hidden states from observations using a generative model.

**Information Gain** - The reduction in uncertainty (entropy) about hidden states after making an observation.

### L

**Likelihood** - The probability of an observation given a particular hidden state; also called the observation model.

### M

**Markov Blanket** - A statistical boundary that separates a system from its environment, defining the system's conditional independence relationships.

**Markov Decision Process (MDP)** - A mathematical framework for modeling decision-making in situations where outcomes are partly random and partly under the control of a decision-maker.

### O

**Observation** - Sensory data received by an agent from its environment.

**Observation Model** - A mapping from hidden states to observations; defines the likelihood function.

### P

**Posterior** - The probability distribution over hidden states after updating with new observations; the result of inference.

**Pragmatic Value** - The expected utility or preference satisfaction from an action or outcome.

**Precision** - The inverse variance of a probability distribution; represents confidence in a prediction or observation.

**Preference** - An agent's goals or desired outcomes, encoded as prior beliefs about future observations.

**Prior** - A probability distribution representing beliefs before receiving new evidence.

**Policy** - A sequence of actions; represents a potential plan for the agent.

**Predictive Coding** - A theory positing that the brain continually generates predictions about sensory inputs and updates its model based on prediction errors.

### S

**State Space** - The set of all possible states of the system or environment.

**Surprise** - The negative log probability of an observation under a model; also called surprisal or self-information.

### T

**Transition Model** - A mapping from current states and actions to future states; defines the dynamics of the environment.

### V

**Variational Inference** - An optimization approach to approximate complex posterior distributions.

**Variational Free Energy** - A functional that provides an upper bound on surprise; the quantity minimized in active inference.

## Interdisciplinary Terms

**Geospatial Active Inference** - The application of active inference principles to geospatial systems, enabling adaptive behavior based on spatial information.

**Hierarchical Spatial Modeling** - A multi-scale approach to modeling spatial phenomena, where processes at different scales interact and inform each other.

**Spatial Belief Updating** - The process of revising beliefs about spatial phenomena based on new geospatial observations.

**Spatial Generative Model** - A probabilistic model that captures how hidden spatial states generate geospatial observations.

**Spatiotemporal Dynamics** - The evolution of spatial patterns over time, often modeled using coupled differential equations or agent-based models.

---

This glossary will be continuously updated as new terms and concepts are incorporated into the GEO-INFER framework. For suggestions or additions, please submit an issue or pull request following the contribution guidelines. 