from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import math
from datetime import timedelta

from geo_infer_health.models import DiseaseReport, Location, PopulationData
from geo_infer_health.utils.geospatial_utils import haversine_distance, create_bounding_box

class DiseaseHotspotAnalyzer:
    """Analyzes disease reports to identify hotspots."""

    def __init__(self, reports: List[DiseaseReport], population_data: Optional[List[PopulationData]] = None):
        self.reports = sorted(reports, key=lambda r: r.report_date)
        self.population_data = population_data if population_data else []
        # Potential pre-processing: create a spatial index for reports or population_data

    def get_cases_in_radius(self, center_loc: Location, radius_km: float) -> List[DiseaseReport]:
        """Returns all disease reports within a given radius of a center location."""
        return [report for report in self.reports if haversine_distance(report.location, center_loc) <= radius_km]

    def calculate_local_incidence_rate(
        self, 
        center_loc: Location, 
        radius_km: float, 
        time_window_days: Optional[int] = None
    ) -> Tuple[float, int, int]: # Returns (incidence_rate, total_cases, estimated_population)
        """Calculates the incidence rate within a given radius and time window.
           Incidence rate is per 100,000 population, if population data is available.
           If no time window, uses all reports.
        """
        relevant_reports = self.reports
        if time_window_days and self.reports:
            latest_report_date = self.reports[-1].report_date
            start_date = latest_report_date - timedelta(days=time_window_days)
            relevant_reports = [r for r in self.reports if r.report_date >= start_date]

        cases_in_radius = [report for report in relevant_reports if haversine_distance(report.location, center_loc) <= radius_km]
        total_cases = sum(report.case_count for report in cases_in_radius)

        # Estimate population in radius (simplified)
        # A more accurate approach would use GIS operations (e.g., point-in-polygon, areal interpolation)
        estimated_population = 0
        if self.population_data:
            for pop_area in self.population_data:
                # This is a very rough check, assumes population data points are centroids
                # and their 'area_id' might imply a certain coverage that can be approximated.
                # Ideally, we'd have polygon geometries for population areas.
                # For now, if a population data point is within the radius, we add its population.
                # This could lead to overcounting or undercounting significantly.
                if hasattr(pop_area, 'location') and haversine_distance(pop_area.location, center_loc) <= radius_km:
                     estimated_population += pop_area.population_count
                elif not hasattr(pop_area, 'location') and self.population_data:
                    # If no location for pop_area, and it's the only one, use its total as a rough estimate
                    if len(self.population_data) == 1:
                        estimated_population = pop_area.population_count 
                        break
        
        if not estimated_population and total_cases > 0: # Fallback if no pop data, return raw case count as 'rate'
            return float(total_cases), total_cases, 0
        if estimated_population == 0:
            return 0.0, total_cases, 0
        
        incidence_rate = (total_cases / estimated_population) * 100000
        return incidence_rate, total_cases, estimated_population

    def identify_simple_hotspots(
        self, 
        threshold_case_count: int = 5, 
        scan_radius_km: float = 1.0, 
        min_density_cases_per_sq_km: Optional[float] = None 
    ) -> List[Dict]:
        """Identifies simple hotspots based on case counts in a radius or density.

        Returns:
            A list of dictionaries, each representing a hotspot with 'location', 'case_count', 'radius_km'.
        """
        hotspots = []
        # This is a naive approach: iterate through each report as a potential center.
        # More sophisticated methods (e.g., DBSCAN, Getis-Ord Gi*) should be used for real applications.
        for report in self.reports:
            cases_in_scan = self.get_cases_in_radius(report.location, scan_radius_km)
            current_case_count = sum(r.case_count for r in cases_in_scan)

            is_hotspot = False
            if current_case_count >= threshold_case_count:
                is_hotspot = True
            
            if min_density_cases_per_sq_km is not None:
                area_sq_km = math.pi * (scan_radius_km ** 2)
                density = current_case_count / area_sq_km if area_sq_km > 0 else 0
                if density >= min_density_cases_per_sq_km:
                    is_hotspot = True
                else:
                    if current_case_count < threshold_case_count: # if density was the only criteria initially failing
                        is_hotspot = False

            if is_hotspot:
                # Avoid adding nearly identical hotspots by checking distance to existing ones
                is_new_hotspot = True
                for hs in hotspots:
                    if haversine_distance(Location(**hs['location']), report.location) < scan_radius_km / 2:
                        # If a new potential hotspot is too close to an existing one,
                        # update the existing one if the new one has more cases.
                        if current_case_count > hs['case_count']:
                            hs['case_count'] = current_case_count
                            hs['location'] = report.location.model_dump() # Pydantic v2
                        is_new_hotspot = False
                        break
                if is_new_hotspot:
                    hotspots.append({
                        "location": report.location.model_dump(),
                        "case_count": current_case_count,
                        "radius_km": scan_radius_km,
                        "comment": "Simple threshold-based hotspot"
                    })
        return hotspots

# Placeholder for disease spread modeling functions
# def simulate_sir_model_spatial(initial_infected_reports: List[DiseaseReport], ...):
#     pass

# Placeholder for contact tracing support functions
# def find_potential_contacts(case_report: DiseaseReport, search_radius_km: float, time_window_hours: int):
#     pass 