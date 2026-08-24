"""Crescent City civic-intelligence ingestion and categorical priors.

The producer contract is ``crescent-city-geo-intel/v1`` from the sibling
``crescent-city-intel`` repository.  This module keeps BAYES independent of a
sibling checkout by loading a reviewed package resource by default, while also
accepting an injected mapping or an explicit JSON path for refreshed inputs.

Parsing is deterministic and preserves the producer's domain ordering.  Prior
construction is also deterministic; stochastic categorical draws use the
package-wide :func:`geo_infer_bayes.utils.rng.resolve_rng` contract.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from types import MappingProxyType
from typing import Final, TypeAlias, TypedDict, cast

import numpy as np

from .utils.rng import SeedLike, resolve_rng

__all__ = [
    "CRESCENT_CITY_INTEL_SCHEMA",
    "DEFAULT_HAZARD_TAG_WEIGHTS",
    "CivicIntelSource",
    "CrescentCityIntel",
    "HazardCategoricalPrior",
    "HazardPriorEntry",
    "HazardPriorTable",
    "build_hazard_categorical_prior",
    "build_hazard_prior_table",
    "load_crescent_city_intel",
]

CRESCENT_CITY_INTEL_SCHEMA: Final[str] = "crescent-city-geo-intel/v1"
_BUNDLED_INTEL_PATH: Final[Path] = Path(__file__).with_name("crescent-city-geo-intel.json")

# Neutral modeling defaults: one hazard tag does not receive more prior mass
# than another without caller-supplied evidence.  These are policy-surface
# multipliers, not estimates of event probability, severity, or municipal risk.
DEFAULT_HAZARD_TAG_WEIGHTS: Mapping[str, float] = MappingProxyType(
    {
        "climate": 1.0,
        "earthquake": 1.0,
        "erosion": 1.0,
        "flood": 1.0,
        "landslide": 1.0,
        "sea level": 1.0,
        "seismic": 1.0,
        "storm": 1.0,
        "tsunami": 1.0,
        "wildfire": 1.0,
    }
)


class _GeoBounds(TypedDict):
    west: float
    south: float
    east: float
    north: float


class _City(TypedDict):
    name: str
    guid: str
    municipality: str
    county: str
    state: str
    latitude: float
    longitude: float


class _CivicSection(TypedDict):
    sectionNumber: str
    relevance: str


class _CivicDomain(TypedDict):
    id: str
    name: str
    icon: str
    description: str
    updatedAt: str
    topicCount: int
    tags: list[str]
    sections: list[_CivicSection]


class _HazardTopic(TypedDict):
    name: str
    tags: list[str]
    sections: list[_CivicSection]


class _HazardDomain(TypedDict):
    id: str
    name: str
    icon: str
    hazardTags: list[str]
    topics: list[_HazardTopic]


class CrescentCityIntel(TypedDict):
    """Normalized BAYES-facing view of the civic-intelligence contract."""

    city: _City | None
    domains: list[_CivicDomain]
    hazardDomains: list[_HazardDomain]
    bounds: _GeoBounds | None


class HazardPriorEntry(TypedDict):
    """Hazard-policy evidence retained for one categorical domain."""

    hazardTags: list[str]
    sectionCount: int


HazardPriorTable: TypeAlias = dict[str, HazardPriorEntry]
CivicIntelSource: TypeAlias = Mapping[str, object] | str | PathLike[str] | None


@dataclass(frozen=True, slots=True)
class HazardCategoricalPrior:
    """Categorical domain prior derived from municipal hazard-policy evidence.

    ``concentration`` contains positive Dirichlet concentration parameters and
    ``probabilities`` contains their normalized mean.  Domain positions are
    stable because :func:`build_hazard_categorical_prior` sorts domain IDs.
    """

    domains: tuple[str, ...]
    concentration: tuple[float, ...]
    probabilities: tuple[float, ...]

    def __post_init__(self) -> None:
        """Reject inconsistent or non-probabilistic direct construction."""
        lengths = {
            len(self.domains),
            len(self.concentration),
            len(self.probabilities),
        }
        if len(lengths) != 1:
            raise ValueError("domains, concentration, and probabilities must have equal length")
        if len(set(self.domains)) != len(self.domains):
            raise ValueError("hazard-prior domain IDs must be unique")
        if any(not name for name in self.domains):
            raise ValueError("hazard-prior domain IDs must be non-empty")
        if any(not math.isfinite(value) or value <= 0.0 for value in self.concentration):
            raise ValueError("hazard-prior concentrations must be finite and positive")
        if any(not math.isfinite(value) or not 0.0 <= value <= 1.0 for value in self.probabilities):
            raise ValueError("hazard-prior probabilities must lie in [0, 1]")
        if self.probabilities and not math.isclose(
            sum(self.probabilities), 1.0, rel_tol=1e-12, abs_tol=1e-12
        ):
            raise ValueError("hazard-prior probabilities must sum to one")

    def as_probability_table(self) -> dict[str, float]:
        """Return ``domain -> prior probability`` for model design matrices."""
        return dict(zip(self.domains, self.probabilities, strict=True))

    def sample(self, size: int = 1, *, seed: SeedLike = None) -> list[str]:
        """Draw hazard-domain categories through the BAYES RNG contract."""
        if isinstance(size, bool) or not isinstance(size, (int, np.integer)):
            raise TypeError("size must be an integer")
        draw_count = int(size)
        if draw_count < 0:
            raise ValueError("size must be non-negative")
        if draw_count == 0:
            return []
        if not self.domains:
            raise ValueError("cannot sample an empty hazard categorical prior")

        indices = resolve_rng(seed).choice(
            len(self.domains),
            size=draw_count,
            p=np.asarray(self.probabilities, dtype=float),
        )
        return [self.domains[int(index)] for index in indices]


def _empty_intel() -> CrescentCityIntel:
    """Return the stable absence surface used when no contract exists."""
    return {"city": None, "domains": [], "hazardDomains": [], "bounds": None}


def _require_mapping(value: object, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object")
    return cast(Mapping[str, object], value)


def _require_list(value: object, field: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be an array")
    return cast(list[object], value)


def _require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _require_string_list(value: object, field: str) -> list[str]:
    items = _require_list(value, field)
    return [_require_string(item, f"{field}[{index}]") for index, item in enumerate(items)]


def _require_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _require_float(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field} must be finite")
    return number


def _parse_bounds(value: object) -> _GeoBounds:
    raw = _require_mapping(value, "anchor.bounds")
    bounds: _GeoBounds = {
        "west": _require_float(raw.get("west"), "anchor.bounds.west"),
        "south": _require_float(raw.get("south"), "anchor.bounds.south"),
        "east": _require_float(raw.get("east"), "anchor.bounds.east"),
        "north": _require_float(raw.get("north"), "anchor.bounds.north"),
    }
    if not -180.0 <= bounds["west"] < bounds["east"] <= 180.0:
        raise ValueError("anchor bounds must satisfy -180 <= west < east <= 180")
    if not -90.0 <= bounds["south"] < bounds["north"] <= 90.0:
        raise ValueError("anchor bounds must satisfy -90 <= south < north <= 90")
    return bounds


def _parse_city(value: object) -> tuple[_City, _GeoBounds]:
    raw = _require_mapping(value, "anchor")
    city: _City = {
        "name": _require_string(raw.get("name"), "anchor.name"),
        "guid": _require_string(raw.get("guid"), "anchor.guid"),
        "municipality": _require_string(raw.get("municipality"), "anchor.municipality"),
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
    return city, _parse_bounds(raw.get("bounds"))


def _parse_section(value: object, field: str) -> _CivicSection:
    raw = _require_mapping(value, field)
    return {
        "sectionNumber": _require_string(raw.get("sectionNumber"), f"{field}.sectionNumber"),
        "relevance": _require_string(raw.get("relevance"), f"{field}.relevance"),
    }


def _parse_sections(value: object, field: str) -> list[_CivicSection]:
    return [
        _parse_section(item, f"{field}[{index}]")
        for index, item in enumerate(_require_list(value, field))
    ]


def _parse_civic_domain(value: object, index: int) -> _CivicDomain:
    field = f"domains[{index}]"
    raw = _require_mapping(value, field)
    return {
        "id": _require_string(raw.get("id"), f"{field}.id"),
        "name": _require_string(raw.get("name"), f"{field}.name"),
        "icon": _require_string(raw.get("icon"), f"{field}.icon"),
        "description": _require_string(raw.get("description"), f"{field}.description"),
        "updatedAt": _require_string(raw.get("updatedAt"), f"{field}.updatedAt"),
        "topicCount": _require_int(raw.get("topicCount"), f"{field}.topicCount"),
        "tags": _require_string_list(raw.get("tags"), f"{field}.tags"),
        "sections": _parse_sections(raw.get("sections"), f"{field}.sections"),
    }


def _parse_hazard_topic(value: object, field: str) -> _HazardTopic:
    raw = _require_mapping(value, field)
    return {
        "name": _require_string(raw.get("name"), f"{field}.name"),
        "tags": _require_string_list(raw.get("tags"), f"{field}.tags"),
        "sections": _parse_sections(raw.get("sections"), f"{field}.sections"),
    }


def _parse_hazard_domain(value: object, index: int) -> _HazardDomain:
    field = f"hazard.relevantDomains[{index}]"
    raw = _require_mapping(value, field)
    hazard_tags = _require_string_list(raw.get("hazardTags"), f"{field}.hazardTags")
    if not hazard_tags:
        raise ValueError(f"{field}.hazardTags must not be empty")
    topics = [
        _parse_hazard_topic(item, f"{field}.topics[{topic_index}]")
        for topic_index, item in enumerate(_require_list(raw.get("topics"), f"{field}.topics"))
    ]
    if not topics:
        raise ValueError(f"{field}.topics must not be empty")
    domain_tags = set(hazard_tags)
    for topic_index, topic in enumerate(topics):
        if not set(topic["tags"]).issubset(domain_tags):
            raise ValueError(f"{field}.topics[{topic_index}].tags must be listed in hazardTags")
    return {
        "id": _require_string(raw.get("id"), f"{field}.id"),
        "name": _require_string(raw.get("name"), f"{field}.name"),
        "icon": _require_string(raw.get("icon"), f"{field}.icon"),
        "hazardTags": hazard_tags,
        "topics": topics,
    }


def _load_source(source: CivicIntelSource) -> Mapping[str, object] | None:
    if isinstance(source, Mapping):
        return source

    path = _BUNDLED_INTEL_PATH if source is None else Path(source)
    try:
        raw_value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid Crescent City intel JSON at {path}: {exc}") from exc
    except OSError as exc:
        raise ValueError(f"unable to read Crescent City intel JSON at {path}: {exc}") from exc
    return _require_mapping(raw_value, "contract")


def load_crescent_city_intel(
    seed: SeedLike = None,
    *,
    source: CivicIntelSource = None,
) -> CrescentCityIntel:
    """Load and normalize a ``crescent-city-geo-intel/v1`` contract.

    Parameters
    ----------
    seed:
        Accepted for reproducible load-and-prior pipelines and validated by the
        package RNG resolver. Parsing itself does not draw randomness or advance
        a caller-owned generator.
    source:
        An injected v1 mapping, an explicit JSON path, or ``None`` to read the
        bundled reviewed contract. A missing file returns the stable empty
        surface; malformed or wrong-schema content raises :class:`ValueError`.
    """
    if seed is not None:
        resolve_rng(seed)

    contract = _load_source(source)
    if contract is None:
        return _empty_intel()

    schema = _require_string(contract.get("schema"), "schema")
    if schema != CRESCENT_CITY_INTEL_SCHEMA:
        raise ValueError(
            f"unexpected Crescent City intel schema {schema!r}; "
            f"expected {CRESCENT_CITY_INTEL_SCHEMA!r}"
        )

    city, bounds = _parse_city(contract.get("anchor"))
    domains = [
        _parse_civic_domain(value, index)
        for index, value in enumerate(_require_list(contract.get("domains"), "domains"))
    ]
    domain_count = _require_int(contract.get("domainCount"), "domainCount")
    if domain_count != len(domains):
        raise ValueError("domainCount must equal the number of domains")
    domain_ids = [domain["id"] for domain in domains]
    if len(set(domain_ids)) != len(domain_ids):
        raise ValueError("domain IDs must be unique")

    hazard = _require_mapping(contract.get("hazard"), "hazard")
    hazard_domains = [
        _parse_hazard_domain(value, index)
        for index, value in enumerate(
            _require_list(hazard.get("relevantDomains"), "hazard.relevantDomains")
        )
    ]
    relevant_count = _require_int(hazard.get("relevantDomainCount"), "hazard.relevantDomainCount")
    if relevant_count != len(hazard_domains):
        raise ValueError("hazard.relevantDomainCount must equal the number of relevantDomains")
    hazard_ids = [domain["id"] for domain in hazard_domains]
    if len(set(hazard_ids)) != len(hazard_ids):
        raise ValueError("hazard-relevant domain IDs must be unique")
    missing_domain_ids = sorted(set(hazard_ids).difference(domain_ids))
    if missing_domain_ids:
        raise ValueError(
            "hazard-relevant domains must occur in domains: " + ", ".join(missing_domain_ids)
        )

    return {
        "city": city,
        "domains": domains,
        "hazardDomains": hazard_domains,
        "bounds": bounds,
    }


def build_hazard_prior_table(intel: CrescentCityIntel) -> HazardPriorTable:
    """Map hazard domains to tags and hazard-topic code-reference counts.

    ``sectionCount`` is the number of municipal-code references carried by the
    domain's hazard-tagged topics. It intentionally excludes sections from the
    broader civic-domain summary that are not in the producer's hazard subset.
    """
    table: HazardPriorTable = {}
    for domain in sorted(intel["hazardDomains"], key=lambda item: item["id"]):
        section_count = sum(len(topic["sections"]) for topic in domain["topics"])
        table[domain["id"]] = {
            "hazardTags": sorted(set(domain["hazardTags"])),
            "sectionCount": section_count,
        }
    return table


def _validated_weight(value: object, field: str) -> float:
    weight = _require_float(value, field)
    if weight < 0.0:
        raise ValueError(f"{field} must be non-negative")
    return weight


def build_hazard_categorical_prior(
    table: HazardPriorTable,
    *,
    hazard_weights: Mapping[str, float] | None = None,
    base_concentration: float = 1.0,
    default_tag_weight: float = 1.0,
) -> HazardCategoricalPrior:
    """Convert a hazard prior table into a categorical Dirichlet mean.

    For domain ``d``, the concentration is ``base_concentration`` plus its
    hazard section count multiplied by the mean configured weight of its
    hazard tags. The mean prevents a section tagged with two hazards from being
    counted twice. Built-in tsunami, seismic, flood, erosion, and other v1
    hazard weights are all neutral ``1.0`` defaults; callers can supply
    evidence-based overrides without changing the ingestion contract.
    """
    base = _validated_weight(base_concentration, "base_concentration")
    if base <= 0.0:
        raise ValueError("base_concentration must be positive")
    fallback_weight = _validated_weight(default_tag_weight, "default_tag_weight")

    weights = dict(DEFAULT_HAZARD_TAG_WEIGHTS)
    if hazard_weights is not None:
        for raw_tag, raw_weight in hazard_weights.items():
            tag = _require_string(raw_tag, "hazard_weights key").casefold()
            weights[tag] = _validated_weight(raw_weight, f"hazard_weights[{raw_tag!r}]")

    domains = tuple(sorted(table))
    concentration_values: list[float] = []
    for domain in domains:
        entry = table[domain]
        tags = sorted({_require_string(tag, f"{domain}.hazardTags") for tag in entry["hazardTags"]})
        if not tags:
            raise ValueError(f"{domain}.hazardTags must not be empty")
        section_count = _require_int(entry["sectionCount"], f"{domain}.sectionCount")
        tag_multiplier = sum(weights.get(tag.casefold(), fallback_weight) for tag in tags) / len(
            tags
        )
        concentration_values.append(base + section_count * tag_multiplier)

    if not concentration_values:
        return HazardCategoricalPrior((), (), ())

    total = math.fsum(concentration_values)
    probabilities = tuple(value / total for value in concentration_values)
    return HazardCategoricalPrior(
        domains=domains,
        concentration=tuple(concentration_values),
        probabilities=probabilities,
    )
