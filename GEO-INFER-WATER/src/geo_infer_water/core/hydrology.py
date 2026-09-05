"""Hydrological modeling module."""

import logging
from typing import Dict, Optional

import xarray as xr

logger = logging.getLogger(__name__)


class HydrologicalModeler:
    """Model hydrological processes."""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize hydrological modeler."""
        self.config = config or {}

    def rainfall_runoff_model(
        self,
        precipitation: xr.DataArray,
        soil_moisture: Optional[xr.DataArray] = None,
        infiltration_rate: float = 0.5
    ) -> xr.Dataset:
        """
        Simple rainfall-runoff model.

        Precipitation is split into infiltration and runoff. When soil
        moisture is supplied (0-1 fraction of saturation) the effective
        infiltration rate is reduced and the split is renormalized so that
        ``runoff + infiltration == precipitation`` (mass is conserved).

        Args:
            precipitation: Precipitation data
            soil_moisture: Optional soil moisture data (0-1 saturation)
            infiltration_rate: Infiltration rate (0-1)

        Returns:
            Runoff and infiltration results
        """
        # Split precipitation into infiltration and runoff.
        infiltration = precipitation * infiltration_rate
        runoff = precipitation - infiltration

        # Adjust for soil moisture if available. Soil moisture is assumed
        # to be on a 0-1 scale (fraction of saturation): wetter soil reduces
        # infiltration capacity and shifts more water to runoff. The split
        # is renormalized so that runoff + infiltration == precipitation
        # (mass is conserved) for every saturation level.
        if soil_moisture is not None:
            saturation_factor = xr.where(soil_moisture > 1.0, 1.0, soil_moisture)
            saturation_factor = xr.where(saturation_factor < 0.0, 0.0, saturation_factor)
            # Effective infiltration fraction shrinks as soil saturates.
            effective_infiltration_rate = infiltration_rate * (1.0 - saturation_factor * 0.5)
            effective_infiltration_rate = xr.where(
                effective_infiltration_rate < 0.0, 0.0, effective_infiltration_rate
            )
            infiltration = precipitation * effective_infiltration_rate
            runoff = precipitation - infiltration

        return xr.Dataset({
            'runoff': runoff,
            'infiltration': infiltration,
            'precipitation': precipitation
        })

    def estimate_groundwater_recharge(
        self,
        infiltration: xr.DataArray,
        evapotranspiration: Optional[xr.DataArray] = None
    ) -> xr.DataArray:
        """
        Estimate groundwater recharge.

        Args:
            infiltration: Infiltration data
            evapotranspiration: Optional ET data

        Returns:
            Groundwater recharge
        """
        recharge = infiltration.copy()

        if evapotranspiration is not None:
            # ET reduces recharge
            recharge = recharge - evapotranspiration * 0.3
            recharge = xr.where(recharge < 0, 0, recharge)

        return recharge

    def calculate_water_balance(
        self,
        precipitation: xr.DataArray,
        evapotranspiration: xr.DataArray,
        runoff: xr.DataArray
    ) -> xr.Dataset:
        """Calculate water balance.

        Delegates to :meth:`WaterBalanceModeler.water_balance_closure`,
        the canonical water-balance owner in this module, to avoid a
        second implementation of the same residual calculation.

        Args:
            precipitation: Precipitation
            evapotranspiration: Evapotranspiration
            runoff: Runoff

        Returns:
            Water balance components
        """
        from .water_balance import WaterBalanceModeler

        return WaterBalanceModeler(self.config).water_balance_closure(
            precipitation, evapotranspiration, runoff
        )
