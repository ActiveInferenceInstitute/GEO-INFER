"""Water infrastructure planning module."""

import logging
from typing import Dict, Optional
import numpy as np
import xarray as xr

logger = logging.getLogger(__name__)


class WaterInfrastructurePlanner:
    """Plan water infrastructure."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize infrastructure planner."""
        self.config = config or {}
    
    def optimize_water_allocation(
        self,
        water_supply: xr.DataArray,
        water_demand: xr.DataArray,
        priorities: Optional[xr.DataArray] = None
    ) -> xr.Dataset:
        """
        Optimize water allocation.
        
        Args:
            water_supply: Available water supply
            water_demand: Water demand
            priorities: Optional priority weights
            
        Returns:
            Allocation optimization results
        """
        # Calculate supply-demand ratio
        supply_demand_ratio = water_supply / (water_demand + 1e-10)
        
        # Allocation (proportional to supply)
        if priorities is not None:
            allocation = water_supply * priorities / priorities.sum()
        else:
            allocation = water_supply * (water_demand / (water_demand.sum() + 1e-10))
        
        # Shortage
        shortage = xr.where(water_demand > allocation, water_demand - allocation, 0)
        
        return xr.Dataset({
            'allocation': allocation,
            'shortage': shortage,
            'supply_demand_ratio': supply_demand_ratio,
            'adequacy': xr.where(supply_demand_ratio >= 1, 1, supply_demand_ratio)
        })
    
    def assess_infrastructure_needs(
        self,
        current_capacity: xr.DataArray,
        projected_demand: xr.DataArray
    ) -> xr.Dataset:
        """
        Assess water infrastructure capacity needs.
        
        Args:
            current_capacity: Current infrastructure capacity
            projected_demand: Projected future demand
            
        Returns:
            Infrastructure needs assessment
        """
        capacity_gap = projected_demand - current_capacity
        capacity_gap = xr.where(capacity_gap < 0, 0, capacity_gap)
        
        adequacy = current_capacity / (projected_demand + 1e-10)
        
        return xr.Dataset({
            'capacity_gap': capacity_gap,
            'adequacy': adequacy,
            'expansion_needed': capacity_gap > 0
        })

