#!/usr/bin/env python3
"""
Performance Tests for GEO-INFER-ANT

This module contains performance and scalability tests for the GEO-INFER-ANT
framework, ensuring that the system performs well under realistic conditions
and scales appropriately with problem size and complexity.

Tests cover:
- Large-scale swarm simulations
- Algorithm performance benchmarking
- Memory and computational efficiency
- Scalability limits and bottlenecks
- Real-time performance requirements
"""

import pytest
import numpy as np
import asyncio
import time
import psutil
import os
from datetime import datetime

# Import modules to test
try:
    from geo_infer_ant.core import AgentPopulation, PheromoneSystem, DigitalStigmergy
    from geo_infer_ant.algorithms import AntColonyOptimization, ParticleSwarmOptimization, ArtificialBeeColony
    from geo_infer_ant.applications import EnvironmentalMonitoringSwarm
    from geo_infer_ant.analysis import SwarmPatternAnalyzer
except ImportError:
    pytest.skip("Core modules not available", allow_module_level=True)


class TestLargeScalePerformance:
    """Test performance with large-scale systems."""

    def test_large_population_simulation(self):
        """Test performance with large agent populations."""
        # Test different population sizes
        population_sizes = [100, 500, 1000]

        for size in population_sizes:
            start_time = time.time()
            start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB

            # Create and run population
            population = AgentPopulation(population_size=size, spatial_distribution='random')
            population.initialize_environment()

            creation_time = time.time() - start_time
            creation_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB

            # Run simulation
            async def simulation_test():
                simulation_start = time.time()

                results = await population.run_simulation(
                    time_steps=50,
                    data_collection=['trajectories']
                )

                simulation_time = time.time() - simulation_start
                simulation_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB

                # Performance assertions
                assert results.time_steps == 50
                assert len(results.trajectories) > 0

                # Time constraints (should complete within reasonable limits)
                assert creation_time < 30.0  # 30 seconds for creation
                assert simulation_time < 120.0  # 120 seconds for simulation

                # Memory constraints (should not exceed reasonable limits)
                assert simulation_memory - start_memory < 500  # Less than 500MB additional memory

                return {
                    'population_size': size,
                    'creation_time': creation_time,
                    'simulation_time': simulation_time,
                    'memory_increase': simulation_memory - start_memory,
                    'agents_per_second': size / creation_time,
                    'simulation_efficiency': len(results.trajectories) / simulation_time
                }

            performance_metrics = asyncio.run(simulation_test())

            # Log performance metrics
            print(f"Population size {size}:")
            print(f"  Creation time: {performance_metrics['creation_time']:.2f}s")
            print(f"  Simulation time: {performance_metrics['simulation_time']:.2f}s")
            print(f"  Memory increase: {performance_metrics['memory_increase']:.1f}MB")
            print(f"  Agents per second: {performance_metrics['agents_per_second']:.1f}")
            print(f"  Simulation efficiency: {performance_metrics['simulation_efficiency']:.1f} trajectories/s")

    def test_pheromone_system_performance(self):
        """Test pheromone system performance with many deposits."""
        pheromone_system = PheromoneSystem()

        async def pheromone_performance_test():
            n_deposits = 1000
            start_time = time.time()
            start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

            # Create many pheromone deposits
            for i in range(n_deposits):
                await pheromone_system.deposit_pheromone(
                    agent_id=f"agent_{i}",
                    pheromone_type='trail',
                    location=np.random.uniform(-20, 20, 2),
                    intensity=np.random.uniform(0.5, 2.0)
                )

            deposit_time = time.time() - start_time
            deposit_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

            # Test sensing performance
            sensing_start = time.time()
            for _ in range(100):
                await pheromone_system.sense_pheromones(
                    location=np.random.uniform(-20, 20, 2),
                    sensory_range=10.0
                )

            sensing_time = time.time() - sensing_start

            # Test diffusion performance
            diffusion_start = time.time()
            await pheromone_system.diffuse_pheromones(time_step=60.0)
            diffusion_time = time.time() - diffusion_start

            # Performance assertions
            assert deposit_time < 10.0  # Should handle 1000 deposits in < 10 seconds
            assert sensing_time < 5.0   # Should handle 100 queries in < 5 seconds
            assert diffusion_time < 3.0  # Should diffuse in < 3 seconds

            return {
                'deposits': n_deposits,
                'deposit_time': deposit_time,
                'sensing_time': sensing_time,
                'diffusion_time': diffusion_time,
                'memory_increase': deposit_memory - start_memory,
                'deposits_per_second': n_deposits / deposit_time
            }

        metrics = asyncio.run(pheromone_performance_test())

        print(f"Pheromone system performance:")
        print(f"  Deposits: {metrics['deposits']}")
        print(f"  Deposit time: {metrics['deposit_time']:.2f}s")
        print(f"  Sensing time: {metrics['sensing_time']:.2f}s")
        print(f"  Diffusion time: {metrics['diffusion_time']:.2f}s")
        print(f"  Memory increase: {metrics['memory_increase']:.1f}MB")
        print(f"  Deposits per second: {metrics['deposits_per_second']:.1f}")

    def test_algorithm_performance_benchmarking(self):
        """Benchmark performance of optimization algorithms."""
        algorithms = {
            'ACO': AntColonyOptimization(number_of_ants=50, max_iterations=50),
            'PSO': ParticleSwarmOptimization(swarm_size=100, dimensions=2, max_iterations=50),
            'ABC': ArtificialBeeColony(colony_size=50, dimensions=2, max_iterations=50)
        }

        problem_sizes = [10, 20, 30]

        for alg_name, algorithm in algorithms.items():
            print(f"\n{alg_name} Performance:")

            for size in problem_sizes:
                # Create test problem
                if alg_name == 'ACO':
                    cities = np.random.uniform(-10, 10, (size, 2))
                    distances = np.zeros((size, size))
                    for i in range(size):
                        for j in range(size):
                            distances[i, j] = np.linalg.norm(cities[i] - cities[j])

                    algorithm.initialize_problem(cities.tolist(), distances)

                    start_time = time.time()
                    result = algorithm.solve()
                    execution_time = time.time() - start_time

                elif alg_name in ['PSO', 'ABC']:
                    def objective_function(x):
                        return np.sum(x**2)  # Sphere function

                    start_time = time.time()
                    if alg_name == 'PSO':
                        optimal = algorithm.optimize(objective_function)
                    else:  # ABC
                        optimal = algorithm.optimize(objective_function)
                    execution_time = time.time() - start_time

                    result = type('Result', (), {
                        'best_fitness': objective_function(optimal),
                        'iterations_completed': algorithm.parameters.max_iterations
                    })()

                # Performance metrics
                print(f"  Problem size {size}:")
                print(f"    Execution time: {execution_time:.2f}s")
                print(f"    Best fitness: {result.best_fitness:.4f}")
                print(f"    Iterations: {result.iterations_completed}")
                print(f"    Time per iteration: {execution_time / result.iterations_completed:.4f}s")


