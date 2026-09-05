# Irregular observations with explicit action histories

`geo_infer_time.core.action_schedule.action_observation_schedule` validates
irregular observation times for a discrete model with a fixed transition
duration. It does not resample measurements or infer missing actions.

```python
from geo_infer_time.core.action_schedule import action_observation_schedule

schedule = action_observation_schedule(
    [
        {"timestamp": "2026-01-01T00:00:00Z", "actions": []},
        {"timestamp": "2026-01-01T00:03:00Z", "actions": [0, 1, 0]},
        {"timestamp": "2026-01-01T00:04:00Z", "actions": [1]},
    ],
    step_seconds=60,
    num_actions=2,
)
assert [event.prediction_count for event in schedule] == [0, 3, 1]
assert [t.minute for t in schedule[1].prediction_timestamps] == [1, 2, 3]
```

Each input record contains exactly `timestamp` and `actions`; observation values
remain with the consuming model. The returned immutable `ScheduledObservation`
contains its UTC timestamp, a tuple of integer action indices, and a tuple of
prediction timestamps. Actions and prediction timestamps correspond in order.

The first action history must be empty: the initial prior is defined at the
first observation instant. Condition that prior on the first observation once.
For each later record, apply each supplied action to the preceding posterior
once, then condition on the new observation once. For categorical models this
means `prior = B[:, :, action] @ prior` for each recorded action. The schedule
does not select policies or update beliefs itself.

A three-minute gap in a one-minute model requires three explicit actions.
Duplicated or reversed timestamps, fractional model steps, missing actions,
extra actions and out-of-range action indices raise. Timestamps require a
timezone; equivalent offsets normalize to the same UTC instant. Boolean and
fractional action indices are rejected. The step must be finite, positive and
representable at microsecond precision; integer `timedelta` arithmetic checks
alignment without accumulating floating-point clock drift.

`max_observations` defaults to 10,000 and `max_predictions` defaults to 100,000
across the complete schedule. Bounded iteration stops even unlimited observation
or action generators. All budgets and `num_actions` must be positive integers.

This is an opt-in schedule API. The existing
`geo_infer_time.core.inference_schedule.inference_schedule` and dense GNN v1
runner retain their fixed-cadence contract. Passing an irregular schedule does
not make the GNN v1 runner accept gaps. Continuous-time dynamics with arbitrary
elapsed durations require a model that defines the appropriate propagator;
they are not approximated by rounding this schedule's step count.

## Verification

```bash
uv run --no-sync python -m pytest \
  GEO-INFER-TIME/tests/unit/test_action_schedule.py --no-cov
```

The analytic trajectory test starts at `[1, 0]`, applies transition
`[[0.8, 0.3], [0.2, 0.7]]`, swaps the states, then applies the first transition
again. At the three-minute observation its predictive distribution is
`[0.4, 0.6]`; the next swap yields `[0.6, 0.4]`. Tests also reject silent gap
repair, invalid action types, missing metadata, excess predictions and
unlimited input streams.
