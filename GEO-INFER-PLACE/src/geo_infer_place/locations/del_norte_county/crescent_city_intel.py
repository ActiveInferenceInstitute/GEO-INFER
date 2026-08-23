"""
CrescentCityIntelMapper: map the Crescent City civic-intel contract onto Del Norte H3.

Imports the machine-readable crescent-city-intel geospatial contract
(``pages-data/geo-intel.json`` — schema ``crescent-city-geo-intel/v1``) produced
by the ``docxology/crescent-city-intel`` platform, and maps its 12 civic
intelligence domains + hazard-relevant subset onto the Del Norte County H3 grid
so the comprehensive dashboard can weight municipal-code policy by hazard intent
(tunami, seismic, flood, erosion) across the same spatial canvas as the forest /
coastal / fire / seismic analyzers.

Data source:
    The contract is read from ``CRESCENT_INTEL_GEO_JSON`` (env override) or a
    packaged seed ``data/crescent-city-geo-intel.json`` bundled beside this
    module. The packaged seed is a reviewed copy of the platform's committed
    ``pages-data/geo-intel.json``; it keeps this mapper dependency-free (no live
    output/ or sibling-repo path needed) and gracefully reports when absent.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

import h3

logger = logging.getLogger(__name__)

# Default packaged seed path bundled with the module.
_SEED_REL = Path(__file__).resolve().parent / "data" / "crescent-city-geo-intel.json"


@dataclass
class CrescentCityIntelMapper:
    """Load the crescent-intel civic contract and project it onto H3 cells.

    Domain knowledge: the contract is a flat ``crescent-city-geo-intel/v1``
    document whose ``domains`` entries each carry ``id``, ``name``, ``icon``,
    ``topicCount``, ``tags``, and municipal-code ``sections``; the ``hazard``
    block carries the hazard-relevant subset of those domains. The mapper
    anchors to the contract's Del Norte bounds and flags every county H3 cell
    with the union of hazard tags present in the civic policy surface.
    """

    seed_path: Optional[Path] = None
    h3_resolution: int = 8

    # ─── Public state ────────────────────────────────────────────────
    contract: Dict[str, Any] = field(default_factory=dict)
    loaded: bool = False
    source_path: Optional[Path] = None
    error: Optional[str] = None

    def __post_init__(self) -> None:
        """Resolve the seed path (env override → passed → packaged) and load."""
        self._load_contract()

    # ── Loading ──────────────────────────────────────────────────────

    def _default_seed_path(self) -> Path:
        env_override = os.environ.get("CRESCENT_INTEL_GEO_JSON")
        if env_override and Path(env_override).exists():
            return Path(env_override)
        return _SEED_REL

    def _load_contract(self) -> None:
        """Load the contract JSON with graceful absence reporting."""
        path = self.seed_path or self._default_seed_path()
        if not path.exists():
            self.loaded = False
            self.error = f"Crescent City intel contract not found at {path}"
            logger.warning(self.error)
            return
        try:
            with open(path, "r", encoding="utf-8") as fh:
                self.contract = cast(Dict[str, Any], json.load(fh))
            if self.contract.get("schema") != "crescent-city-geo-intel/v1":
                raise ValueError(
                    f"Unexpected intel schema {self.contract.get('schema')!r}"
                )
            self.loaded = True
            self.source_path = path
            logger.info(
                "Crescent City intel contract loaded: %s domains (schema v1)",
                self.contract.get("domainCount"),
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            self.loaded = False
            self.contract = {}
            self.error = f"Failed to load Crescent City intel contract: {exc}"
            logger.warning(self.error)

    # ── Mapper surface ───────────────────────────────────────────────

    def domains(self) -> List[Dict[str, Any]]:
        """Return the civic-intel domains (empty list when not loaded)."""
        if not self.loaded:
            return []
        return self.contract.get("domains", []) or []

    def hazard_domains(self) -> List[Dict[str, Any]]:
        """Return the hazard-relevant domain subset."""
        if not self.loaded:
            return []
        return self.contract.get("hazard", {}).get("relevantDomains", []) or []

    def domain_ids(self) -> List[str]:
        """Return sorted civic-domain slugs (useful for gap reporting)."""
        return sorted(d.get("id", "") for d in self.domains() if d.get("id"))

    def bounds(self) -> Dict[str, float]:
        """Return Del Norte bounds from the contract's municipality anchor."""
        anchor = self.contract.get("anchor", {}) if self.loaded else {}
        bounds = anchor.get("bounds", {})
        return {
            "west": float(bounds.get("west", -124.408)),
            "south": float(bounds.get("south", 41.458)),
            "east": float(bounds.get("east", -123.536)),
            "north": float(bounds.get("north", 42.006)),
        }

    def _county_geojson(self) -> Dict[str, Any]:
        """Return a GeoJSON Polygon (lng,lat ring) covering the Del Norte bounds."""
        b = self.bounds()
        ring = [
            [b["west"], b["south"]],
            [b["east"], b["south"]],
            [b["east"], b["north"]],
            [b["west"], b["north"]],
            [b["west"], b["south"]],  # close the ring
        ]
        return {"type": "Polygon", "coordinates": [ring]}

    def generate_h3_cells(self) -> Dict[str, Dict[str, Any]]:
        """Generate an H3-indexed civic-intel surface covering the county.

        Returns:
            Mapping of ``h3_cell -> {hazard_tags, domain_count, civic_domains}``
            for every grid cell intersecting the Del Norte bounds polygon. Empty
            when the contract is not loaded (the caller reports the gap).
        """
        if not self.loaded:
            return {}
        try:
            cells = set(h3.geo_to_cells(self._county_geojson(), self.h3_resolution))
        except TypeError:
            # Older h3 (<4.5) used the vertex-list form; fall back gracefully.
            cells = set()
            b = self.bounds()
            for lat, lng in [
                (b["south"], b["west"]),
                (b["south"], b["east"]),
                (b["north"], b["east"]),
                (b["north"], b["west"]),
            ]:
                cells.add(h3.latlng_to_cell(lat, lng, self.h3_resolution))

        domain_ids = self.domain_ids()
        hazard_tags = self._all_hazard_tags()
        out: Dict[str, Dict[str, Any]] = {}
        for cell_id in cells:
            out[cell_id] = {
                "hazard_tags": sorted(hazard_tags),
                "domain_count": len(domain_ids),
                "intel_present": True,
                "civic_domains": list(domain_ids)[:25],
            }
        return out

    def generate_hazard_surface(self) -> Dict[str, Any]:
        """Build a compact hazard-intent summary (domain-aware, not a full grid)."""
        hazards = self.hazard_domains()
        if not hazards:
            return {"status": "no_hazard_domains", "domains": []}
        return {
            "status": "ok",
            "domains": [
                {
                    "id": d.get("id"),
                    "name": d.get("name"),
                    "icon": d.get("icon"),
                    "hazardTags": d.get("hazardTags", []),
                    "topics": [
                        {
                            "name": t.get("name"),
                            "sections": t.get("sections", []),
                        }
                        for t in d.get("topics", [])
                    ],
                }
                for d in hazards
            ],
        }

    def _all_hazard_tags(self) -> set:
        """Collect the union of hazard tags across all hazard-relevant domains."""
        tags: set[str] = set()
        for dom in self.hazard_domains():
            for tag in dom.get("hazardTags", []):
                tags.add(str(tag))
        return tags