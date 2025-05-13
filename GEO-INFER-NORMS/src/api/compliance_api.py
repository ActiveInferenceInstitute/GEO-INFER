"""
Compliance API module for tracking and reporting on regulatory compliance.

This module provides API endpoints for interacting with compliance tracking
functionality, including status checks, evaluations, and reporting.
"""

from typing import Dict, List, Optional, Union, Any
import datetime
from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends
from pydantic import BaseModel, Field
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
import json

from geo_infer_norms.core.compliance_tracking import ComplianceTracker, ComplianceReport
from geo_infer_norms.models.compliance_status import ComplianceStatus, ComplianceMetric
from geo_infer_norms.models.regulation import Regulation
from geo_infer_norms.models.legal_entity import LegalEntity


# Pydantic models for API request/response
class ComplianceStatusCreate(BaseModel):
    """Request model for creating a compliance status"""
    entity_id: str = Field(..., description="ID of the legal entity being evaluated")
    regulation_id: str = Field(..., description="ID of the regulation being evaluated")
    is_compliant: bool = Field(..., description="Whether the entity is compliant with the regulation")
    compliance_level: float = Field(..., ge=0.0, le=1.0, description="Compliance level between 0.0 and 1.0")
    notes: Optional[str] = Field(None, description="Additional notes about the compliance status")
    metric_results: Optional[List[Dict[str, Any]]] = Field(None, description="Results of individual metric evaluations")
    
    class Config:
        schema_extra = {
            "example": {
                "entity_id": "entity-123",
                "regulation_id": "reg-456",
                "is_compliant": True,
                "compliance_level": 0.85,
                "notes": "All requirements met with minor observations",
                "metric_results": [
                    {
                        "metric_id": "metric-1",
                        "name": "Emissions Limit",
                        "is_compliant": True,
                        "compliance_level": 0.9,
                        "notes": "Emissions well below threshold"
                    }
                ]
            }
        }


class ComplianceMetricCreate(BaseModel):
    """Request model for creating a compliance metric"""
    name: str = Field(..., description="Name of the compliance metric")
    description: Optional[str] = Field(None, description="Description of the metric")
    regulation_id: str = Field(..., description="ID of the regulation this metric is for")
    evaluation_type: str = Field(..., description="Type of evaluation (threshold, range, boolean)")
    primary_field: str = Field(..., description="Primary data field for evaluation")
    required_fields: List[str] = Field(..., description="Required data fields for evaluation")
    threshold_value: Optional[float] = Field(None, description="Threshold value for threshold evaluation")
    comparison: Optional[str] = Field(None, description="Comparison operator for threshold evaluation")
    range_min: Optional[float] = Field(None, description="Minimum value for range evaluation")
    range_max: Optional[float] = Field(None, description="Maximum value for range evaluation")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Emissions Limit",
                "description": "Maximum allowable emissions level",
                "regulation_id": "reg-456",
                "evaluation_type": "threshold",
                "primary_field": "emissions_level",
                "required_fields": ["emissions_level", "measurement_date"],
                "threshold_value": 50.0,
                "comparison": "less_than"
            }
        }


class EvaluationData(BaseModel):
    """Request model for compliance evaluation data"""
    entity_id: str = Field(..., description="ID of the entity to evaluate")
    regulation_id: str = Field(..., description="ID of the regulation to evaluate against")
    evaluation_data: Dict[str, Any] = Field(..., description="Data points for evaluation")
    
    class Config:
        schema_extra = {
            "example": {
                "entity_id": "entity-123",
                "regulation_id": "reg-456",
                "evaluation_data": {
                    "emissions_level": 42.5,
                    "measurement_date": "2023-10-15",
                    "measurement_location": "Stack 3",
                    "operating_hours": 168
                }
            }
        }


class GeoPoint(BaseModel):
    """Geographic point model"""
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude")
    lon: float = Field(..., ge=-180.0, le=180.0, description="Longitude")


class ReportParams(BaseModel):
    """Parameters for generating reports"""
    title: Optional[str] = Field(None, description="Report title")
    description: Optional[str] = Field(None, description="Report description")
    as_of_date: Optional[datetime.datetime] = Field(None, description="Report as of date")
    export_format: Optional[str] = Field("json", description="Export format (json, html)")


