"""Crescent City civic-intel ingestion and municipal hazard policy-prior plating.

This module pulls the sibling ``crescent-city-intel`` geo-intel contract
(``crescent-city-geo-intel/v1``) into GEO-INFER-ACT so that Active Inference
over Crescent City can treat municipal hazard policy as structured priors and
observables rather than hand-authored constants.

The contract exposes a Crescent City anchor, twelve civic domains, and a
hazard-relevant subset (tsunami/seismic/flood/fire-tagged municipal code
sections). ``parse_crescent_city_intel`` lowers that shape into a typed,
dict-shaped record; ``hazard_policy_prior`` maps the hazard subset into
preference weights that a :class:`geo_infer_act.core.policy_selection.PolicySelector`
can consume directly, so inference policies are weighted by Crescent City
municipal hazard intent.

All parsing is deterministic. Randomness (when requested) follows the same
RNG contract used across GEO-INFER-ACT: an explicit ``np.random.default_rng``
instance seeded by the caller, with ``seed=None`` producing a fully
deterministic result.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import numpy as np

SUPPORTED_SCHEMA = "crescent-city-geo-intel/v1"
ENV_CONTRACT_PATH = "CRESCENT_CITY_INTEL_CONTRACT_PATH"

# Path to the sibling crescent-city-intel contract relative to this checkout.
_DEFAULT_CONTRACT_RELATIVE = (
    Path("crescent-city-intel") / "pages-data" / "geo-intel.json"
)

# Municipal hazard tags recognised in the contract and how strongly a policy
# should avoid the state they mark. A higher value means the state is less
# desirable, so preference weight = 1 - avoidance.
HAZARD_AVOIDANCE: Dict[str, float] = {
    "tsunami": 0.90,
    "seismic": 0.85,
    "flood": 0.75,
    "fire": 0.70,
    "inundation": 0.65,
    "erosion": 0.60,
}
_DEFAULT_AVOIDANCE = 0.5
_MIN_PREFERENCE = 1e-6

# The baseline (all-clear / non-hazard-aware) state is the most preferred.
_BASELINE_PREFERENCE = 1.0

# Match configured base hazards as complete terms inside qualified producer
# tags (for example, ``flood zone`` or ``tsunami drill``). The alphanumeric
# lookarounds deliberately reject substring collisions such as ``backfire``.
_HAZARD_TERM_PATTERNS = {
    tag: re.compile(rf"(?<![0-9a-z]){re.escape(tag)}(?![0-9a-z])")
    for tag in HAZARD_AVOIDANCE
}


@dataclass(frozen=True)
class CivicIntelBounds:
    """Municipal bounding box from the contract anchor."""

    west: float
    south: float
    east: float
    north: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "west": float(self.west),
            "south": float(self.south),
            "east": float(self.east),
            "north": float(self.north),
        }


@dataclass(frozen=True)
class GeoIntelSection:
    """A municipal code section referenced by a civic topic."""

    sectionNumber: str
    relevance: str = ""


@dataclass(frozen=True)
class GeoIntelTopic:
    """A hazard-relevant topic within a civic domain."""

    name: str
    tags: List[str] = field(default_factory=list)
    sections: List[GeoIntelSection] = field(default_factory=list)


@dataclass(frozen=True)
class HazardDomain:
    """A civic domain flagged as hazard-relevant by the contract."""

    id: str
    name: str
    hazardTags: List[str]
    topics: List[GeoIntelTopic] = field(default_factory=list)
    icon: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "hazardTags": list(self.hazardTags),
            "topics": [
                {
                    "name": topic.name,
                    "tags": list(topic.tags),
                    "sections": [
                        {
                            "sectionNumber": section.sectionNumber,
                            "relevance": section.relevance,
                        }
                        for section in topic.sections
                    ],
                }
                for topic in self.topics
            ],
        }


@dataclass(frozen=True)
class CrescentCityIntel:
    """Typed view of the crescent-city-geo-intel/v1 contract.

    ``hazardDomains`` is the hazard-relevant subset the contract marks
    explicitly (falling back to a tag-driven scan of the full domain list
    when the contract omits the hazard subset).
    """

    city: str
    hazardDomains: List[HazardDomain]
    bounds: Optional[CivicIntelBounds]
    schema: Optional[str] = None
    anchor: Dict[str, Any] = field(default_factory=dict)
    generatedAt: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "city": self.city,
            "anchor": dict(self.anchor),
            "generatedAt": self.generatedAt,
            "bounds": self.bounds.as_dict() if self.bounds is not None else {},
            "hazardDomains": [domain.as_dict() for domain in self.hazardDomains],
        }


def default_contract_path() -> Path:
    """Return the path to the sibling crescent-city-intel contract.

    Honors ``CRESCENT_CITY_INTEL_CONTRACT_PATH`` when set, otherwise resolves
    ``crescent-city-intel/pages-data/geo-intel.json`` relative to the
    GEO-INFER checkout that contains this module.
    """
    override = os.environ.get(ENV_CONTRACT_PATH)
    if override:
        return Path(override)
    # GEO-INFER-ACT/src/geo_infer_act/core/civic_intel.py
    # -> parents[4] is the GEO-INFER repository root, whose sibling is
    #    crescent-city-intel.
    geo_infer_root = Path(__file__).resolve().parents[4]
    return geo_infer_root.parent / _DEFAULT_CONTRACT_RELATIVE


def _decode_contract_json(text: str, source_label: str) -> Dict[str, Any]:
    """Decode one JSON object or raise a contract-facing ``ValueError``."""
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid Crescent City intel JSON from {source_label}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"Crescent City intel JSON from {source_label} must be an object")
    return loaded


def _coerce_contract(source: Any) -> Optional[Dict[str, Any]]:
    """Load a raw contract from a dict, a path, or a JSON string.

    Returns ``None`` when a requested path is absent. Existing but unreadable
    paths and malformed JSON fail closed with ``ValueError``.
    """
    if isinstance(source, dict):
        return source

    if isinstance(source, str):
        stripped = source.lstrip()
        if stripped.startswith(("{", "[")):
            return _decode_contract_json(source, "injected string")
        path = Path(source)
    elif isinstance(source, os.PathLike):
        path = Path(source)
    else:
        return None

    try:
        if not path.exists():
            return None
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"unable to read Crescent City intel JSON at {path}: {exc}") from exc
    return _decode_contract_json(text, str(path))


def _require_dict(value: Any, field_name: str) -> Dict[str, Any]:
    """Return a dict-shaped contract field or fail closed."""
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    return value


def _require_list(value: Any, field_name: str) -> List[Any]:
    """Return a list-shaped contract field or fail closed."""
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be an array")
    return value


def _require_finite_float(value: Any, field_name: str) -> float:
    """Return a finite numeric contract field or fail closed."""
    if isinstance(value, bool) or not isinstance(
        value, (int, float, np.integer, np.floating)
    ):
        raise ValueError(f"{field_name} must be a finite number")
    number = float(value)
    if not np.isfinite(number):
        raise ValueError(f"{field_name} must be a finite number")
    return number


def _base_hazard_tag(tag: str) -> Optional[str]:
    """Resolve a producer tag to a configured base hazard by whole terms."""
    normalized = " ".join(tag.casefold().split())
    for base_tag, pattern in _HAZARD_TERM_PATTERNS.items():
        if pattern.search(normalized):
            return base_tag
    return None


def _read_topic(raw: Dict[str, Any], field_name: str = "hazard topic") -> GeoIntelTopic:
    raw_tags = _require_list(raw.get("tags", []), f"{field_name}.tags")
    raw_sections = _require_list(raw.get("sections", []), f"{field_name}.sections")
    sections: List[GeoIntelSection] = []
    for index, section_value in enumerate(raw_sections):
        section = _require_dict(section_value, f"{field_name}.sections[{index}]")
        sections.append(
            GeoIntelSection(
                sectionNumber=str(section.get("sectionNumber", "")),
                relevance=str(section.get("relevance", "")),
            )
        )
    return GeoIntelTopic(
        name=str(raw.get("name", "")),
        tags=[str(tag) for tag in raw_tags],
        sections=sections,
    )


def _read_hazard_domain(
    raw: Dict[str, Any],
    field_name: str = "hazard domain",
    *,
    fallback_to_domain_tags: bool = False,
) -> HazardDomain:
    if "hazardTags" in raw:
        raw_hazard_tags = _require_list(raw["hazardTags"], f"{field_name}.hazardTags")
    elif fallback_to_domain_tags:
        domain_tags = _require_list(raw.get("tags", []), f"{field_name}.tags")
        raw_hazard_tags = [tag for tag in domain_tags if _base_hazard_tag(str(tag))]
    else:
        raw_hazard_tags = []

    raw_topics = _require_list(raw.get("topics", []), f"{field_name}.topics")
    topics: List[GeoIntelTopic] = []
    for index, topic_value in enumerate(raw_topics):
        topic = _require_dict(topic_value, f"{field_name}.topics[{index}]")
        topics.append(_read_topic(topic, f"{field_name}.topics[{index}]"))

    return HazardDomain(
        id=str(raw.get("id", "")),
        name=str(raw.get("name", "")),
        icon=str(raw.get("icon", "")),
        hazardTags=[str(tag) for tag in raw_hazard_tags],
        topics=topics,
    )


def _has_hazard_signal(raw: Dict[str, Any]) -> bool:
    """True when a raw domain references any recognised hazard tag."""
    raw_tags = _require_list(raw.get("tags", []), "domain.tags")
    tag_sources: List[str] = [str(item) for item in raw_tags]
    tag_sources.extend(_read_hazard_domain(raw).hazardTags)
    return any(_base_hazard_tag(tag) is not None for tag in tag_sources)


def _extract_hazard_domains(contract: Dict[str, Any]) -> List[HazardDomain]:
    """Return hazard-relevant domains from the contract.

    Prefers the explicit ``hazard.relevantDomains`` subset; when the contract
    omits it, falls back to a deterministic tag-driven scan of the full domain
    list. Duplicate domain ids are collapsed keeping the first occurrence so the
    result is stable regardless of source shape.
    """
    hazard_value = contract.get("hazard", {})
    hazard = _require_dict(hazard_value, "hazard")
    explicit = _require_list(
        hazard.get("relevantDomains", []), "hazard.relevantDomains"
    )
    if explicit:
        domains = [
            _read_hazard_domain(
                _require_dict(item, f"hazard.relevantDomains[{index}]"),
                f"hazard.relevantDomains[{index}]",
            )
            for index, item in enumerate(explicit)
        ]
        return _dedupe_domains([domain for domain in domains if domain.id])

    full_domain_values = _require_list(contract.get("domains", []), "domains")
    full_domains = [
        _require_dict(item, f"domains[{index}]")
        for index, item in enumerate(full_domain_values)
    ]
    domains = [
        _read_hazard_domain(
            item,
            f"domains[{index}]",
            fallback_to_domain_tags=True,
        )
        for index, item in enumerate(full_domains)
        if _has_hazard_signal(item)
    ]
    return _dedupe_domains([domain for domain in domains if domain.id])


def _read_bounds(anchor: Dict[str, Any]) -> Optional[CivicIntelBounds]:
    """Parse and validate optional WGS84 municipal bounds."""
    if "bounds" not in anchor:
        return None
    raw = _require_dict(anchor["bounds"], "anchor.bounds")
    bounds = CivicIntelBounds(
        west=_require_finite_float(raw.get("west"), "anchor.bounds.west"),
        south=_require_finite_float(raw.get("south"), "anchor.bounds.south"),
        east=_require_finite_float(raw.get("east"), "anchor.bounds.east"),
        north=_require_finite_float(raw.get("north"), "anchor.bounds.north"),
    )
    if not -180.0 <= bounds.west < bounds.east <= 180.0:
        raise ValueError("anchor.bounds must satisfy -180 <= west < east <= 180")
    if not -90.0 <= bounds.south < bounds.north <= 90.0:
        raise ValueError("anchor.bounds must satisfy -90 <= south < north <= 90")
    return bounds


def _dedupe_domains(domains: Sequence[HazardDomain]) -> List[HazardDomain]:
    seen: Dict[str, HazardDomain] = {}
    for domain in domains:
        if domain.id not in seen:
            seen[domain.id] = domain
    return list(seen.values())


def parse_crescent_city_intel(
    seed: Optional[int] = None,
    source: Union[None, str, Path, Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Parse the ``crescent-city-geo-intel/v1`` contract into a helper record.

    Args:
        seed: RNG seed conforming to the GEO-INFER-ACT RNG contract. Parsing
            itself is deterministic; the seed is accepted for signature symmetry
            with the policy-prior builder and reserved for future stochastic
            defaults, so callers can rely on identical output for identical
            input regardless of the seed value.
        source: The contract as a dict, a path to a JSON file, or a JSON string.
            Defaults to the sibling ``crescent-city-intel/pages-data/geo-intel.json``.

    Returns:
        A dict with ``schema``, ``city``, ``anchor``, ``generatedAt``,
        ``bounds`` and ``hazardDomains`` keys. When the contract path is absent,
        returns a graceful empty record (empty city, empty hazard subset, empty
        bounds). Malformed JSON or v1 structures fail closed with ``ValueError``.
    """
    contract = _coerce_contract(source) if source is not None else _coerce_contract(
        default_contract_path()
    )

    if not contract or contract.get("schema") != SUPPORTED_SCHEMA:
        return {
            "schema": None,
            "city": "",
            "anchor": {},
            "generatedAt": None,
            "bounds": {},
            "hazardDomains": [],
        }

    anchor = _require_dict(contract.get("anchor", {}), "anchor")
    bounds = _read_bounds(anchor)

    record = CrescentCityIntel(
        city=str(anchor.get("name", contract.get("anchor_name", ""))),
        hazardDomains=_extract_hazard_domains(contract),
        bounds=bounds,
        schema=str(contract.get("schema")),
        anchor=dict(anchor),
        generatedAt=(
            str(contract.get("generatedAt")) if contract.get("generatedAt") is not None else None
        ),
    )
    return record.as_dict()