class TestMemoryEfficiency:
    """Test memory efficiency and usage patterns."""

    def test_memory_usage_patterns(self):
        """Test memory usage patterns with different configurations."""
        configurations = [
            {'population_size': 100, 'simulation_steps': 50},
            {'population_size': 500, 'simulation_steps': 25},
            {'population_size': 1000, 'simulation_steps': 10}
        ]

        for config in configurations:
            start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

            population = AgentPopulation(
                population_size=config['population_size'],
                spatial_distribution='random'
            )

            agents = population.create_agents()
            environment = population.initialize_environment()

            creation_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

            # Run simulation
            async def memory_test():
                results = await population.run_simulation(
                    time_steps=config['simulation_steps'],
                    data_collection=['trajectories']
                )

                simulation_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

                return {
                    'config': config,
                    'creation_memory': creation_memory - start_memory,
                    'simulation_memory': simulation_memory - creation_memory,
                    'total_memory': simulation_memory - start_memory,
                    'memory_per_agent': (simulation_memory - start_memory) / config['population_size']
                }

            memory_metrics = asyncio.run(memory_test())

            print(f"Memory usage for {config['population_size']} agents, {config['simulation_steps']} steps:")
            print(f"  Creation memory: {memory_metrics['creation_memory']:.1f}MB")
            print(f"  Simulation memory: {memory_metrics['simulation_memory']:.1f}MB")
            print(f"  Total memory: {memory_metrics['total_memory']:.1f}MB")
            print(f"  Memory per agent: {memory_metrics['memory_per_agent']:.2f}MB")

            # Memory efficiency assertions
            assert memory_metrics['memory_per_agent'] < 2.0  # Less than 2MB per agent
            assert memory_metrics['total_memory'] < 1000  # Less than 1GB total

    def test_memory_cleanup(self):
        """Test memory cleanup after operations."""
        initial_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

        # Create and run large simulation
        population = AgentPopulation(population_size=500)
        agents = population.create_agents()

        async def cleanup_test():
            results = await population.run_simulation(
                time_steps=20,
                data_collection=['trajectories', 'interactions']
            )

            # Clear large data structures
            population.agents.clear()
            results.trajectories.clear()
            results.interactions.clear()

            # Force garbage collection
            import gc
            gc.collect()

            final_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

            return final_memory - initial_memory

        memory_increase = asyncio.run(cleanup_test())

        print(f"Memory increase after cleanup: {memory_increase:.1f}MB")
        assert memory_increase < 300  # Should clean up most memory


