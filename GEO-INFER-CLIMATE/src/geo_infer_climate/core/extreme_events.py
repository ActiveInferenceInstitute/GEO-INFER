"""
Extreme weather event analysis module.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
import xarray as xr

logger = logging.getLogger(__name__)


class ExtremeEventType(Enum):
    """Types of extreme events."""

    HEATWAVE = "heatwave"
    COLDSPELL = "coldspell"
    DROUGHT = "drought"
    FLOOD = "flood"
    STORM = "storm"
    EXTREME_PRECIPITATION = "extreme_precipitation"
    COMPOUND = "compound"


class Severity(Enum):
    """Event severity levels."""

    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"
    CATASTROPHIC = "catastrophic"


@dataclass
class ExtremeEvent:
    """Extreme weather event."""

    event_id: str
    event_type: ExtremeEventType
    start_date: str
    end_date: str
    duration_days: int
    peak_value: float
    severity: Severity
    location: Optional[Tuple[float, float]] = None
    area_km2: Optional[float] = None
    return_period_years: Optional[float] = None


class ExtremeEventAnalyzer:
    """
    Comprehensive extreme weather event analyzer.

    Provides analysis of:
    - Heatwaves and cold spells
    - Droughts and floods
    - Extreme precipitation
    - Compound events
    - Return period calculation
    - Climate indices
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize extreme event analyzer.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

        # Event thresholds
        self.thresholds = {
            "heatwave_percentile": 90.0,
            "coldspell_percentile": 10.0,
            "drought_percentile": 10.0,
            "flood_percentile": 95.0,
            "extreme_precip_percentile": 99.0,
        }

        # Event registry
        self.event_registry: List[ExtremeEvent] = []

    def detect_heatwaves(
        self,
        temperature: xr.DataArray,
        threshold_percentile: float = 90.0,
        min_duration: int = 3,
    ) -> Dict[str, Any]:
        """
        Detect heatwave events.

        Args:
            temperature: Temperature data
            threshold_percentile: Percentile threshold for heatwave
            min_duration: Minimum duration in days

        Returns:
            Dictionary with heatwave detection results.
        """
        threshold = float(temperature.quantile(threshold_percentile / 100.0))
        values = temperature.values.flatten()
        above_threshold = values >= threshold
        if np.nanmax(values) == np.nanmin(values):
            above_threshold = np.zeros_like(values, dtype=bool)

        events = []
        in_event = False
        event_start = 0

        for i, is_hot in enumerate(above_threshold):
            if is_hot and not in_event:
                in_event = True
                event_start = i
            elif not is_hot and in_event:
                duration = i - event_start
                if duration >= min_duration:
                    events.append(
                        {
                            "start_index": event_start,
                            "end_index": i - 1,
                            "duration_days": duration,
                            "max_temp": float(max(values[event_start:i])),
                            "mean_temp": float(np.mean(values[event_start:i])),
                        }
                    )
                in_event = False

        if in_event and len(values) - event_start >= min_duration:
            events.append(
                {
                    "start_index": event_start,
                    "end_index": len(values) - 1,
                    "duration_days": len(values) - event_start,
                    "max_temp": float(max(values[event_start:])),
                    "mean_temp": float(np.mean(values[event_start:])),
                }
            )

        return {
            "threshold_temp": threshold,
            "threshold_percentile": threshold_percentile,
            "min_duration": min_duration,
            "events_detected": len(events),
            "events": events,
            "total_hot_days": int(np.sum(above_threshold)),
        }

    def detect_droughts(
        self,
        precipitation: xr.DataArray,
        threshold_percentile: float = 10.0,
        min_duration: int = 30,
    ) -> xr.Dataset:
        """
        Detect drought events.

        Args:
            precipitation: Precipitation data
            threshold_percentile: Percentile threshold for drought
            min_duration: Minimum duration in days

        Returns:
            Dataset with drought events
        """
        threshold = precipitation.quantile(threshold_percentile / 100.0, dim="time")

        # Identify days below threshold
        below_threshold = precipitation < threshold

        # Find consecutive periods
        droughts = self._find_consecutive_periods(below_threshold, min_duration)

        return droughts

    def detect_cold_spells(
        self,
        temperature: xr.DataArray,
        threshold_percentile: float = 10.0,
        min_duration: int = 3,
    ) -> Dict[str, Any]:
        """
        Detect cold spell events.

        Args:
            temperature: Temperature data
            threshold_percentile: Percentile for cold threshold
            min_duration: Minimum consecutive days

        Returns:
            Cold spell detection results
        """
        threshold = float(temperature.quantile(threshold_percentile / 100.0))

        values = temperature.values.flatten()

        # Find cold periods
        below_threshold = values <= threshold
        if np.nanmax(values) == np.nanmin(values):
            below_threshold = np.zeros_like(values, dtype=bool)

        events = []
        in_event = False
        event_start = 0

        for i, is_cold in enumerate(below_threshold):
            if is_cold and not in_event:
                in_event = True
                event_start = i
            elif not is_cold and in_event:
                duration = i - event_start
                if duration >= min_duration:
                    events.append(
                        {
                            "start_index": event_start,
                            "end_index": i - 1,
                            "duration_days": duration,
                            "min_temp": float(min(values[event_start:i])),
                            "mean_temp": float(np.mean(values[event_start:i])),
                        }
                    )
                in_event = False

        # Handle event ongoing at end
        if in_event and len(values) - event_start >= min_duration:
            events.append(
                {
                    "start_index": event_start,
                    "end_index": len(values) - 1,
                    "duration_days": len(values) - event_start,
                    "min_temp": float(min(values[event_start:])),
                    "mean_temp": float(np.mean(values[event_start:])),
                }
            )

        return {
            "threshold_temp": threshold,
            "threshold_percentile": threshold_percentile,
            "min_duration": min_duration,
            "events_detected": len(events),
            "events": events,
            "total_cold_days": int(np.sum(below_threshold)),
        }

    def detect_floods(
        self,
        streamflow: xr.DataArray,
        threshold_percentile: float = 95.0,
        min_duration: int = 1,
    ) -> Dict[str, Any]:
        """
        Detect flood events from streamflow data.

        Args:
            streamflow: Streamflow/discharge data
            threshold_percentile: High flow percentile
            min_duration: Minimum event duration

        Returns:
            Flood detection results
        """
        threshold = float(streamflow.quantile(threshold_percentile / 100.0))

        values = streamflow.values.flatten()
        above_threshold = values >= threshold
        if np.nanmax(values) == np.nanmin(values):
            above_threshold = np.zeros_like(values, dtype=bool)

        events = []
        in_event = False
        event_start = 0

        for i, is_flood in enumerate(above_threshold):
            if is_flood and not in_event:
                in_event = True
                event_start = i
            elif not is_flood and in_event:
                duration = i - event_start
                if duration >= min_duration:
                    peak = float(max(values[event_start:i]))
                    events.append(
                        {
                            "start_index": event_start,
                            "end_index": i - 1,
                            "duration_days": duration,
                            "peak_flow": peak,
                            "mean_flow": float(np.mean(values[event_start:i])),
                            "exceedance_factor": peak / threshold,
                        }
                    )
                in_event = False

        if in_event and len(values) - event_start >= min_duration:
            peak = float(max(values[event_start:]))
            events.append(
                {
                    "start_index": event_start,
                    "end_index": len(values) - 1,
                    "duration_days": len(values) - event_start,
                    "peak_flow": peak,
                    "mean_flow": float(np.mean(values[event_start:])),
                    "exceedance_factor": (
                        peak / threshold if threshold else float("inf")
                    ),
                }
            )

        return {
            "threshold_flow": threshold,
            "threshold_percentile": threshold_percentile,
            "events_detected": len(events),
            "events": events,
            "max_peak": max([e["peak_flow"] for e in events]) if events else None,
        }

    def calculate_return_period(
        self, data: xr.DataArray, value: float, method: str = "gev"
    ) -> Dict[str, Any]:
        """
        Calculate return period for an extreme value.

        Args:
            data: Historical data for fitting
            value: Value to calculate return period for
            method: Method ('empirical', 'gev', 'gumbel')

        Returns:
            Return period analysis
        """
        values = np.sort(data.values.flatten())[::-1]  # Descending
        n = len(values)

        if method == "empirical":
            # Empirical return period using Weibull plotting position
            ranks = np.arange(1, n + 1)
            exc_probs = ranks / (n + 1)
            return_periods = 1 / exc_probs

            # Find closest value
            idx = np.argmin(np.abs(values - value))
            estimated_rp = float(return_periods[idx])
            exceedance_prob = float(exc_probs[idx])

        elif method == "gumbel":
            # Gumbel distribution
            mean = np.mean(values)
            std = np.std(values)

            # Gumbel parameters
            beta = std * np.sqrt(6) / np.pi
            mu = mean - 0.5772 * beta

            # Exceedance probability
            z = (value - mu) / beta
            exceedance_prob = 1 - np.exp(-np.exp(-z))
            estimated_rp = 1 / exceedance_prob if exceedance_prob > 0 else float("inf")

        else:  # gev (simplified)
            mean = np.mean(values)
            std = np.std(values)

            # Standard normal approximation
            z = (value - mean) / std
            exceedance_prob = 1 - 0.5 * (1 + np.tanh(z * 0.7))
            estimated_rp = 1 / exceedance_prob if exceedance_prob > 0 else float("inf")

        # Classify severity based on return period
        if estimated_rp < 5:
            severity = Severity.MINOR
        elif estimated_rp < 20:
            severity = Severity.MODERATE
        elif estimated_rp < 50:
            severity = Severity.SEVERE
        elif estimated_rp < 100:
            severity = Severity.EXTREME
        else:
            severity = Severity.CATASTROPHIC

        return {
            "value": float(value),
            "method": method,
            "return_period_years": (
                float(estimated_rp) if estimated_rp != float("inf") else None
            ),
            "exceedance_probability": float(exceedance_prob),
            "severity": severity.value,
            "historical_stats": {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "max": float(np.max(values)),
                "min": float(np.min(values)),
            },
        }

    def detect_compound_events(
        self,
        temperature: xr.DataArray,
        precipitation: xr.DataArray,
        temp_threshold_percentile: float = 90.0,
        precip_threshold_percentile: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Detect compound extreme events (e.g., hot and dry).

        Args:
            temperature: Temperature data
            precipitation: Precipitation data
            temp_threshold_percentile: Temperature threshold
            precip_threshold_percentile: Precipitation threshold

        Returns:
            Compound event analysis
        """
        temp_threshold = float(temperature.quantile(temp_threshold_percentile / 100.0))
        precip_threshold = float(
            precipitation.quantile(precip_threshold_percentile / 100.0)
        )

        # Align data
        min_len = min(len(temperature), len(precipitation))
        temp_values = temperature.values.flatten()[:min_len]
        precip_values = precipitation.values.flatten()[:min_len]

        # Identify compound events (hot AND dry)
        hot_days = temp_values >= temp_threshold
        dry_days = precip_values <= precip_threshold
        if np.nanmax(temp_values) == np.nanmin(temp_values):
            hot_days = np.zeros_like(temp_values, dtype=bool)
        if np.nanmax(precip_values) == np.nanmin(precip_values):
            dry_days = np.zeros_like(precip_values, dtype=bool)
        compound_days = hot_days & dry_days

        # Find compound periods
        events = []
        in_event = False
        event_start = 0

        for i, is_compound in enumerate(compound_days):
            if is_compound and not in_event:
                in_event = True
                event_start = i
            elif not is_compound and in_event:
                events.append(
                    {
                        "start_index": event_start,
                        "end_index": i - 1,
                        "duration_days": i - event_start,
                        "max_temp": float(max(temp_values[event_start:i])),
                        "mean_precip": float(np.mean(precip_values[event_start:i])),
                    }
                )
                in_event = False

        if in_event:
            events.append(
                {
                    "start_index": event_start,
                    "end_index": min_len - 1,
                    "duration_days": min_len - event_start,
                    "max_temp": float(max(temp_values[event_start:])),
                    "mean_precip": float(np.mean(precip_values[event_start:])),
                }
            )

        return {
            "compound_type": "hot_and_dry",
            "temp_threshold": temp_threshold,
            "precip_threshold": precip_threshold,
            "days_analyzed": min_len,
            "compound_days": int(np.sum(compound_days)),
            "compound_frequency": float(np.sum(compound_days)) / min_len * 100,
            "events_detected": len(events),
            "events": events,
            "correlation": float(np.corrcoef(temp_values, precip_values)[0, 1]),
        }

    def calculate_climate_indices(
        self, temperature: xr.DataArray, precipitation: Optional[xr.DataArray] = None
    ) -> Dict[str, Any]:
        """
        Calculate standard climate extreme indices.

        Args:
            temperature: Daily temperature data
            precipitation: Optional daily precipitation

        Returns:
            Climate indices
        """
        temp_values = temperature.values.flatten()

        indices = {}

        # Temperature indices
        indices["TXx"] = float(np.max(temp_values))  # Max of daily max temp
        indices["TNn"] = float(np.min(temp_values))  # Min of daily min temp
        indices["TX90p"] = float(np.percentile(temp_values, 90))  # 90th percentile
        indices["TX10p"] = float(np.percentile(temp_values, 10))  # 10th percentile
        indices["DTR"] = float(np.std(temp_values))  # Diurnal temp range proxy

        # Warm days (T > 25°C)
        indices["SU25"] = int(np.sum(temp_values > 25))  # Summer days

        # Frost days (T < 0°C)
        indices["FD0"] = int(np.sum(temp_values < 0))  # Frost days

        # Warm spell duration (simplified)
        p90 = np.percentile(temp_values, 90)
        warm_days = temp_values > p90
        indices["WSDI"] = int(np.sum(warm_days))  # Warm spell duration index

        # Precipitation indices
        if precipitation is not None:
            precip_values = precipitation.values.flatten()

            indices["PRCPTOT"] = float(np.sum(precip_values))  # Total precip
            indices["RX1day"] = float(np.max(precip_values))  # Max 1-day precip
            indices["SDII"] = float(
                np.mean(precip_values[precip_values >= 1])
            )  # Simple intensity
            indices["R10mm"] = int(np.sum(precip_values >= 10))  # Days >= 10mm
            indices["R20mm"] = int(np.sum(precip_values >= 20))  # Days >= 20mm
            indices["CDD"] = self._max_consecutive_dry_days(precip_values)
            indices["CWD"] = self._max_consecutive_wet_days(precip_values)

        return {
            "indices": indices,
            "description": {
                "TXx": "Maximum temperature",
                "TNn": "Minimum temperature",
                "SU25": "Summer days (T > 25°C)",
                "FD0": "Frost days (T < 0°C)",
                "WSDI": "Warm spell days",
                "PRCPTOT": "Total precipitation (mm)",
                "RX1day": "Max 1-day precipitation (mm)",
                "CDD": "Max consecutive dry days",
                "CWD": "Max consecutive wet days",
            },
        }

    def _max_consecutive_dry_days(
        self, precip: np.ndarray, threshold: float = 1.0
    ) -> int:
        """Calculate maximum consecutive dry days."""
        dry = precip < threshold
        max_run = 0
        current_run = 0
        for is_dry in dry:
            if is_dry:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0
        return max_run

    def _max_consecutive_wet_days(
        self, precip: np.ndarray, threshold: float = 1.0
    ) -> int:
        """Calculate maximum consecutive wet days."""
        wet = precip >= threshold
        max_run = 0
        current_run = 0
        for is_wet in wet:
            if is_wet:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0
        return max_run

    def _find_consecutive_periods(
        self, condition: xr.DataArray, min_duration: int
    ) -> xr.Dataset:
        """Find consecutive periods meeting condition."""
        # Simplified: count consecutive True values
        events = condition.astype(int).groupby("time").sum()
        events = events.where(events >= min_duration, 0)

        return xr.Dataset({"events": events})

    def register_event(self, event: ExtremeEvent) -> str:
        """Register an extreme event."""
        self.event_registry.append(event)
        logger.info(f"Registered {event.event_type.value} event: {event.event_id}")
        return event.event_id

    def get_event_statistics(self) -> Dict[str, Any]:
        """Get statistics on registered events."""
        if not self.event_registry:
            return {"error": "No events registered"}

        by_type = {}
        for event in self.event_registry:
            etype = event.event_type.value
            if etype not in by_type:
                by_type[etype] = {
                    "count": 0,
                    "total_duration": 0,
                    "avg_duration": 0,
                    "severities": {},
                }
            by_type[etype]["count"] += 1
            by_type[etype]["total_duration"] += event.duration_days

            sev = event.severity.value
            by_type[etype]["severities"][sev] = (
                by_type[etype]["severities"].get(sev, 0) + 1
            )

        # Calculate averages
        for etype in by_type:
            by_type[etype]["avg_duration"] = (
                by_type[etype]["total_duration"] / by_type[etype]["count"]
            )

        return {"total_events": len(self.event_registry), "by_type": by_type}
