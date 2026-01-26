# GEO
-INFER-ANT Examples and Tutorials This directory contains examples and tutorials demonstrating the functionality of the GEO-INFER-ANT swarm intelligence and complex adaptive systems framework. ## Available
 Examples ### 🚀 Demonstration (`swarm_intelligence_demo.py`) **Purpose**: demonstration of all GEO-INFER-ANT features **Features Demonstrated**: - Individual swarm agent creation and behavior - Population dynamics and management - Stigmergic communication (pheromone and digital) - Swarm optimization algorithms (ACO, PSO, ABC) - Environmental monitoring applications - Pattern analysis and emergence detection **Usage**: ```bash python examples/swarm_intelligence_demo.py ``` **Expected Output**: - simulation results - Performance metrics and analysis - JSON output file with results ### 📊 Individual Component Examples #### 1
. Basic Swarm Agents ```python from geo_infer_ant.core import SwarmAgent # Create a basic swarm agent agent = SwarmAgent( agent_id="demo_agent_001", position=np.array([37.7749, -122.4194]), # San Francisco sensory_range=100.0, active_inference_enabled=True ) # Agent perception and decision making sensory_input = await agent.perceive_environment( spatial_context={'position': agent.position}, environmental_signals={'temperature': 22.0, 'food_nearby': True} ) decision = agent.make_decision(sensory_input, motivations={'forage': 0.8}) await agent.execute_action(decision) ``` #### 2
. Population Dynamics ```python from geo_infer_ant.core import AgentPopulation # Create agent population population = AgentPopulation( population_size=1000, agent_types=['worker', 'scout', 'soldier'], spatial_distribution='clustered' ) # Initialize environment environment = population.initialize_environment( spatial_bounds={'min_lat': -10, 'max_lat': 10, 'min_lng': -10, 'max_lng': 10}, resource_distribution={'food': {'centers': [np.array([0, 0])], 'max_density': 1.0}} ) # Run simulation results = await population.run_simulation( time_steps=500, data_collection=['trajectories', 'interactions', 'emergent_patterns'] ) ``` #### 3
. Stigmergic Communication ```python from geo_infer_ant.core import PheromoneSystem, DigitalStigmergy # Pheromone-based communication pheromone_system = PheromoneSystem( spatial_resolution='h3_r8', pheromone_types=['trail', 'food', 'alarm'] ) await pheromone_system.deposit_pheromone( agent_id="agent_001", pheromone_type='trail', location=np.array([0, 0]), intensity=1.0 ) # Digital stigmergy digital_stigmergy = DigitalStigmergy( communication_medium='iot_network', information_types=['sensor_data', 'alerts'] ) await digital_stigmergy.contribute_information( agent_id="agent_001", information_type='sensor_data', content={'temperature': 22.0, 'humidity': 65.0}, location=np.array([0, 0]) ) ``` #### 4
. Optimization Algorithms ```python from geo_infer_ant.algorithms import AntColonyOptimization, ParticleSwarmOptimization # Ant Colony Optimization for path finding aco = AntColonyOptimization(number_of_ants=50, max_iterations=100) aco.initialize_problem(city_coordinates, distance_matrix) result = aco.solve() optimal_path = result.best_solution # Particle Swarm Optimization for continuous problems pso = ParticleSwarmOptimization(swarm_size=100, dimensions=2) optimal_point = pso.optimize(objective_function, bounds) ``` #### 5
. Environmental Monitoring Application ```python from geo_infer_ant.applications import EnvironmentalMonitoringSwarm # Create environmental monitoring system monitoring_swarm = EnvironmentalMonitoringSwarm( swarm_size=200, monitoring_objectives=['air_quality', 'biodiversity'], adaptive_sampling=True ) # Deploy agents and coordinate monitoring deployment = await monitoring_swarm.deploy_agents() coordination = await monitoring_swarm.coordinate_monitoring(agent_positions) # Process collective intelligence assessment = await monitoring_swarm.process_collective_intelligence( sensor_readings, spatial_interpolation='kriging', anomaly_detection='statistical' ) ``` #### 6
. Pattern Analysis ```python from geo_infer_ant.analysis import SwarmPatternAnalyzer # Analyze emergent patterns analyzer = SwarmPatternAnalyzer() spatial_patterns = analyzer.analyze_spatial_patterns( trajectories, pattern_types=['clustering', 'flocking', 'migration'] ) emergence = analyzer.detect_emergence( individual_behaviors, collective_outcomes, information_measures=['mutual_information'], complexity_measures=['fractal_dimension'] ) ``` ## Tutorial
 Structure ### 🏗️ Getting Started Tutorial **File**: `tutorials/getting_started.py` Step-by-step introduction to GEO-INFER-ANT: 1. **Basic Concepts**: Introduction to swarm intelligence and active inference 2. **Simple Agent**: Creating and running your first swarm agent 3. **Agent Communication**: Setting up stigmergic communication 4. **Basic Optimization**: Using ACO for path optimization 5. **Pattern Analysis**: Understanding emergent behaviors ### 🔬 Tutorials #### Environmenta
