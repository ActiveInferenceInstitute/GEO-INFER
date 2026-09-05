"""Energy grid optimization module."""

import logging
from typing import Dict, Optional
import xarray as xr

logger = logging.getLogger(__name__)


class EnergyGridOptimizer:
    """Optimize energy grid networks."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize grid optimizer."""
        self.config = config or {}
    
    def optimize_grid_network(
        self,
        demand: xr.DataArray,
        supply: xr.DataArray,
        transmission_capacity: Optional[xr.DataArray] = None
    ) -> xr.Dataset:
        """
        Optimize energy grid network.
        
        Args:
            demand: Energy demand
            supply: Energy supply
            transmission_capacity: Optional transmission capacity
            
        Returns:
            Grid optimization results
        """
        # Calculate supply-demand balance
        balance = supply - demand
        
        # Identify deficits and surpluses
        deficit = xr.where(balance < 0, -balance, 0)
        surplus = xr.where(balance > 0, balance, 0)
        
        # Grid reliability
        reliability = supply / (demand + 1e-10)
        reliability = xr.where(reliability > 1, 1, reliability)
        
        return xr.Dataset({
            'balance': balance,
            'deficit': deficit,
            'surplus': surplus,
            'reliability': reliability
        })
    
    def assess_grid_reliability(
        self,
        generation_capacity: xr.DataArray,
        peak_demand: xr.DataArray,
        reserve_margin: float = 0.15
    ) -> xr.Dataset:
        """
        Assess grid reliability.
        
        Args:
            generation_capacity: Total generation capacity
            peak_demand: Peak demand
            reserve_margin: Required reserve margin (0-1)
            
        Returns:
            Reliability assessment
        """
        required_capacity = peak_demand * (1 + reserve_margin)
        adequacy = generation_capacity / (required_capacity + 1e-10)
        
        # Reliability index (1 = adequate, <1 = inadequate)
        reliability = xr.where(adequacy >= 1, 1, adequacy)
        
        return xr.Dataset({
            'required_capacity': required_capacity,
            'adequacy': adequacy,
            'reliability_index': reliability,
            'capacity_deficit': xr.where(adequacy < 1, required_capacity - generation_capacity, 0)
        })