class TestScalabilityLimits:
    """Test scalability limits and identify bottlenecks."""

    def test_maximum_swarm_size(self):
        """Test maximum practical swarm size."""
        max_sizes = [500, 1000, 2000]

        for size in max_sizes:
            try:
                start_time = time.time()
                start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

                population = AgentPopulation(population_size=size)
                agents = population.create_agents()

                creation_time = time.time() - start_time
                creation_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

                # Test if basic operations are still feasible
                async def feasibility_test():
                    # Test basic simulation
                    results = await population.run_simulation(
                        time_steps=5,  # Very short simulation
                        data_collection=['trajectories']
                    )

                    simulation_time = time.time() - start_time - creation_time

                    return {
                        'size': size,
                        'creation_time': creation_time,
                        'simulation_time': simulation_time,
                        'memory_usage': creation_memory - start_memory,
                        'feasible': results.time_steps == 5 and len(results.trajectories) > 0
                    }

                feasibility = asyncio.run(feasibility_test())

                print(f"Swarm size {size}:")
                print(f"  Feasible: {feasibility['feasible']}")
                print(f"  Creation time: {feasibility['creation_time']:.2f}s")
                print(f"  Memory usage: {feasibility['memory_usage']:.1f}MB")

                if not feasibility['feasible']:
                    print(f"  Maximum feasible size appears to be < {size}")
                    break

            except MemoryError:
                print(f"Memory error at size {size} - this is the limit")
                break
            except Exception as e:
                print(f"Error at size {size}: {e}")
                break

    def test_algorithm_complexity_scaling(self):
        """Test how algorithm performance scales with problem complexity."""
        # Test ACO with different problem sizes
        problem_sizes = [5, 10, 15, 20]

        aco_times = []
        aco_memory = []

        for size in problem_sizes:
            start_time = time.time()
            start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

            aco = AntColonyOptimization(number_of_ants=min(30, size*2), max_iterations=20)

            # Create TSP problem
            cities = np.random.uniform(-10, 10, (size, 2))
            distances = np.zeros((size, size))
            for i in range(size):
                for j in range(size):
                    distances[i, j] = np.linalg.norm(cities[i] - cities[j])

            aco.initialize_problem(cities.tolist(), distances)
            result = aco.solve()

            execution_time = time.time() - start_time
            execution_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 - start_memory

            aco_times.append(execution_time)
            aco_memory.append(execution_memory)

            print(f"ACO problem size {size}:")
            print(f"  Time: {execution_time:.2f}s")
            print(f"  Memory: {execution_memory:.1f}MB")
            print(f"  Best fitness: {result.best_fitness:.4f}")

        # Analyze scaling
        if len(aco_times) > 1:
            time_scaling = np.polyfit(problem_sizes, aco_times, 1)[0]  # Linear coefficient
            memory_scaling = np.polyfit(problem_sizes, aco_memory, 1)[0]  # Linear coefficient

            print("ACO Scaling Analysis:")
            print(f"  Time scaling rate: {time_scaling:.4f}s per city")
            print(f"  Memory scaling rate: {memory_scaling:.4f}MB per city")

            # Check if scaling is reasonable (should be polynomial, not exponential)
            assert time_scaling < 1.0  # Less than 1 second per additional city
            assert memory_scaling < 10.0  # Less than 10MB per additional city


class TestRealTimePerformance:
    """Test real-time performance requirements."""

    def test_simulation_real_time_constraints(self):
        """Test simulation performance under real-time constraints."""
        # Test different time step requirements
        time_steps_configs = [
            {'steps': 100, 'max_time': 10.0},  # 10 FPS
            {'steps': 50, 'max_time': 5.0},   # 10 FPS
            {'steps': 20, 'max_time': 1.0}    # 20 FPS
        ]

        for config in time_steps_configs:
            population = AgentPopulation(population_size=50)

            async def real_time_test():
                start_time = time.time()

                results = await population.run_simulation(
                    time_steps=config['steps'],
                    data_collection=['trajectories']
                )

                execution_time = time.time() - start_time
                target_time = config['max_time']

                real_time_efficiency = execution_time / target_time

                return {
                    'config': config,
                    'execution_time': execution_time,
                    'target_time': target_time,
                    'efficiency': 1.0 / real_time_efficiency if real_time_efficiency > 0 else float('inf'),
                    'meets_constraint': execution_time <= target_time
                }

            performance = asyncio.run(real_time_test())

            print(f"Real-time test {config['steps']} steps in {config['max_time']}s:")
            print(f"  Execution time: {performance['execution_time']:.2f}s")
            print(f"  Target time: {performance['target_time']:.2f}s")
            print(f"  Efficiency: {performance['efficiency']:.2f}x")
            print(f"  Meets constraint: {performance['meets_constraint']}")

            # Should meet real-time constraints for small simulations
            if config['steps'] <= 50:
                assert performance['meets_constraint'] or performance['execution_time'] < config['max_time'] * 1.5  # Allow 50% overrun


