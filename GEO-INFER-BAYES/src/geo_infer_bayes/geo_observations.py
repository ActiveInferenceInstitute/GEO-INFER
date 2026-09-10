"""Crescent City hazard-observation ingestion (``crescent-city-geo-observations/v1``).

The producer envelope is ``crescent-city-geo-observations/v1`` from the sibling
``crescent-city-intel`` repository (``GET /api/geo-observations`` and the
committed pages seed).  It carries LIVE monitor observations — a composite
severity snapshot, per-monitor availability (``ok`` / ``empty`` /
``unavailable`` / ``stale``), and the freshness of the upstream
``crescent-city-geo-intel/v1`` policy contract — whereas the geo-intel
contract itself is the static municipal policy surface.

This module keeps BAYES independent of a sibling checkout by loading a
reviewed package resource by default, while also accepting an injected
mapping or an explicit JSON path for refreshed inputs.  Validation is
fail-closed: a wrong schema id, a missing required field, or an unrecognized
monitor status raises :class:`ValueError`; a *missing* source yields ``None``
(the sibling-absent degradation path shared with
:mod:`geo_infer_bayes.civic_intel`).

Parsing is deterministic and preserves the producer's monitor and
hazard-summary ordering.
"""

from __future__ import annotations

import importlib.resources
from collections.abc import Mapping
from os import PathLike
from pathlib import Path
from typing import Final, TypedDict

from .civic_intel import decode_contract_json

__all__ = [
    "CRESCENT_CITY_OBSERVATIONS_SCHEMA",
    "GEO_INTEL_CONTRACT_SCHEMA_REF",
    "VALID_OBSERVATION_STATUSES",
    "ObservationAnchor",
    "CompositeSnapshot",
    "MonitorObservation",
    "HazardTagSummary",
    "ObservationsFreshness",
    "load_crescent_city_geo_observations",
]

CRESCENT_CITY_OBSERVATIONS_SCHEMA: Final[str] = "crescent-city-geo-observations/v1"

#: Schema id of the upstream policy contract the envelope stays fresh against.
GEO_INTEL_CONTRACT_SCHEMA_REF: Final[str] = "crescent-city-geo-intel/v1"

_BUNDLED_OBSERVATIONS_RESOURCE: Final[str] = "crescent-city-geo-observations.json"

#: Operational statuses the producer's normalizer emits.  Unrecognized values
#: degrade to ``"unavailable"`` producer-side; consumer-side they fail closed.
VALID_OBSERVATION_STATUSES: Final[frozenset[str]] = frozenset(
    {"ok", "empty", "unavailable", "stale"}
)


class ObservationAnchor(TypedDict):
    """Municipal point identity shared with the geo-intel contract."""

    name: str
    guid: str
    municipality: str
    county: str
    state: str
    latitude: float
    longitude: float


class CompositeSnapshot(TypedDict):
    """Normalized composite severity snapshot (``CALM``..``EMERGENCY``)."""

    level: str
    reason: str
    assessedAt: str | None
    hasUnavailableMonitors: bool


class MonitorObservation(TypedDict, total=False):
    """One monitor's normalized observation entry.

    ``id``/``label``/``status`` are always present; the remaining keys are
    producer-optional (``checkedAt``, ``itemCount``, ``ageMs``, ``url``).
    """

    id: str
    label: str
    status: str
    checkedAt: str | None
    itemCount: int
    ageMs: int
    url: str


class HazardTagSummary(TypedDict):
    """Per-tag aggregation over the contract's hazard-relevant domains."""

    tag: str
    domainCount: int
    topicCount: int


class ObservationsFreshness(TypedDict):
    """Freshness of the upstream ``crescent-city-geo-intel/v1`` contract."""

    contractSchema: str
    contractGeneratedAt: str | None


