"""Crescent City civic-intelligence ingestion for hazard risk analysis.

The parser in this module consumes the frozen ``crescent-city-geo-intel/v1``
contract emitted by the sibling ``crescent-city-intel`` project.  The
canonical reviewed copy of that gold contract ships with GEO-INFER-BAYES and
is resolved here through the shared import.  It performs no discovery,
network access, or live-data fallback.
"""

from __future__ import annotations

import json
import math
import os
import warnings
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, TypeAlias, TypedDict

# Shared civic-intel ingestion core: the canonical contract loader, schema
# constant, and validator family live in GEO-INFER-BAYES, so every consumer
# resolves the SAME objects and reads the ONE reviewed
# crescent-city-geo-intel.json copy. The import stays guarded: the
# sibling-absent degradation path is a pinned contract (GEO-INFER-PLACE's
# dashboard suite simulates the absence through the real import machinery),
# so the fallback block below keeps this module's own ingest-and-weights
# surface fully working without BAYES.
CivicIntelSource: TypeAlias = Mapping[str, object] | str | os.PathLike[str] | None

try:
    from geo_infer_bayes.civic_intel import (
        CRESCENT_CITY_INTEL_SCHEMA,
        _parse_contract_anchor,
        _require_list,
        _require_mapping,
        _require_string,
        _require_string_list,
        _require_tags_within,
        load_crescent_city_contract,
    )
    from geo_infer_bayes.geo_observations import (
        CRESCENT_CITY_OBSERVATIONS_SCHEMA,  # noqa: F401 - re-exported for RISK consumers
        load_crescent_city_geo_observations,  # noqa: F401 - re-exported for RISK consumers
    )
