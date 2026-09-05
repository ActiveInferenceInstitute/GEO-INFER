"""Explicit prediction histories must account for every elapsed model step."""

from itertools import repeat

import numpy as np
import pytest

from geo_infer_time.core.action_schedule import action_observation_schedule


def test_irregular_history_matches_analytic_prediction_trajectory():
    records = [
        {"timestamp": "2026-01-01T00:00:00Z", "actions": []},
        {"timestamp": "2025-12-31T16:03:00-08:00", "actions": [0, 1, 0]},
        {"timestamp": "2026-01-01T00:04:00Z", "actions": [1]},
    ]
    schedule = action_observation_schedule(records, step_seconds=60, num_actions=2)
    assert [event.prediction_count for event in schedule] == [0, 3, 1]
    assert [t.minute for t in schedule[1].prediction_timestamps] == [1, 2, 3]
    transitions = [np.array([[0.8, 0.3], [0.2, 0.7]]), np.array([[0, 1], [1, 0]])]
    belief = np.array([1.0, 0.0])
    trajectory = []
    for event in schedule:
        for action in event.actions:
            belief = transitions[action] @ belief
        trajectory.append(belief.copy())
    np.testing.assert_allclose(trajectory, [[1, 0], [0.4, 0.6], [0.6, 0.4]])
    assert records[1]["timestamp"].endswith("-08:00")


@pytest.mark.parametrize("seconds", [0, True, 1e-8, float("inf"), 1e30])
def test_invalid_model_step(seconds):
    with pytest.raises(ValueError):
        action_observation_schedule([], step_seconds=seconds, num_actions=2)


@pytest.mark.parametrize(
    "records",
    [
        [],
        [{"timestamp": "2026-01-01", "actions": []}],
        [{"timestamp": "2026-01-01T00:00:00Z", "actions": [0]}],
        [{"timestamp": "2026-01-01T00:00:00Z", "actions": [], "observation": 1}],
        [{"timestamp": "2026-01-01T00:00:00Z"}],
    ],
)
def test_invalid_first_record(records):
    with pytest.raises(ValueError):
        action_observation_schedule(records, step_seconds=60, num_actions=2)


@pytest.mark.parametrize(
    "timestamp,actions",
    [
        ("2026-01-01T00:02:00Z", [0]),
        ("2026-01-01T00:02:00Z", [0, 0, 0]),
        ("2026-01-01T00:01:30Z", [0]),
        ("2026-01-01T00:00:00Z", []),
        ("2025-12-31T23:59:00Z", [0]),
        ("2026-01-01T00:01:00Z", [True]),
        ("2026-01-01T00:01:00Z", [0.0]),
        ("2026-01-01T00:01:00Z", [-1]),
        ("2026-01-01T00:01:00Z", [2]),
        ("2026-01-01T00:01:00Z", "0"),
    ],
)
def test_gaps_and_actions_are_never_repaired(timestamp, actions):
    with pytest.raises(ValueError):
        action_observation_schedule(
            [
                {"timestamp": "2026-01-01T00:00:00Z", "actions": []},
                {"timestamp": timestamp, "actions": actions},
            ],
            step_seconds=60,
            num_actions=2,
        )


def test_bounds_stop_unlimited_inputs_and_total_predictions():
    initial = {"timestamp": "2026-01-01T00:00:00Z", "actions": []}
    with pytest.raises(ValueError, match="max_observations"):
        action_observation_schedule(
            repeat(initial), step_seconds=60, num_actions=2, max_observations=1
        )
    with pytest.raises(ValueError, match="max_predictions"):
        action_observation_schedule(
            [
                initial,
                {"timestamp": "2026-01-01T00:02:00Z", "actions": repeat(0)},
            ],
            step_seconds=60,
            num_actions=2,
            max_predictions=1,
        )
    with pytest.raises(ValueError, match="max_predictions"):
        action_observation_schedule(
            [
                initial,
                {"timestamp": "2026-01-01T00:01:00Z", "actions": [0]},
                {"timestamp": "2026-01-01T00:02:00Z", "actions": [0]},
            ],
            step_seconds=60,
            num_actions=2,
            max_predictions=1,
        )


@pytest.mark.parametrize(
    "keyword", ["num_actions", "max_observations", "max_predictions"]
)
@pytest.mark.parametrize("value", [True, 0, -1, 1.5])
def test_invalid_budget(keyword, value):
    options = {"num_actions": 2, keyword: value}
    with pytest.raises(ValueError):
        action_observation_schedule([], step_seconds=60, **options)