def _bundled_observations_text() -> str | None:
    """Read the reviewed bundled snapshot; absent resource yields ``None``."""
    try:
        resource = importlib.resources.files("geo_infer_bayes").joinpath(
            _BUNDLED_OBSERVATIONS_RESOURCE
        )
        return resource.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def _require_fields(
    raw: Mapping[str, object], fields: tuple[str, ...], origin: str
) -> None:
    missing = [name for name in fields if name not in raw]
    if missing:
        raise ValueError(f"{origin}: missing required field(s): {', '.join(missing)}")


def _require_str(raw: Mapping[str, object], name: str, origin: str) -> str:
    value = raw.get(name)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{origin}: field {name!r} must be a non-empty string")
    return value


def _require_optional_str(
    raw: Mapping[str, object], name: str, origin: str
) -> str | None:
    value = raw.get(name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{origin}: field {name!r} must be a string or null")
    return value


def _require_finite_float(raw: Mapping[str, object], name: str, origin: str) -> float:
    value = raw.get(name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{origin}: field {name!r} must be a finite number")
    number = float(value)
    if number != number or number in (float("inf"), float("-inf")):
        raise ValueError(f"{origin}: field {name!r} must be a finite number")
    return number


def _validate_anchor(anchor: object, origin: str) -> None:
    if not isinstance(anchor, Mapping):
        raise ValueError(f"{origin}: 'anchor' must be an object")
    _require_fields(
        anchor,
        ("name", "guid", "municipality", "county", "state", "latitude", "longitude"),
        f"{origin} anchor",
    )
    for name in ("name", "guid", "municipality", "county", "state"):
        _require_str(anchor, name, f"{origin} anchor")
    _require_finite_float(anchor, "latitude", f"{origin} anchor")
    _require_finite_float(anchor, "longitude", f"{origin} anchor")


def _validate_composite(composite: object, origin: str) -> None:
    if composite is None:
        return
    if not isinstance(composite, Mapping):
        raise ValueError(f"{origin}: 'composite' must be an object or null")
    _require_fields(
        composite,
        ("level", "reason", "assessedAt", "hasUnavailableMonitors"),
        f"{origin} composite",
    )
    _require_str(composite, "level", f"{origin} composite")
    if not isinstance(composite.get("reason"), str):
        raise ValueError(f"{origin}: composite 'reason' must be a string")
    _require_optional_str(composite, "assessedAt", f"{origin} composite")
    if not isinstance(composite.get("hasUnavailableMonitors"), bool):
        raise ValueError(
            f"{origin}: composite 'hasUnavailableMonitors' must be a boolean"
        )


def _validate_monitors(monitors: object, origin: str) -> None:
    if not isinstance(monitors, list):
        raise ValueError(f"{origin}: 'monitors' must be an array")
    for index, monitor in enumerate(monitors):
        label = f"{origin} monitors[{index}]"
        if not isinstance(monitor, Mapping):
            raise ValueError(f"{label} must be an object")
        _require_fields(monitor, ("id", "label", "status"), label)
        _require_str(monitor, "id", label)
        _require_str(monitor, "label", label)
        status = _require_str(monitor, "status", label)
        if status not in VALID_OBSERVATION_STATUSES:
            raise ValueError(
                f"{label}: unrecognized status {status!r}; expected one of "
                f"{sorted(VALID_OBSERVATION_STATUSES)}"
            )
        _require_optional_str(monitor, "checkedAt", label)
        item_count = monitor.get("itemCount")
        if item_count is not None and (
            isinstance(item_count, bool) or not isinstance(item_count, int)
        ):
            raise ValueError(f"{label}: 'itemCount' must be an integer or null")
        age_ms = monitor.get("ageMs")
        if age_ms is not None and (
            isinstance(age_ms, bool) or not isinstance(age_ms, int)
        ):
            raise ValueError(f"{label}: 'ageMs' must be an integer or null")
        url = monitor.get("url")
        if url is not None and not isinstance(url, str):
            raise ValueError(f"{label}: 'url' must be a string or null")


def _validate_hazard_summary(hazard_summary: object, origin: str) -> None:
    if not isinstance(hazard_summary, list):
        raise ValueError(f"{origin}: 'hazardSummary' must be an array")
    for index, entry in enumerate(hazard_summary):
        label = f"{origin} hazardSummary[{index}]"
        if not isinstance(entry, Mapping):
            raise ValueError(f"{label} must be an object")
        _require_fields(entry, ("tag", "domainCount", "topicCount"), label)
        _require_str(entry, "tag", label)
        for count_field in ("domainCount", "topicCount"):
            value = entry.get(count_field)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{label}: {count_field!r} must be an integer")


def _validate_freshness(freshness: object, origin: str) -> None:
    if not isinstance(freshness, Mapping):
        raise ValueError(f"{origin}: 'freshness' must be an object")
    _require_fields(
        freshness, ("contractSchema", "contractGeneratedAt"), f"{origin} freshness"
    )
    if (
        _require_str(freshness, "contractSchema", f"{origin} freshness")
        != GEO_INTEL_CONTRACT_SCHEMA_REF
    ):
        raise ValueError(
            f"{origin}: freshness 'contractSchema' must be {GEO_INTEL_CONTRACT_SCHEMA_REF!r}"
        )
    _require_optional_str(freshness, "contractGeneratedAt", f"{origin} freshness")


def validate_geo_observations(envelope: object, origin: str) -> Mapping[str, object]:
    """Validate a ``crescent-city-geo-observations/v1`` envelope, fail-closed.

    Returns the envelope unchanged (producer ordering preserved) when valid;
    raises :class:`ValueError` describing the first structural violation
    otherwise.  Producer-optional monitor keys (``checkedAt``, ``itemCount``,
    ``ageMs``, ``url``) pass through unmodified.
    """
    if not isinstance(envelope, Mapping):
        raise ValueError(f"{origin}: observations envelope must be a JSON object")
    _require_fields(
        envelope,
        (
            "schema",
            "anchor",
            "generatedAt",
            "composite",
            "monitors",
            "hazardSummary",
            "freshness",
        ),
        origin,
    )
    schema = _require_str(envelope, "schema", origin)
    if schema != CRESCENT_CITY_OBSERVATIONS_SCHEMA:
        raise ValueError(
            f"{origin}: expected schema {CRESCENT_CITY_OBSERVATIONS_SCHEMA!r}, got {schema!r}"
        )
    _validate_anchor(envelope.get("anchor"), origin)
    _require_str(envelope, "generatedAt", origin)
    _validate_composite(envelope.get("composite"), origin)
    _validate_monitors(envelope.get("monitors"), origin)
    _validate_hazard_summary(envelope.get("hazardSummary"), origin)
    _validate_freshness(envelope.get("freshness"), origin)
    return envelope


def load_crescent_city_geo_observations(
    source: Mapping[str, object] | str | PathLike[str] | None = None,
) -> Mapping[str, object] | None:
    """Resolve a raw ``crescent-city-geo-observations/v1`` envelope.

    This is the shared observation-ingestion core for the GEO-INFER
    civic-intel family: ``geo_infer_act.core.civic_intel`` and
    ``geo_infer_risk.civic_intel`` delegate here so live observations are
    read from exactly one canonical reviewed copy.

    Parameters
    ----------
    source:
        An injected v1 mapping (validated and passed through unchanged), an
        explicit JSON path, or ``None`` to read the bundled reviewed snapshot
        via :mod:`importlib.resources`.  A missing file or absent resource
        yields ``None``; existing but unreadable, malformed, or structurally
        invalid JSON fails closed with :class:`ValueError`.
    """
    if isinstance(source, Mapping):
        return validate_geo_observations(source, "injected observations mapping")

    if source is None:
        text = _bundled_observations_text()
        if text is None:
            return None
        return validate_geo_observations(
            decode_contract_json(
                text, f"geo_infer_bayes/{_BUNDLED_OBSERVATIONS_RESOURCE}"
            ),
            f"geo_infer_bayes/{_BUNDLED_OBSERVATIONS_RESOURCE}",
        )

    path = Path(source)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    return validate_geo_observations(
        decode_contract_json(text, str(path)),
        str(path),
    )