l
 Monitoring Tutorial **File**: `tutorials/environmental_monitoring.py` environmental monitoring with: - Multi-objective optimization - Real-time data integration - Anomaly detection and alerting - Coverage optimization #### Urba
n
 Systems Tutorial **File**: `tutorials/urban_systems.py` Urban optimization applications: - Traffic flow optimization - Resource distribution - Emergency response coordination - Infrastructure management #### Researc
h
 Applications Tutorial **File**: `tutorials/research_applications.py` Research-focused examples: - Parameter sensitivity analysis - Algorithm comparison studies - Emergence quantification - Statistical validation ## Running
 Examples ### Prerequisite
s
 ```bash # Install dependencies uv pip install numpy scipy matplotlib networkx geopandas h3 # Optional: Install integration modules uv pip install geo-infer-act geo-infer-space geo-infer-agent geo-infer-math ``` ### Basi
c
 Execution ```bash # Run demonstration python examples/swarm_intelligence_demo.py # Run specific tutorials python examples/tutorials/getting_started.py python examples/tutorials/environmental_monitoring.py ``` ### Configuratio
n
 Examples can be configured via YAML files: ```bash # Use custom configuration python examples/swarm_intelligence_demo.py --config custom_config.yaml # Specify output directory python examples/swarm_intelligence_demo.py --output results/ ``` ## Output
 and Results ### Consol
e
 Output Examples provide console logging with: - Component initialization status - Simulation progress updates - Performance metrics - Analysis results summary ### Dat
a
 Files Generated output includes: - **Simulation Results**: JSON files with metrics - **Visualization Data**: CSV files for plotting - **Analysis Reports**: analysis summaries - **Performance Logs**: Timing and efficiency metrics ### Exampl
e
 Output Structure ``` swarm_intelligence_demo_results_20250119_143022.json ├── demonstration_completed: true ├── total_execution_time: 45.67 ├── components_tested: 6 └── results: ├── swarm_agents: {count: 5} ├── population_dynamics: {population_size: 100, spatial_patterns: "..."} ├── stigmergic_communication: {pheromone_types: 3, digital_types: 3} ├── optimization_algorithms: {aco_fitness: 0.95, pso_optimal: 1.23} ├── environmental_monitoring: {anomalies_detected: 3, recommendations: 5} └── pattern_analysis: {emergence_detected: true, network_density: 0.34} ``` ## Troubleshooting
 ### Commo
n
 Issues #### Impor
t
 Errors ``` ModuleNotFoundError: No module named 'geo_infer_ant' ``` **Solution**: Ensure you're in the correct directory and modules are installed: ```bash cd /path/to/GEO-INFER/GEO-INFER-ANT uv pip install -e . ``` #### Integratio
n
 Module Errors ``` Warning: Integration modules not available ``` **Solution**: Install optional integration modules: ```bash uv pip install geo-infer-act geo-infer-space geo-infer-agent geo-infer-math ``` #### Performanc
e
 Issues ``` Warning: Large simulation may be slow ``` **Solution**: Reduce parameters for testing: ```python # In your script population_size = 50 # Instead of 1000 max_iterations = 20 # Instead of 100 ``` ### Debuggin
g
 #### Enabl
e
 Debug Logging ```python import logging logging.basicConfig(level=logging.DEBUG) ``` #### Profil
e
 Performance ```python import cProfile cProfile.run('run_demonstration()') ``` #### Memor
