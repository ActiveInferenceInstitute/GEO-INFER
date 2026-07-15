"""Regression tests for ANT integration contracts."""

import asyncio
import logging

import numpy as np

from geo_infer_ant.core.population import AgentPopulation
from geo_infer_ant.core.agent_base import SwarmAgent


def test_perceive_environment_preserves_unconfigured_active_inference_context(
    caplog,
):
    """An unconfigured ACT model stores context without emitting API warnings."""
    agent = SwarmAgent("integration-agent", np.array([37.7, -122.4]))

    with caplog.at_level(logging.WARNING):
        sensory_input = asyncio.run(
            agent.perceive_environment(
                environmental_signals={"temperature": 18.0},
            )
        )

    assert "active_inference_observations" in sensory_input.processed_data
    assert (
        sensory_input.processed_data["active_inference_observations"]["temperature"]
        == 18.0
    )
    assert "Active Inference processing failed" not in caplog.text
    assert "Spatial analysis failed" not in caplog.text


def test_population_social_context_counts_nearby_agents_without_cell_api(caplog):
    """Population social context uses agent positions and stays warning-free."""
    population = AgentPopulation(population_size=2, agent_types=["worker"])
    population.agents[0].position = np.array([0.0, 0.0])
    population.agents[1].position = np.array([0.5, 0.0])
    population.agents[0].sensory_range = 1.0

    with caplog.at_level(logging.WARNING):
        context = population._get_social_context(population.agents[0])

    assert context["nearby_agents"] == 1
    assert context["nearby_agent_types"] == {"worker": 1}
    assert "Spatial neighbor search failed" not in caplog.text
