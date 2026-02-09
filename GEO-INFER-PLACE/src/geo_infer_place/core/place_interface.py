"""
PlaceInterface: unified entry point for Del Norte and Cascadia analyses.

Provides a single class that orchestrates all location-specific analyzers,
data acquisition, temporal analysis, and data quality management through
one coherent API.

Usage::

    from geo_infer_place import PlaceInterface

    pi = PlaceInterface("del_norte")
    results = pi.run_full_analysis()

    pi_cascadia = PlaceInterface("cascadia", counties=["CA:Del Norte", "OR:Josephine"])
    results = pi_cascadia.run_full_analysis()
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Location presets
LOCATION_PRESETS = {
    "del_norte": {
        "name": "Del Norte County, California",
        "bounds": {"west": -124.408, "south": 41.458, "east": -123.536, "north": 42.006},
        "h3_resolution": 8,
        "analyzers": ["forest_health", "coastal_resilience", "fire_risk", "seismic_hazard"],
        "data_sources": ["calfire", "noaa", "usgs"],
    },
    "cascadia": {
        "name": "Cascadia Bioregion (CA + OR)",
        "bounds": {"west": -124.6, "south": 40.0, "east": -121.0, "north": 46.3},
        "h3_resolution": 8,
        "analyzers": ["seismic_hazard", "cascadia_agricultural"],
        "data_sources": ["usgs", "noaa", "calfire", "usda"],
    },
}


class PlaceInterface:
    """Unified interface for place-based analysis.

    Brings together:
    - Location-specific analyzers (forest, coastal, fire, seismic)
    - Data integration (CAL FIRE, NOAA, USGS)
    - Temporal analysis (trend detection, anomaly flagging)
    - Data quality management and provenance tracking
    - Cascadia agricultural H3 backend (when location is ``cascadia``)

    Args:
        location: Location key (``"del_norte"`` or ``"cascadia"``).
        config: Optional override config dict.
        output_dir: Where to write analysis outputs.
        counties: For Cascadia: list of ``"STATE:County"`` strings.
    """

    def __init__(
        self,
        location: str = "del_norte",
        config: Optional[Dict[str, Any]] = None,
        output_dir: Optional[str] = None,
        counties: Optional[List[str]] = None,
    ) -> None:
        if location not in LOCATION_PRESETS:
            raise ValueError(
                f"Unknown location '{location}'. Supported: {list(LOCATION_PRESETS.keys())}"
            )

        self.location = location
        preset = LOCATION_PRESETS[location]
        self.location_name = preset["name"]

        # Build config
        self.config = config or {
            "location": {"bounds": preset["bounds"]},
            "spatial": {"h3_resolution": preset["h3_resolution"]},
            "analyses": {a: {} for a in preset["analyzers"]},
        }

        # Output directory
        default_out = Path(__file__).resolve().parents[3] / "locations" / location.replace(" ", "_") / "output"
        self.output_dir = Path(output_dir) if output_dir else default_out
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Counties for Cascadia
        self.counties = counties

        # Lazy-initialised components
        self._integrator = None
        self._data_manager = None
        self._temporal = None
        self._analyzers: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Component accessors (lazy init)
    # ------------------------------------------------------------------

    @property
    def integrator(self):
        """Data integrator with CAL FIRE, NOAA, USGS wrappers."""
        if self._integrator is None:
            from ..utils.integration import DelNorteDataIntegrator
            self._integrator = DelNorteDataIntegrator()
        return self._integrator

    @property
    def data_manager(self):
        """Data quality and provenance manager (bridges GEO-INFER-DATA)."""
        if self._data_manager is None:
            from .module_bridge import PlaceDataManager
            self._data_manager = PlaceDataManager()
        return self._data_manager

    @property
    def temporal(self):
        """Temporal analyzer (bridges GEO-INFER-TIME)."""
        if self._temporal is None:
            from .module_bridge import PlaceTemporalAnalyzer
            self._temporal = PlaceTemporalAnalyzer()
        return self._temporal

    # ------------------------------------------------------------------
    # Analyzer access
    # ------------------------------------------------------------------

    def get_analyzer(self, name: str) -> Any:
        """Get or create a named analyzer.

        Supported analyzers:
        - ``forest_health``: ForestHealthMonitor
        - ``coastal_resilience``: CoastalResilienceAnalyzer
        - ``fire_risk``: FireRiskAssessor
        - ``seismic_hazard``: SeismicHazardAnalyzer
        """
        if name not in self._analyzers:
            self._analyzers[name] = self._create_analyzer(name)
        return self._analyzers[name]

    def _create_analyzer(self, name: str) -> Any:
        if name == "forest_health":
            from ..locations.del_norte_county.forest_health_monitor import ForestHealthMonitor
            return ForestHealthMonitor(
                config=self.config,
                data_integrator=self.integrator,
                spatial_processor=None,
                output_dir=self.output_dir,
            )
        elif name == "coastal_resilience":
            from ..locations.del_norte_county.coastal_resilience_analyzer import CoastalResilienceAnalyzer
            return CoastalResilienceAnalyzer(
                config=self.config,
                data_integrator=self.integrator,
                spatial_processor=None,
                output_dir=self.output_dir,
            )
        elif name == "fire_risk":
            from ..locations.del_norte_county.fire_risk_assessor import FireRiskAssessor
            return FireRiskAssessor(
                config=self.config,
                data_integrator=self.integrator,
                spatial_processor=None,
                output_dir=self.output_dir,
            )
        elif name == "seismic_hazard":
            from ..locations.del_norte_county.seismic_hazard_analyzer import SeismicHazardAnalyzer
            return SeismicHazardAnalyzer(
                config=self.config,
                data_integrator=self.integrator,
                spatial_processor=None,
                output_dir=self.output_dir,
            )
        else:
            raise ValueError(f"Unknown analyzer: {name}")

    # ------------------------------------------------------------------
    # Full analysis pipeline
    # ------------------------------------------------------------------

    def run_full_analysis(
        self,
        analyzers: Optional[List[str]] = None,
        include_temporal: bool = True,
    ) -> Dict[str, Any]:
        """Run all configured analyzers and return unified results.

        Args:
            analyzers: List of analyzer names to run. Defaults to all for the location.
            include_temporal: If True, run temporal analysis on applicable data.

        Returns:
            Unified results dict with analysis outputs, temporal trends,
            data quality reports, and provenance log.
        """
        preset = LOCATION_PRESETS[self.location]
        analyzer_names = analyzers or preset["analyzers"]

        logger.info("Starting full analysis for %s with analyzers: %s", self.location_name, analyzer_names)

        results: Dict[str, Any] = {
            "location": self.location_name,
            "timestamp": datetime.now().isoformat(),
            "config": {
                "bounds": preset["bounds"],
                "h3_resolution": preset["h3_resolution"],
                "analyzers_requested": analyzer_names,
            },
            "analyses": {},
            "temporal_analysis": {},
            "data_quality": {},
            "provenance": [],
        }

        # Run each analyzer
        for name in analyzer_names:
            if name == "cascadia_agricultural":
                # Skip - requires separate Cascadia pipeline invocation
                logger.info("Skipping cascadia_agricultural (use cascadia_main.py)")
                continue

            logger.info("Running analyzer: %s", name)
            try:
                analyzer = self.get_analyzer(name)
                analysis_result = analyzer.run_analysis()
                results["analyses"][name] = analysis_result

                # Validate output quality
                quality = self.data_manager.validate_dataset(analysis_result, name=name)
                results["data_quality"][name] = quality

                # Log provenance
                self.data_manager.log_provenance(name, {
                    "analyzer": name,
                    "location": self.location,
                    "data_quality": quality.get("completeness", 0),
                })

            except Exception as exc:
                logger.error("Analyzer %s failed: %s", name, exc, exc_info=True)
                results["analyses"][name] = {"error": str(exc), "success": False}

        # Temporal analysis on applicable data
        if include_temporal:
            results["temporal_analysis"] = self._run_temporal_analysis(results["analyses"])

        # Attach provenance
        results["provenance"] = self.data_manager.get_provenance()

        # Save results
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = self.output_dir / f"{self.location}_full_analysis_{ts}.json"
        out_path.write_text(json.dumps(results, indent=2, default=str))
        logger.info("Full analysis saved to %s", out_path)

        return results

    # ------------------------------------------------------------------
    # Temporal analysis integration
    # ------------------------------------------------------------------

    def _run_temporal_analysis(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Run temporal analysis on applicable datasets."""
        temporal_results = {}

        # Tide data trends (from coastal_resilience or direct fetch)
        try:
            tide_data = self.integrator.noaa_client.get_tide_gauge_data()
            if tide_data.get("series"):
                temporal_results["tide_trends"] = self.temporal.analyze_tide_trends(tide_data)
                self.data_manager.log_provenance("temporal_tide_analysis", {
                    "method": "trend_and_anomaly_detection",
                })
        except Exception as exc:
            logger.debug("Tide temporal analysis skipped: %s", exc)

        # Seismic rate analysis (from seismic_hazard)
        seismic = analyses.get("seismic_hazard", {})
        csz_data = seismic.get("cascadia_seismicity", {})
        if csz_data.get("events"):
            try:
                temporal_results["seismic_rates"] = self.temporal.analyze_seismic_rates(csz_data)
                self.data_manager.log_provenance("temporal_seismic_analysis", {
                    "method": "daily_rate_trend",
                })
            except Exception as exc:
                logger.debug("Seismic temporal analysis skipped: %s", exc)

        return temporal_results

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    def get_earthquakes(self, bbox: Optional[tuple] = None) -> Dict[str, Any]:
        """Fetch recent earthquakes for the location."""
        return self.integrator.usgs_client.get_earthquakes(bbox=bbox)

    def get_cascadia_seismicity(self, days: int = 30) -> Dict[str, Any]:
        """Fetch Cascadia-wide seismicity data."""
        return self.integrator.usgs_client.get_cascadia_seismicity(days=days)

    def get_tide_data(
        self,
        stations: Optional[List[str]] = None,
        time_range: Optional[tuple] = None,
    ) -> Dict[str, Any]:
        """Fetch tide gauge data."""
        return self.integrator.noaa_client.get_tide_gauge_data(
            stations=stations, time_range=time_range
        )

    def get_fire_perimeters(
        self,
        bbox: Optional[tuple] = None,
        start_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Fetch fire perimeter data."""
        return self.integrator.calfire_client.get_fire_perimeters(
            bbox=bbox, start_year=start_year
        )

    def get_weather(self, station_id: str = "KCEC") -> Dict[str, Any]:
        """Fetch current weather observations."""
        return self.integrator.noaa_client.get_weather_data(station_id=station_id)

    def status(self) -> Dict[str, Any]:
        """Return status of all components."""
        return {
            "location": self.location,
            "location_name": self.location_name,
            "output_dir": str(self.output_dir),
            "data_module_available": self.data_manager.has_data_module,
            "time_module_available": self.temporal.has_time_module,
            "available_analyzers": LOCATION_PRESETS[self.location]["analyzers"],
            "initialized_analyzers": list(self._analyzers.keys()),
            "cache_stats": {
                "calfire": self.integrator.calfire_client.cache_stats(),
                "noaa": self.integrator.noaa_client.cache_stats(),
                "usgs": self.integrator.usgs_client.cache_stats(),
            },
        }