y
 Profiling ```python import tracemalloc tracemalloc.start() # Run your code print(tracemalloc.get_traced_memory()) ``` ## Contributing
 Examples ### Addin
g
 Examples 1. **Create Example File**: Add `.py` file in appropriate directory 2. **Follow Structure**: Include docstrings and comments 3. **Add Documentation**: Update this README with example 4. **Test Thoroughly**: Ensure example runs without errors 5. **Include Data**: Provide sample data or generation methods ### Exampl
e
 Template ```python #!/usr/bin/env python3 """ [Example Name] - [Brief Description] This example demonstrates [specific functionality]. Usage: python examples/[path]/[filename].py """ import numpy as np import logging from datetime import datetime logger = logging.getLogger(__name__) def main(): """Main example function.""" logger.info(f"Starting [Example Name] at {datetime.now()}") # Your example code here logger.info("Example completed successfully") if __name__ == "__main__": main() ``` ## Integration
 Examples ### Usin
g
 with Other GEO-INFER Modules #### Activ
e
 Inference Integration ```python from geo_infer_act.core import ActiveInferenceModel from geo_infer_ant.core import SwarmAgent # Create active inference model ai_model = ActiveInferenceModel(preferences={'forage': 0.8, 'rest': 0.6}) # Create agent with active inference agent = SwarmAgent( agent_id="ai_agent_001", position=np.array([0, 0]), active_inference_model=ai_model ) ``` #### Spatia
l
 Integration ```python from geo_infer_space.core import SpatialIndexingInterface from geo_infer_ant.core import PheromoneSystem # Create spatial indexer spatial_indexer = SpatialIndexingInterface(backend='h3') # Create spatially-aware pheromone system pheromone_system = PheromoneSystem( spatial_resolution='h3_r8', spatial_indexer=spatial_indexer ) ``` ### Custo
m
 Applications #### Creatin
g
 Custom Swarm Applications ```python from geo_infer_ant.core import SwarmAgent, AgentPopulation class CustomSwarmApplication: def __init__(self, config): self.population = AgentPopulation(**config) async def run_custom_scenario(self): # Custom application logic pass ``` ## Performance
 Benchmarks ### Benchmar
k
 Results Typical performance on standard hardware: | Component | Scale | Execution Time | Memory Usage | |-----------|-------|----------------|--------------| | ACO (50 ants, 20 cities) | Small | ~2 seconds | ~50 MB | | PSO (100 particles, 10D) | Small | ~1 second | ~30 MB | | Population (1000 agents) | Medium | ~10 seconds | ~100 MB | | Pattern Analysis | Medium | ~5 seconds | ~75 MB | | Environmental Monitoring | Large | ~30 seconds | ~200 MB | ### Optimizatio
n
 Tips 1. **Use Parallel Processing**: Enable parallel computation for large populations 2. **Spatial Partitioning**: Use H3 indexing for efficient spatial operations 3. **Caching**: Cache expensive computations and reuse results 4. **Batch Processing**: Process data in batches for memory efficiency 5. **Early Termination**: Implement convergence detection to stop early ## Research
 Applications ### Paramete
r
 Studies Examples include systematic parameter variation to understand: - Algorithm sensitivity to parameters - Optimal configurations for different problems - Trade-offs between exploration and exploitation ### Algorith
m
 Comparison Comparative studies between: - Different ACO variants (AS, ACS, MMAS) - Swarm algorithms vs traditional optimization - Single-objective vs multi-objective approaches ### Emergenc
e
 Quantification Tools for measuring and quantifying: - Information coupling between agents - Complexity measures (fractal dimension, Lyapunov exponents) - Phase transitions in collective behavior ## Getting
 Help ### Documentatio
n
 - **Module README**: `../README.md` - module documentation - **API Documentation**: `../docs/api/` - API reference - **Integration Guide**: `../docs/integration.md` - Cross-module integration ### Suppor
t
 - **Issues**: Report bugs and request features - **Discussions**: Community discussions and Q&A - **Examples**: Browse community-contributed examples ### Usag
e
 For research applications, see: - **Research Papers**: References and theoretical foundations - **Performance Optimization**: optimization techniques - **Custom Algorithms**: Extending the framework with algorithms --- **Remember**: These examples are designed to be educational and demonstrate best practices. Start with the basic examples and gradually explore more features as you become familiar with the framework. 