def _distinct_hazard_tags(parsed: Dict[str, Any]) -> List[str]:
    """Collect ordered, de-duplicated hazard tags across the hazard subset."""
    tags: Dict[str, None] = {}
    for domain in parsed.get("hazardDomains", []):
        if not isinstance(domain, dict):
            continue
        for tag in domain.get("hazardTags", []):
            normalized = " ".join(str(tag).casefold().split())
            if normalized:
                tags[normalized] = None
        for topic in domain.get("topics", []):
            if isinstance(topic, dict):
                for tag in topic.get("tags", []):
                    normalized = " ".join(str(tag).casefold().split())
                    if normalized:
                        tags[normalized] = None
    return sorted(tags.keys())


def _validated_hedge_share(value: float) -> float:
    """Validate the optional stochastic hedge fraction."""
    if isinstance(value, bool) or not isinstance(
        value, (int, float, np.integer, np.floating)
    ):
        raise ValueError("hedge_share must be a finite number in [0, 1]")
    share = float(value)
    if not np.isfinite(share) or not 0.0 <= share <= 1.0:
        raise ValueError("hedge_share must be a finite number in [0, 1]")
    return share


def hazard_policy_prior(
    contract: Dict[str, Any],
    seed: Optional[int] = None,
    hedge_share: float = 0.0,
) -> Dict[str, Any]:
    """Build preference weights from municipal hazard intent for a PolicySelector.

    The returned ``preferences`` vector aligns with a state axis whose first
    entry is the baseline all-clear state (most preferred) and whose remaining
    entries correspond to the discovered hazard tags in sorted order. A policy
    that predicts a hazard state therefore carries a lower preference and a
    higher expected free energy, so a ``PolicySelector`` in ``deterministic``
    mode selects the policy that best avoids Crescent City's notified hazards.

    Randomness follows the GEO-INFER-ACT RNG contract: an explicit
    ``np.random.default_rng(seed)`` instance is always created, and it is only
    consulted when ``hedge_share`` is positive. With the default ``hedge_share=0``
    the result is fully deterministic regardless of ``seed``.

    Args:
        contract: A parsed record from ``parse_crescent_city_intel`` or a raw
            contract dict (parsed on the fly).
        seed: RNG seed for the optional hedged prior.
        hedge_share: Fraction in ``[0, 1]`` of spread to add as seeded hedge
            noise to the raw weights. ``0.0`` keeps the prior deterministic.

    Returns:
        A dict with ``preferences`` (normalised), ``weights`` (tag -> avoidance),
        ``preference_weights`` (tag -> preference), ``hazardTags``,
        ``hazardDomainIds``, ``dominantHazard``, ``deterministic`` and ``seed``.
    """
    validated_hedge_share = _validated_hedge_share(hedge_share)

    # Accept either a parsed record or a raw contract dict.
    parsed = (
        contract
        if "hazardDomains" in contract
        else parse_crescent_city_intel(source=contract)
    )

    hazard_domain_ids = [
        str(domain.get("id"))
        for domain in parsed.get("hazardDomains", [])
        if isinstance(domain, dict) and domain.get("id")
    ]
    tags = _distinct_hazard_tags(parsed)

    # Baseline (all-clear) preference plus one entry per discovered hazard tag.
    weights: List[float] = [_BASELINE_PREFERENCE]
    tag_preferences: Dict[str, float] = {}
    tag_avoidance: Dict[str, float] = {}
    for tag in tags:
        base_tag = _base_hazard_tag(tag)
        avoidance = float(
            HAZARD_AVOIDANCE.get(base_tag, _DEFAULT_AVOIDANCE)
            if base_tag is not None
            else _DEFAULT_AVOIDANCE
        )
        tag_avoidance[tag] = avoidance
        preference = max(_BASELINE_PREFERENCE - avoidance, _MIN_PREFERENCE)
        tag_preferences[tag] = preference
        weights.append(preference)

    rng = np.random.default_rng(seed)
    if validated_hedge_share > 0:
        finite = np.asarray(weights, dtype=float)
        spread = 0.05 * validated_hedge_share
        jitter = rng.uniform(-spread, spread, size=finite.shape)
        weights = np.maximum(finite + jitter, _MIN_PREFERENCE).tolist()

    preference_vector = np.asarray(weights, dtype=float)
    total = float(np.sum(preference_vector))
    normalized = preference_vector / total if total > 0 else np.ones_like(preference_vector)

    dominant = None
    if tags:
        dominant = max(tags, key=lambda tag: tag_avoidance[tag])

    return {
        "preferences": normalized,
        "weights": tag_avoidance,
        "preference_weights": tag_preferences,
        "hazardTags": tags,
        "hazardDomainIds": hazard_domain_ids,
        "dominantHazard": dominant,
        "deterministic": validated_hedge_share == 0,
        "seed": seed,
    }
