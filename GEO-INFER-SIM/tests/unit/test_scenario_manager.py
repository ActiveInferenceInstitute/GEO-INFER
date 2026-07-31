"""Contract tests for scenario updates and result analysis."""

from geo_infer_sim.scenarios.scenario_manager import ScenarioManager


def test_update_scenario_accepts_explicit_empty_values() -> None:
    manager = ScenarioManager()
    scenario = manager.create_scenario(
        scenario_id="scenario-a",
        name="Initial",
        description="Initial description",
        parameters={"threshold": 1},
        initial_conditions={"state": 1},
        interventions=[{"type": "seed"}],
    )

    assert manager.update_scenario(
        scenario.scenario_id,
        name="",
        description="",
        parameters={},
        initial_conditions={},
        interventions=[],
    )
    assert scenario.name == ""
    assert scenario.description == ""
    assert scenario.interventions == []


def test_analyze_results_maps_best_metric_to_the_matching_scenario() -> None:
    manager = ScenarioManager()
    first = manager.create_scenario("First", scenario_id="first")
    second = manager.create_scenario("Second", scenario_id="second")
    manager.save_scenario_result(first.scenario_id, {"metrics": {"score": 1.0}})
    manager.save_scenario_result(second.scenario_id, {"metrics": {"score": 9.0}})

    analysis = manager.analyze_results([first.scenario_id, second.scenario_id])

    assert analysis["best_scenarios"]["score"] == {
        "scenario_id": "second",
        "value": 9.0,
        "scenario_name": "Second",
    }