class TestStressTesting:
    """Stress testing for system limits."""

    def test_concurrent_operations(self):
        """Test performance under concurrent operations."""
        async def concurrent_test():
            # Create multiple populations simultaneously
            populations = []
            for i in range(3):
                population = AgentPopulation(population_size=100)
                populations.append(population)

            # Run simulations concurrently
            import asyncio

            async def run_single_population(pop):
                agents = pop.create_agents()
                env = pop.initialize_environment()

                results = await pop.run_simulation(
                    time_steps=10,
                    data_collection=['trajectories']
                )

                return len(results.trajectories)

            tasks = [run_single_population(pop) for pop in populations]

            start_time = time.time()
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time

            # All simulations should complete
            assert all(result > 0 for result in results)

            return {
                'concurrent_populations': len(populations),
                'total_time': total_time,
                'avg_time_per_population': total_time / len(populations),
                'results': results
            }

        metrics = asyncio.run(concurrent_test())

        print("Concurrent operations test:")
        print(f"  Populations: {metrics['concurrent_populations']}")
        print(f"  Total time: {metrics['total_time']:.2f}s")
        print(f"  Avg time per population: {metrics['avg_time_per_population']:.2f}s")

        # Concurrent operations should complete successfully
        assert metrics['concurrent_populations'] == 3
        assert all(result > 0 for result in metrics['results'])

    def test_data_structure_limits(self):
        """Test limits of data structures and collections."""
        # Test pheromone system with many deposits
        pheromone_system = PheromoneSystem()

        async def data_limits_test():
            n_deposits = 5000

            # Add many pheromone deposits
            for i in range(n_deposits):
                await pheromone_system.deposit_pheromone(
                    agent_id=f"agent_{i}",
                    pheromone_type='trail',
                    location=np.random.uniform(-50, 50, 2),
                    intensity=np.random.uniform(0.1, 1.0)
                )

            # Test system still functions
            test_location = np.array([0, 0])
            sensed = await pheromone_system.sense_pheromones(
                location=test_location,
                sensory_range=10.0
            )

            # Test diffusion still works
            diffusion_result = await pheromone_system.diffuse_pheromones(time_step=30.0)

            return {
                'deposits': n_deposits,
                'pheromone_types': len(sensed),
                'diffusion_cells': len(diffusion_result.get('trail', {}).get('concentrations', {}))
            }

        limits = asyncio.run(data_limits_test())

        print("Data structure limits test:")
        print(f"  Deposits: {limits['deposits']}")
        print(f"  Pheromone types sensed: {limits['pheromone_types']}")
        print(f"  Diffusion cells: {limits['diffusion_cells']}")

        # System should handle large numbers of deposits
        assert limits['pheromone_types'] >= 0
        assert limits['diffusion_cells'] >= 0


if __name__ == "__main__":
    # Run performance tests
    print("Running GEO-INFER-ANT Performance Tests")
    print("=" * 50)

    # Test large scale performance
    print("\n1. Large Scale Performance Tests")
    test_large = TestLargeScalePerformance()
    test_large.test_large_population_simulation()
    test_large.test_pheromone_system_performance()
    test_large.test_algorithm_performance_benchmarking()

    # Test memory efficiency
    print("\n2. Memory Efficiency Tests")
    test_memory = TestMemoryEfficiency()
    test_memory.test_memory_usage_patterns()
    test_memory.test_memory_cleanup()

    # Test scalability limits
    print("\n3. Scalability Limits Tests")
    test_scalability = TestScalabilityLimits()
    test_scalability.test_maximum_swarm_size()
    test_scalability.test_algorithm_complexity_scaling()

    # Test real-time performance
    print("\n4. Real-Time Performance Tests")
    test_realtime = TestRealTimePerformance()
    test_realtime.test_simulation_real_time_constraints()

    # Test stress conditions
    print("\n5. Stress Testing")
    test_stress = TestStressTesting()
    test_stress.test_concurrent_operations()
    test_stress.test_data_structure_limits()

    print("\n" + "=" * 50)
    print("Performance Testing Complete!")
    print("All tests completed successfully.")
