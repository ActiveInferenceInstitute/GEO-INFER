from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Location(BaseModel):
    """Represents a geographic location."""
    latitude: float = Field(..., description="Latitude of the location.")
    longitude: float = Field(..., description="Longitude of the location.")
    crs: str = Field("EPSG:4326", description="Coordinate Reference System.")

class HealthFacility(BaseModel):
    """Represents a healthcare facility."""
    facility_id: str = Field(..., description="Unique identifier for the facility.")
    name: str = Field(..., description="Name of the health facility.")
    facility_type: str = Field(..., description="Type of health facility (e.g., hospital, clinic).")
    location: Location = Field(..., description="Geographic location of the facility.")
    capacity: Optional[int] = Field(None, description="Capacity of the facility (e.g., number of beds).")
    services_offered: List[str] = Field(default_factory=list, description="List of services offered.")
    operating_hours: Optional[str] = Field(None, description="Operating hours of the facility.")
    contact_info: Optional[Dict[str, str]] = Field(None, description="Contact information (e.g., phone, email).")

class DiseaseReport(BaseModel):
    """Represents a report of a disease case or observation."""
    report_id: str = Field(..., description="Unique identifier for the report.")
    disease_code: str = Field(..., description="Standardized code for the disease (e.g., ICD-10).")
    location: Location = Field(..., description="Geographic location of the reported case.")
    report_date: datetime = Field(..., description="Date and time of the report.")
    case_count: int = Field(1, description="Number of cases in this report.", ge=1)
    source: Optional[str] = Field(None, description="Source of the report (e.g., hospital, lab).")
    demographics: Optional[Dict[str, Any]] = Field(None, description="Anonymized demographic data if available.")
    notes: Optional[str] = Field(None, description="Additional notes for the report.")

class PopulationData(BaseModel):
    """Represents population data for a given area, potentially a polygon."""
    area_id: str = Field(..., description="Identifier for the administrative or statistical area.")
    # geometry: Any # Would typically be a GeoJSON dict or a Shapely geometry object
    population_count: int = Field(..., description="Total population in the area.")
    age_distribution: Optional[Dict[str, int]] = Field(None, description="Population count by age group.")
    other_demographics: Optional[Dict[str, Any]] = Field(None, description="Other relevant demographic splits.")

class EnvironmentalData(BaseModel):
    """Represents an environmental data point or raster summary."""
    data_id: str = Field(..., description="Identifier for the environmental data record.")
    parameter_name: str = Field(..., description="Name of the environmental parameter (e.g., PM2.5, Temperature).")
    value: float = Field(..., description="Value of the environmental parameter.")
    unit: str = Field(..., description="Unit of the environmental parameter.")
    location: Location = Field(..., description="Geographic location of the data point.")
    timestamp: datetime = Field(..., description="Timestamp of the data recording.")
    # For raster data, this might include cell_value, raster_id, band_info etc.
    # For vector data, it might be associated with a polygon geometry. 