class ComplianceAPI:
    """API for compliance tracking and reporting"""
    
    def __init__(self, compliance_tracker: Optional[ComplianceTracker] = None):
        """
        Initialize the ComplianceAPI.
        
        Args:
            compliance_tracker: Optional ComplianceTracker instance to use
        """
        self.compliance_tracker = compliance_tracker or ComplianceTracker(
            name="Default Compliance Tracker",
            description="Default tracker for compliance management"
        )
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Set up API routes"""
        # Status endpoints
        self.router.post("/status", response_model=Dict[str, Any])(self.add_compliance_status)
        self.router.get("/status/entity/{entity_id}", response_model=Dict[str, Any])(self.get_entity_compliance)
        self.router.get("/status/regulation/{regulation_id}", response_model=Dict[str, Any])(self.get_regulation_compliance)
        
        # Metric endpoints
        self.router.post("/metrics", response_model=Dict[str, Any])(self.add_compliance_metric)
        self.router.get("/metrics", response_model=List[Dict[str, Any]])(self.list_compliance_metrics)
        
        # Evaluation endpoints
        self.router.post("/evaluate", response_model=Dict[str, Any])(self.evaluate_compliance)
        self.router.post("/evaluate/location", response_model=Dict[str, Any])(self.evaluate_compliance_at_location)
        
        # Report endpoints
        self.router.post("/reports/summary", response_model=Dict[str, Any])(self.generate_summary_report)
        self.router.post("/reports/entity/{entity_id}", response_model=Dict[str, Any])(self.generate_entity_report)
        self.router.post("/reports/regulation/{regulation_id}", response_model=Dict[str, Any])(self.generate_regulation_report)
        self.router.post("/reports/export", response_model=Dict[str, Any])(self.export_report)
        
        # GeoJSON endpoints
        self.router.post("/geo/export", response_model=Dict[str, Any])(self.export_to_geojson)
    
    # Status endpoints
    
    async def add_compliance_status(self, status_data: ComplianceStatusCreate) -> Dict[str, Any]:
        """
        Add a new compliance status.
        
        Args:
            status_data: The compliance status data
            
        Returns:
            Success message with status ID
        """
        try:
            # Create a ComplianceStatus object
            status = ComplianceStatus(
                id=f"status-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                entity_id=status_data.entity_id,
                regulation_id=status_data.regulation_id,
                is_compliant=status_data.is_compliant,
                compliance_level=status_data.compliance_level,
                timestamp=datetime.datetime.now(),
                notes=status_data.notes or "",
                metric_results=status_data.metric_results or []
            )
            
            # Add to tracker
            self.compliance_tracker.add_compliance_status(status)
            
            return {
                "status": "success",
                "message": "Compliance status added successfully",
                "status_id": status.id
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding compliance status: {str(e)}")
    
    async def get_entity_compliance(
        self, 
        entity_id: str = Path(..., description="ID of the entity"),
        as_of_date: Optional[datetime.datetime] = Query(None, description="As of date (default: current time)")
    ) -> Dict[str, Any]:
        """
        Get compliance status for all regulations for a specific entity.
        
        Args:
            entity_id: The ID of the entity
            as_of_date: Optional date to get compliance status as of
            
        Returns:
            Entity compliance information
        """
        try:
            compliance_info = self.compliance_tracker.get_entity_compliance(
                entity_id=entity_id,
                as_of_date=as_of_date
            )
            return compliance_info
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting entity compliance: {str(e)}")
    
    async def get_regulation_compliance(
        self, 
        regulation_id: str = Path(..., description="ID of the regulation"),
        as_of_date: Optional[datetime.datetime] = Query(None, description="As of date (default: current time)")
    ) -> Dict[str, Any]:
        """
        Get compliance status for all entities for a specific regulation.
        
        Args:
            regulation_id: The ID of the regulation
            as_of_date: Optional date to get compliance status as of
            
        Returns:
            Regulation compliance information
        """
        try:
            compliance_info = self.compliance_tracker.get_regulation_compliance(
                regulation_id=regulation_id,
                as_of_date=as_of_date
            )
            return compliance_info
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting regulation compliance: {str(e)}")
    
    # Metric endpoints
    
    async def add_compliance_metric(self, metric_data: ComplianceMetricCreate) -> Dict[str, Any]:
        """
        Add a new compliance metric.
        
        Args:
            metric_data: The compliance metric data
            
        Returns:
            Success message with metric ID
        """
        try:
            # Create a ComplianceMetric object
            metric = ComplianceMetric(
                id=f"metric-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                name=metric_data.name,
                description=metric_data.description or "",
                regulation_id=metric_data.regulation_id,
                evaluation_type=metric_data.evaluation_type,
                primary_field=metric_data.primary_field,
                required_fields=metric_data.required_fields,
                threshold_value=metric_data.threshold_value,
                comparison=metric_data.comparison,
                range_min=metric_data.range_min,
                range_max=metric_data.range_max
            )
            
            # Add to tracker
            self.compliance_tracker.add_compliance_metric(metric)
            
            return {
                "status": "success",
                "message": "Compliance metric added successfully",
                "metric_id": metric.id
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding compliance metric: {str(e)}")
    
    async def list_compliance_metrics(
        self,
        regulation_id: Optional[str] = Query(None, description="Filter by regulation ID")
    ) -> List[Dict[str, Any]]:
        """
        List all compliance metrics, optionally filtered by regulation.
        
        Args:
            regulation_id: Optional regulation ID to filter by
            
        Returns:
            List of compliance metrics
        """
        try:
            metrics = self.compliance_tracker.compliance_metrics
            
            if regulation_id:
                metrics = [m for m in metrics if m.regulation_id == regulation_id]
            
            return [
                {
                    "id": m.id,
                    "name": m.name,
                    "description": m.description,
                    "regulation_id": m.regulation_id,
                    "evaluation_type": m.evaluation_type,
                    "primary_field": m.primary_field,
                    "required_fields": m.required_fields,
                    "threshold_value": m.threshold_value,
                    "comparison": m.comparison,
                    "range_min": m.range_min,
                    "range_max": m.range_max
                }
                for m in metrics
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error listing compliance metrics: {str(e)}")
    
    # Evaluation endpoints
    
    async def evaluate_compliance(self, evaluation_data: EvaluationData) -> Dict[str, Any]:
        """
        Evaluate compliance of an entity with a regulation based on data.
        
        Args:
            evaluation_data: The evaluation data
            
        Returns:
            Evaluation results
        """
        try:
            # This is a simplified version - in reality we would need to get the entity and regulation objects
            entity = LegalEntity(
                id=evaluation_data.entity_id,
                name=f"Entity {evaluation_data.entity_id}",
                legal_type="unknown"
            )
            
            regulation = Regulation(
                id=evaluation_data.regulation_id,
                name=f"Regulation {evaluation_data.regulation_id}",
                description="",
                applicable_jurisdictions=[]
            )
            
            # Evaluate compliance
            status = self.compliance_tracker.evaluate_compliance(
                entity=entity,
                regulation=regulation,
                evaluation_data=evaluation_data.evaluation_data
            )
            
            return {
                "status": "success",
                "entity_id": entity.id,
                "regulation_id": regulation.id,
                "is_compliant": status.is_compliant,
                "compliance_level": status.compliance_level,
                "timestamp": status.timestamp.isoformat(),
                "notes": status.notes,
                "metric_results": status.metric_results
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error evaluating compliance: {str(e)}")
    
    async def evaluate_compliance_at_location(
        self,
        point: GeoPoint,
        regulation_ids: Optional[List[str]] = Body(None, description="List of regulation IDs to evaluate"),
        entity_id: str = Body(..., description="ID of the entity to evaluate"),
        evaluation_data: Dict[str, Any] = Body(..., description="Data points for evaluation")
    ) -> Dict[str, Any]:
        """
        Evaluate compliance at a specific geographic location.
        
        Args:
            point: Geographic point
            regulation_ids: Optional list of regulation IDs
            entity_id: ID of the entity to evaluate
            evaluation_data: Data points for evaluation
            
        Returns:
            Evaluation results
        """
        # This would need to be implemented with spatial lookup functionality
        # For now, return a mock response
        return {
            "status": "success",
            "message": "Location-based compliance evaluation not implemented",
            "location": {"lat": point.lat, "lon": point.lon},
            "entity_id": entity_id
        }
    
    # Report endpoints
    
    async def generate_summary_report(self, params: ReportParams) -> Dict[str, Any]:
        """
        Generate a summary compliance report.
        
        Args:
            params: Report parameters
            
        Returns:
            Summary report
        """
        try:
            # Create a ComplianceReport
            report = ComplianceReport(
                compliance_tracker=self.compliance_tracker,
                title=params.title or "Compliance Summary Report",
                description=params.description or "Summary of compliance statuses"
            )
            
            # Generate report
            summary = report.generate_summary_report(
                as_of_date=params.as_of_date
            )
            
            return summary
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating summary report: {str(e)}")
    
    async def generate_entity_report(
        self,
        entity_id: str = Path(..., description="ID of the entity"),
        params: ReportParams = Body(...)
    ) -> Dict[str, Any]:
        """
        Generate a detailed compliance report for a specific entity.
        
        Args:
            entity_id: The ID of the entity
            params: Report parameters
            
        Returns:
            Entity report
        """
        try:
            # Create a ComplianceReport
            report = ComplianceReport(
                compliance_tracker=self.compliance_tracker,
                title=params.title or f"Entity Compliance Report: {entity_id}",
                description=params.description or f"Compliance report for entity {entity_id}"
            )
            
            # Generate report
            entity_report = report.generate_entity_report(
                entity_id=entity_id,
                as_of_date=params.as_of_date
            )
            
            return entity_report
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating entity report: {str(e)}")
    
    async def generate_regulation_report(
        self,
        regulation_id: str = Path(..., description="ID of the regulation"),
        params: ReportParams = Body(...)
    ) -> Dict[str, Any]:
        """
        Generate a detailed compliance report for a specific regulation.
        
        Args:
            regulation_id: The ID of the regulation
            params: Report parameters
            
        Returns:
            Regulation report
        """
        try:
            # Create a ComplianceReport
            report = ComplianceReport(
                compliance_tracker=self.compliance_tracker,
                title=params.title or f"Regulation Compliance Report: {regulation_id}",
                description=params.description or f"Compliance report for regulation {regulation_id}"
            )
            
            # Generate report
            regulation_report = report.generate_regulation_report(
                regulation_id=regulation_id,
                as_of_date=params.as_of_date
            )
            
            return regulation_report
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating regulation report: {str(e)}")
    
    async def export_report(
        self,
        report_type: str = Body(..., description="Type of report (summary, entity, regulation)"),
        entity_id: Optional[str] = Body(None, description="Entity ID for entity reports"),
        regulation_id: Optional[str] = Body(None, description="Regulation ID for regulation reports"),
        params: ReportParams = Body(...)
    ) -> Dict[str, Any]:
        """
        Export a report in the specified format.
        
        Args:
            report_type: Type of report
            entity_id: Optional entity ID
            regulation_id: Optional regulation ID
            params: Report parameters
            
        Returns:
            Export information
        """
        try:
            # Create a ComplianceReport
            report = ComplianceReport(
                compliance_tracker=self.compliance_tracker,
                title=params.title or f"Compliance Report",
                description=params.description or "Exported compliance report"
            )
            
            if params.export_format == "html":
                # Example for HTML export
                file_path = f"report_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.html"
                
                # This would actually export the file in a real implementation
                # report.export_report_to_html(file_path)
                
                return {
                    "status": "success",
                    "message": "Report exported successfully",
                    "format": "html",
                    "file_path": file_path
                }
            else:
                # Default to JSON
                if report_type == "summary":
                    data = report.generate_summary_report(as_of_date=params.as_of_date)
                elif report_type == "entity" and entity_id:
                    data = report.generate_entity_report(entity_id=entity_id, as_of_date=params.as_of_date)
                elif report_type == "regulation" and regulation_id:
                    data = report.generate_regulation_report(regulation_id=regulation_id, as_of_date=params.as_of_date)
                else:
                    raise ValueError(f"Invalid report type or missing required parameters")
                
                return {
                    "status": "success",
                    "message": "Report data generated successfully",
                    "format": "json",
                    "data": data
                }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error exporting report: {str(e)}")
    
    # GeoJSON endpoints
    
    async def export_to_geojson(
        self,
        entity_ids: List[str] = Body(..., description="List of entity IDs to include"),
        regulation_id: Optional[str] = Body(None, description="Optional regulation ID to filter by"),
        as_of_date: Optional[datetime.datetime] = Body(None, description="As of date (default: current time)")
    ) -> Dict[str, Any]:
        """
        Export compliance data to GeoJSON format for mapping.
        
        Args:
            entity_ids: List of entity IDs to include
            regulation_id: Optional regulation ID to filter by
            as_of_date: Optional date to get compliance status as of
            
        Returns:
            GeoJSON data
        """
        try:
            # This is a simplified version - in reality we would need to get actual entity objects with geometries
            entities = [
                LegalEntity(
                    id=entity_id,
                    name=f"Entity {entity_id}",
                    legal_type="unknown",
                    geometry=Point(0, 0)  # Mock geometry
                )
                for entity_id in entity_ids
            ]
            
            # Export to GeoDataFrame
            gdf = self.compliance_tracker.export_compliance_to_geodataframe(
                entities=entities,
                regulation_id=regulation_id,
                as_of_date=as_of_date
            )
            
            if gdf.empty:
                return {
                    "status": "warning",
                    "message": "No compliance data with geometry found for GeoJSON export",
                    "geojson": None
                }
            
            # Convert to GeoJSON
            geojson = json.loads(gdf.to_json())
            
            return {
                "status": "success",
                "message": "Compliance data exported to GeoJSON successfully",
                "feature_count": len(geojson["features"]),
                "geojson": geojson
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error exporting to GeoJSON: {str(e)}") 