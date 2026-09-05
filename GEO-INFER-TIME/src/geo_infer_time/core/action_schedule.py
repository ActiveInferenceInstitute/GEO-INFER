"""Irregular observations with explicit, bounded discrete prediction histories."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import islice

from geo_infer_time.core.inference_schedule import inference_schedule


@dataclass(frozen=True)
class ScheduledObservation:
    """An observation instant and all actions since the preceding observation."""

    timestamp: datetime
    actions: tuple[int, ...]
    prediction_timestamps: tuple[datetime, ...]

    @property
    def prediction_count(self) -> int:
        """Number of predictions required before conditioning this observation."""
        return len(self.actions)


def action_observation_schedule(
    records: Iterable[Mapping],
    *,
    step_seconds: float,
    num_actions: int,
    max_observations: int = 10_000,
    max_predictions: int = 100_000,
) -> tuple[ScheduledObservation, ...]:
    """Validate observation gaps against caller-supplied action histories.

    Each record has exactly ``timestamp`` and ``actions``. The first action
    history is empty: the initial prior lives at that observation instant.
    Every later action advances the preceding posterior by one model step;
    there must be exactly enough actions to reach the next observation. No
    action is inferred, repeated, sorted, or selected by this function.
    """
    for name, value in (
        ("num_actions", num_actions),
        ("max_observations", max_observations),
        ("max_predictions", max_predictions),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    try:
        inference_schedule(["1970-01-01T00:00:00Z"], step_seconds=step_seconds)
        interval = timedelta(seconds=step_seconds)
    except (OverflowError, TypeError) as exc:
        raise ValueError(
            "step_seconds is outside the supported datetime range"
        ) from exc
    result: list[ScheduledObservation] = []
    total = 0
    for record in islice(records, max_observations + 1):
        if len(result) == max_observations:
            raise ValueError("Schedule exceeds max_observations")
        if not isinstance(record, Mapping) or set(record) != {"timestamp", "actions"}:
            raise ValueError("Records require exactly timestamp and actions")
        timestamp = inference_schedule(
            [record["timestamp"]], step_seconds=step_seconds
        )[0]
        actions_input = record["actions"]
        if isinstance(actions_input, (str, bytes, Mapping)):
            raise ValueError("actions must be an iterable of integer action indices")
        try:
            actions = tuple(islice(actions_input, max_predictions - total + 1))
        except TypeError as exc:
            raise ValueError(
                "actions must be an iterable of integer action indices"
            ) from exc
        if total + len(actions) > max_predictions:
            raise ValueError("Schedule exceeds max_predictions")
        if any(
            isinstance(a, bool) or not isinstance(a, int) or not 0 <= a < num_actions
            for a in actions
        ):
            raise ValueError("Action indices must be integers in [0, num_actions)")
        if not result:
            if actions:
                raise ValueError(
                    "The initial observation requires an empty action history"
                )
            prediction_times = ()
        else:
            previous = result[-1].timestamp
            elapsed = timestamp - previous
            # Integer timedelta arithmetic avoids floating-point interval rounding.
            count, remainder = divmod(elapsed, interval)
            if count < 1 or remainder != timedelta(0) or count != len(actions):
                raise ValueError(
                    "Elapsed time must equal the explicit action count times step_seconds"
                )
            prediction_times = tuple(
                previous + interval * i for i in range(1, count + 1)
            )
        result.append(ScheduledObservation(timestamp, actions, prediction_times))
        total += len(actions)
    if not result:
        raise ValueError("Observation schedule must not be empty")
    return tuple(result)