except ImportError:  # pragma: no cover - sibling-absent degradation path
    CRESCENT_CITY_INTEL_SCHEMA = "crescent-city-geo-intel/v1"
    CRESCENT_CITY_OBSERVATIONS_SCHEMA = "crescent-city-geo-observations/v1"

    def load_crescent_city_contract(
        source: CivicIntelSource = None,
    ) -> Mapping[str, object] | None:
        raise ImportError(
            "load_crescent_city_contract requires geo-infer-bayes; the canonical"
            " crescent-city-geo-intel.json copy ships with geo-infer-bayes"
        )

    def load_crescent_city_geo_observations(
        source: Any = None,
    ) -> Mapping[str, object] | None:
        raise ImportError(
            "load_crescent_city_geo_observations requires geo-infer-bayes; the"
            " canonical crescent-city-geo-observations.json copy ships with"
            " geo-infer-bayes"
        )

    def _require_mapping(value: object, field: str) -> Mapping[str, object]:
        if not isinstance(value, Mapping):
            raise ValueError(f"{field} must be an object")
        return value

    def _require_list(value: object, field: str) -> list[object]:
        if not isinstance(value, list):
            raise ValueError(f"{field} must be an array")
        return value

    def _require_string(value: object, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")
        return value.strip()

    def _require_string_list(value: object, field: str) -> list[str]:
        items = _require_list(value, field)
        return [
            _require_string(item, f"{field}[{index}]")
            for index, item in enumerate(items)
        ]

    def _require_float(value: object, field: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field} must be a finite number")
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"{field} must be a finite number")
        return number

    def _require_tags_within(
        tags: list[str], allowed: set[str], field: str, allowed_field: str
    ) -> None:
        if not set(tags).issubset(allowed):
            raise ValueError(f"{field} must be listed in {allowed_field}")

    def _parse_contract_bounds(value: object) -> dict[str, Any]:
        """Degraded-mode WGS84 bounds validation matching the BAYES core."""
        raw = _require_mapping(value, "anchor.bounds")
        bounds = {
            "west": _require_float(raw.get("west"), "anchor.bounds.west"),
            "south": _require_float(raw.get("south"), "anchor.bounds.south"),
            "east": _require_float(raw.get("east"), "anchor.bounds.east"),
            "north": _require_float(raw.get("north"), "anchor.bounds.north"),
        }
        if not -180.0 <= bounds["west"] < bounds["east"] <= 180.0:
            raise ValueError("anchor.bounds must satisfy -180 <= west < east <= 180")
        if not -90.0 <= bounds["south"] < bounds["north"] <= 90.0:
            raise ValueError("anchor.bounds must satisfy -90 <= south < north <= 90")
        return bounds

    def _parse_contract_anchor(
        value: object,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Degraded-mode v1 anchor validation matching the BAYES core."""
        raw = _require_mapping(value, "anchor")
        city = {
            "name": _require_string(raw.get("name"), "anchor.name"),
            "guid": _require_string(raw.get("guid"), "anchor.guid"),
            "municipality": _require_string(
                raw.get("municipality"), "anchor.municipality"
            ),
            "county": _require_string(raw.get("county"), "anchor.county"),
            "state": _require_string(raw.get("state"), "anchor.state"),
            "latitude": _require_float(raw.get("latitude"), "anchor.latitude"),
            "longitude": _require_float(raw.get("longitude"), "anchor.longitude"),
        }
        if city["name"] != "Crescent City":
            raise ValueError("anchor.name must be 'Crescent City' for the v1 contract")
        if not -90.0 <= city["latitude"] <= 90.0:
            raise ValueError("anchor.latitude must lie in [-90, 90]")
        if not -180.0 <= city["longitude"] <= 180.0:
            raise ValueError("anchor.longitude must lie in [-180, 180]")
        return city, _parse_contract_bounds(raw.get("bounds"))


CRESCENT_CITY_GEO_INTEL_SCHEMA = CRESCENT_CITY_INTEL_SCHEMA


class CrescentCityBounds(TypedDict):
    """WGS84 bounding box for the Crescent City civic-intel anchor."""

    west: float
    south: float
    east: float
    north: float


class CrescentCityAnchor(TypedDict):
    """Municipal identity and WGS84 geometry from the contract anchor."""

    name: str
    guid: str
    municipality: str
    county: str
    state: str
    latitude: float
    longitude: float
    bounds: CrescentCityBounds


class MunicipalCodeSection(TypedDict):
    """One municipal-code reference attached to a hazard topic."""

    sectionNumber: str
    relevance: str


class CivicHazardDomain(TypedDict):
    """Hazard-relevant civic domain projected for risk consumers."""

    id: str
    name: str
    hazardTags: list[str]
    sections: list[MunicipalCodeSection]


class CrescentCityHazardIntel(TypedDict):
    """Normalized Crescent City hazard-policy surface."""

    city: CrescentCityAnchor | None
    hazardDomains: list[CivicHazardDomain]
    bounds: CrescentCityBounds | None


def _empty_hazard_intel() -> CrescentCityHazardIntel:
    """Return a new empty result for an absent contract source."""

    return {"city": None, "hazardDomains": [], "bounds": None}


def _required_strings(
    container: Mapping[str, object], key: str, field: str
) -> list[str]:
    """Read an ordered, de-duplicated array of non-empty strings."""

    values = _require_string_list(container.get(key), f"{field}.{key}")
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def _parse_anchor(
    contract: Mapping[str, object],
) -> tuple[CrescentCityAnchor, CrescentCityBounds]:
    """Validate and project the Crescent City anchor."""

    raw_anchor = _require_mapping(contract.get("anchor"), "anchor")
    city, bounds = _parse_contract_anchor(raw_anchor)
    anchor = CrescentCityAnchor(
        name=city["name"],
        guid=city["guid"],
        municipality=city["municipality"],
        county=city["county"],
        state=city["state"],
        latitude=city["latitude"],
        longitude=city["longitude"],
        bounds=bounds,
    )
    if not bounds["south"] <= anchor["latitude"] <= bounds["north"]:
        raise ValueError("anchor.latitude must fall within anchor.bounds")
    if not bounds["west"] <= anchor["longitude"] <= bounds["east"]:
        raise ValueError("anchor.longitude must fall within anchor.bounds")
    return anchor, bounds


def _parse_sections(
    domain: Mapping[str, object],
    domain_index: int,
    hazard_tags: Sequence[str],
) -> list[MunicipalCodeSection]:
    """Flatten and de-duplicate municipal-code refs from hazard topics."""

    field = f"hazard.relevantDomains[{domain_index}]"
    topics = _require_list(domain.get("topics"), f"{field}.topics")
    if not topics:
        raise ValueError(f"{field}.topics must not be empty")
    sections: list[MunicipalCodeSection] = []
    seen: set[tuple[str, str]] = set()
    domain_tags = set(hazard_tags)
    for topic_index, raw_topic in enumerate(topics):
        topic_field = f"{field}.topics[{topic_index}]"
        topic = _require_mapping(raw_topic, topic_field)
        _require_string(topic.get("name"), f"{topic_field}.name")
        topic_tags = _required_strings(topic, "tags", topic_field)
        if not topic_tags:
            raise ValueError(f"{topic_field}.tags must not be empty")
        _require_tags_within(
            topic_tags, domain_tags, f"{topic_field}.tags", f"{field}.hazardTags"
        )
        raw_sections = _require_list(topic.get("sections"), f"{topic_field}.sections")
        for section_index, raw_section in enumerate(raw_sections):
            section_field = f"{topic_field}.sections[{section_index}]"
            section = _require_mapping(raw_section, section_field)
            section_number = _require_string(
                section.get("sectionNumber"), f"{section_field}.sectionNumber"
            )
            relevance = _require_string(
                section.get("relevance"), f"{section_field}.relevance"
            )
            identity = (section_number, relevance)
            if identity in seen:
                continue
            seen.add(identity)
            sections.append(
                MunicipalCodeSection(
                    sectionNumber=section_number,
                    relevance=relevance,
                )
            )
    if not sections:
        raise ValueError(f"{field} must reference at least one municipal-code section")
    return sections


def _parse_hazard_domains(
    contract: Mapping[str, object],
) -> list[CivicHazardDomain]:
    """Validate and project the contract's hazard-relevant domain subset."""

    hazard = _require_mapping(contract.get("hazard"), "hazard")
    raw_domains = _require_list(hazard.get("relevantDomains"), "hazard.relevantDomains")
    declared_count = hazard.get("relevantDomainCount")
    if declared_count is not None:
        if (
            isinstance(declared_count, bool)
            or not isinstance(declared_count, int)
            or declared_count != len(raw_domains)
        ):
            raise ValueError(
                "hazard.relevantDomainCount must match hazard.relevantDomains"
            )

    domains: list[CivicHazardDomain] = []
    seen_ids: set[str] = set()
    for index, raw_domain in enumerate(raw_domains):
        field = f"hazard.relevantDomains[{index}]"
        domain = _require_mapping(raw_domain, field)
        domain_id = _require_string(domain.get("id"), f"{field}.id")
        if domain_id in seen_ids:
            raise ValueError("hazard.relevantDomains ids must be unique")
        seen_ids.add(domain_id)
        hazard_tags = _required_strings(domain, "hazardTags", field)
        if not hazard_tags:
            raise ValueError(f"{field}.hazardTags must not be empty")
        domains.append(
            CivicHazardDomain(
                id=domain_id,
                name=_require_string(domain.get("name"), f"{field}.name"),
                hazardTags=hazard_tags,
                sections=_parse_sections(domain, index, hazard_tags),
            )
        )
    return domains


def parse_crescent_city_hazard(
    contract: Mapping[str, object],
) -> CrescentCityHazardIntel:
    """Purely parse one ``crescent-city-geo-intel/v1`` mapping.

    Parameters
    ----------
    contract:
        Already-decoded JSON mapping.  Malformed or version-mismatched inputs
        fail closed with ``ValueError``.

    Returns
    -------
    CrescentCityHazardIntel
        City point, Del Norte bounds, and flattened municipal-code references
        for each hazard-relevant civic domain.
    """

    schema = contract.get("schema")
    if schema != CRESCENT_CITY_GEO_INTEL_SCHEMA:
        raise ValueError(
            f"schema must be {CRESCENT_CITY_GEO_INTEL_SCHEMA!r}; received {schema!r}"
        )
    city, bounds = _parse_anchor(contract)
    return {
        "city": city,
        "hazardDomains": _parse_hazard_domains(contract),
        "bounds": bounds,
    }


def load_crescent_city_hazard(
    source: CivicIntelSource = None,
    *,
    seed: CivicIntelSource = None,
) -> CrescentCityHazardIntel:
    """Load Crescent City hazard policy from an injected mapping or JSON path.

    ``None`` loads the reviewed package seed.  A missing package seed or
    explicit path returns an empty result.  Existing but malformed files fail
    closed.  The loader never searches sibling projects, downloads data, or
    falls back to a live service.  ``seed=`` is a deprecated alias of
    ``source=``.
    """

    if seed is not None:
        warnings.warn(
            "load_crescent_city_hazard(seed=...) is deprecated;"
            " pass the contract as source=...",
            DeprecationWarning,
            stacklevel=2,
        )
        if source is not None:
            raise TypeError("pass either source or seed, not both")
        source = seed

    if isinstance(source, Mapping):
        return parse_crescent_city_hazard(source)

    if source is None:
        # The reviewed package seed is the canonical bundled contract copy
        # owned by GEO-INFER-BAYES; RISK no longer ships its own duplicate.
        contract = load_crescent_city_contract()
        if contract is None:
            return _empty_hazard_intel()
        return parse_crescent_city_hazard(contract)

    if not isinstance(source, (str, os.PathLike)):
        raise TypeError("source must be a mapping, local JSON path, or None")

    path = Path(source)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _empty_hazard_intel()
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid Crescent City intel JSON at {path}: {exc}") from exc
    except OSError as exc:
        raise ValueError(
            f"unable to read Crescent City intel JSON at {path}: {exc}"
        ) from exc
    if not isinstance(payload, Mapping):
        raise ValueError("Crescent City intel JSON root must be an object")
    return parse_crescent_city_hazard(payload)


def _normalized_hazard_name(value: str) -> str:
    """Normalize a hazard name for policy-evidence matching."""

    return " ".join(value.strip().lower().replace("_", " ").replace("-", " ").split())


def _hazard_lookup_names(value: str) -> tuple[str, ...]:
    """Return contract-tag aliases for one RISK hazard name."""

    normalized = _normalized_hazard_name(value)
    if normalized == "earthquake":
        return ("earthquake", "seismic")
    if normalized == "seismic":
        return ("seismic", "earthquake")
    return (normalized,)


def _hazard_tag_matches(tag: str, hazard: str) -> bool:
    """Match a RISK hazard to an explicit civic tag on phrase boundaries."""

    padded_tag = f" {_normalized_hazard_name(tag)} "
    return any(f" {alias} " in padded_tag for alias in _hazard_lookup_names(hazard))


def crescent_city_hazard_weights(
    hazard_intel: CrescentCityHazardIntel,
    hazard_types: Sequence[str] | None = None,
    *,
    default_weight: float = 0.0,
) -> dict[str, float]:
    """Map municipal policy evidence to normalized RISK hazard weights.

    Each contract hazard tag receives the number of unique referenced municipal
    code sections, divided by the largest such count across the city surface.
    Thus the strongest documented tag has weight ``1.0`` and other documented
    tags are proportional.  When matrix hazards are requested, sections from
    explicit qualified tags such as ``flood zone`` and ``tsunami drill`` are
    pooled on whole-phrase boundaries before normalization.  Tags with no
    section evidence receive ``default_weight`` (``0.0`` by default).

    Pass ``MultiHazardInteractionMatrix.hazard_types`` as ``hazard_types`` to
    align keys and ordering with an existing matrix.  ``earthquake`` is matched
    to the contract's ``seismic`` tag.  Qualified tags never use substring
    inference (for example, ``storm`` does not match ``stormwater``).  These are
    policy-evidence weights, not directed causal interaction strengths, so this
    helper does not mutate the matrix.
    """

    if isinstance(default_weight, bool):
        raise ValueError("default_weight must be finite and between 0 and 1")
    numeric_default = float(default_weight)
    if not math.isfinite(numeric_default) or not 0.0 <= numeric_default <= 1.0:
        raise ValueError("default_weight must be finite and between 0 and 1")

    sections_by_tag: dict[str, set[str]] = {}
    for domain in hazard_intel["hazardDomains"]:
        section_numbers = {section["sectionNumber"] for section in domain["sections"]}
        for raw_tag in domain["hazardTags"]:
            tag = _normalized_hazard_name(raw_tag)
            sections_by_tag.setdefault(tag, set()).update(section_numbers)

    maximum_count = max(
        (len(section_numbers) for section_numbers in sections_by_tag.values()),
        default=0,
    )
    if maximum_count:
        evidence_weights = {
            tag: len(section_numbers) / maximum_count
            for tag, section_numbers in sections_by_tag.items()
        }
    else:
        evidence_weights = {tag: numeric_default for tag in sections_by_tag}

    if hazard_types is None:
        return {tag: evidence_weights[tag] for tag in sorted(evidence_weights)}
    if isinstance(hazard_types, (str, bytes)):
        raise TypeError("hazard_types must be a sequence of hazard names")

    requested = list(hazard_types)
    if any(not isinstance(hazard, str) or not hazard.strip() for hazard in requested):
        raise ValueError("hazard_types must contain non-empty strings")
    if len(set(requested)) != len(requested):
        raise ValueError("hazard_types must be unique")

    matched_sections: dict[str, set[str]] = {}
    for hazard in requested:
        matched_sections[hazard] = set().union(
            *(
                section_numbers
                for tag, section_numbers in sections_by_tag.items()
                if _hazard_tag_matches(tag, hazard)
            )
        )
    normalization_count = max(
        maximum_count,
        max(
            (len(section_numbers) for section_numbers in matched_sections.values()),
            default=0,
        ),
    )
    return {
        hazard: (
            len(section_numbers) / normalization_count
            if section_numbers and normalization_count
            else numeric_default
        )
        for hazard, section_numbers in matched_sections.items()
    }


__all__ = [
    "CRESCENT_CITY_GEO_INTEL_SCHEMA",
    "CivicHazardDomain",
    "CrescentCityAnchor",
    "CrescentCityBounds",
    "CrescentCityHazardIntel",
    "MunicipalCodeSection",
    "crescent_city_hazard_weights",
    "load_crescent_city_hazard",
    "parse_crescent_city_hazard",
]
