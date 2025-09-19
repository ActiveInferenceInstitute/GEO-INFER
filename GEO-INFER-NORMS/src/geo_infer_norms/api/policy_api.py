"""
Policy API module for geospatial policy analysis and impact assessment.

This module provides API endpoints for interacting with policy definitions,
implementations, and impact assessments.
"""

from typing import Dict, List, Optional, Union, Any
import datetime
from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends
from pydantic import BaseModel, Field
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon, shape
import json
from shapely.geometry.base import BaseGeometry

from geo_infer_norms.core.policy_impact import PolicyImpactAnalyzer, RegulatoryImpactAssessment
from geo_infer_norms.models.policy import Policy, PolicyImplementation


# Pydantic models for API request/response
class GeometryModel(BaseModel):
    """Model for GeoJSON geometry data"""
    type: str
    coordinates: Any
    
    class Config:
        arbitrary_types_allowed = True


class PolicyCreate(BaseModel):
    """Request model for creating a policy"""
    name: str = Field(..., description="Name of the policy")
    description: Optional[str] = Field(None, description="Description of the policy")
    category: str = Field(..., description="Category of policy")
    issuing_authority: Optional[str] = Field(None, description="Authority that issued the policy")
    effective_date: Optional[datetime.datetime] = Field(None, description="When the policy takes effect")
    expiration_date: Optional[datetime.datetime] = Field(None, description="When the policy expires")
    jurisdiction_ids: List[str] = Field(..., description="IDs of jurisdictions where this policy applies")
    status: Optional[str] = Field("active", description="Status of the policy (draft, active, expired)")
    source_url: Optional[str] = Field(None, description="URL to the source document")
    tags: Optional[List[str]] = Field(None, description="Tags for the policy")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Green Infrastructure Policy",
                "description": "Policy promoting sustainable stormwater management using green infrastructure",
                "category": "environmental",
                "issuing_authority": "Department of Environmental Protection",
                "effective_date": "2023-01-01T00:00:00Z",
                "jurisdiction_ids": ["city-001", "city-002"],
                "status": "active",
                "tags": ["stormwater", "green", "infrastructure", "sustainability"]
            }
        }


class PolicyImplementationCreate(BaseModel):
    """Request model for creating a policy implementation"""
    policy_id: str = Field(..., description="ID of the policy being implemented")
    name: str = Field(..., description="Name of the implementation")
    description: Optional[str] = Field(None, description="Description of the implementation")
    start_date: Optional[datetime.datetime] = Field(None, description="Start date of implementation")
    end_date: Optional[datetime.datetime] = Field(None, description="End date of implementation")
    jurisdiction_id: str = Field(..., description="ID of jurisdiction where implemented")
    geometry: Optional[GeometryModel] = Field(None, description="GeoJSON geometry of implementation area")
    budget: Optional[float] = Field(None, description="Budget allocated for implementation")
    status: Optional[str] = Field("planned", description="Status (planned, in_progress, completed, canceled)")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Metrics for measuring implementation")
    
    class Config:
        schema_extra = {
            "example": {
                "policy_id": "policy-001",
                "name": "Downtown Green Infrastructure Program",
                "description": "Implementation of green infrastructure in downtown area",
                "start_date": "2023-03-01T00:00:00Z",
                "end_date": "2023-12-31T00:00:00Z",
                "jurisdiction_id": "city-001",
                "budget": 500000.0,
                "status": "in_progress",
                "metrics": {
                    "area_treated": {"value": 25000, "unit": "square_meters"},
                    "runoff_reduction": {"value": 80, "unit": "percent"}
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
                }
            }
        }


class ImpactAssessmentRequest(BaseModel):
    """Request model for policy impact assessment"""
    policy_id: str = Field(..., description="ID of the policy to assess")
    assessment_type: str = Field(..., description="Type of assessment (environmental, economic, social)")
    assessment_date: Optional[datetime.datetime] = Field(None, description="Date of assessment")
    spatial_extent: Optional[GeometryModel] = Field(None, description="GeoJSON geometry of assessment area")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Assessment parameters")
    
    class Config:
        schema_extra = {
            "example": {
                "policy_id": "policy-001",
                "assessment_type": "environmental",
                "assessment_date": "2023-06-15T00:00:00Z",
                "parameters": {
                    "metrics": ["water_quality", "habitat_impact", "carbon_sequestration"],
                    "baseline_year": 2020,
                    "projection_years": [2025, 2030]
                },
                "spatial_extent": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
                }
            }
        }


class RegulationComparisonRequest(BaseModel):
    """Request model for comparing regulations"""
    regulation_ids: List[str] = Field(..., description="IDs of regulations to compare")
    jurisdiction_id: Optional[str] = Field(None, description="Optional jurisdiction ID for context")
    comparison_metrics: List[str] = Field(..., description="Metrics to use for comparison")
    
    class Config:
        schema_extra = {
            "example": {
                "regulation_ids": ["reg-001", "reg-002", "reg-003"],
                "jurisdiction_id": "city-001",
                "comparison_metrics": ["compliance_cost", "environmental_benefit", "implementation_timeline"]
            }
        }


class PolicyAPI:
    """API for policy management and impact analysis"""
    
    def __init__(
        self, 
        policy_impact_analyzer: Optional[PolicyImpactAnalyzer] = None,
        regulatory_impact_assessment: Optional[RegulatoryImpactAssessment] = None
    ):
        """
        Initialize the PolicyAPI.
        
        Args:
            policy_impact_analyzer: Optional PolicyImpactAnalyzer instance to use
            regulatory_impact_assessment: Optional RegulatoryImpactAssessment instance to use
        """
        self.policy_impact_analyzer = policy_impact_analyzer or PolicyImpactAnalyzer()
        self.regulatory_impact_assessment = regulatory_impact_assessment or RegulatoryImpactAssessment()
        self.router = APIRouter()
        self._setup_routes()
        
        # Temporary storage for policies and implementations
        self._policies = {}
        self._implementations = {}
    
    def _setup_routes(self) -> None:
        """Set up API routes"""
        # Policy endpoints
        self.router.post("/policies", response_model=Dict[str, Any])(self.create_policy)
        self.router.get("/policies", response_model=List[Dict[str, Any]])(self.list_policies)
        self.router.get("/policies/{policy_id}", response_model=Dict[str, Any])(self.get_policy)
        
        # Policy implementation endpoints
        self.router.post("/implementations", response_model=Dict[str, Any])(self.create_policy_implementation)
        self.router.get("/implementations", response_model=List[Dict[str, Any]])(self.list_policy_implementations)
        self.router.get("/implementations/{implementation_id}", response_model=Dict[str, Any])(self.get_policy_implementation)
        self.router.get("/policies/{policy_id}/implementations", response_model=List[Dict[str, Any]])(self.get_implementations_by_policy)
        
        # Impact assessment endpoints
        self.router.post("/impact/assess", response_model=Dict[str, Any])(self.assess_policy_impact)
        self.router.get("/impact/history/{policy_id}", response_model=List[Dict[str, Any]])(self.get_impact_assessment_history)
        
        # Regulatory comparison endpoints
        self.router.post("/comparison/regulations", response_model=Dict[str, Any])(self.compare_regulations)
        
        # Export endpoints
        self.router.get("/export/geojson", response_model=Dict[str, Any])(self.export_to_geojson)
    
    # Helper methods
    
    def _geometry_from_model(self, geometry_model: Optional[GeometryModel]) -> Optional[BaseGeometry]:
        """
        Convert a GeometryModel to a Shapely geometry object.
        
        Args:
            geometry_model: GeometryModel to convert
            
        Returns:
            Shapely geometry object or None
        """
        if not geometry_model:
            return None
        
        geojson = {
            "type": geometry_model.type,
            "coordinates": geometry_model.coordinates
        }
        
        try:
            return shape(geojson)
        except Exception as e:
            raise ValueError(f"Invalid geometry: {str(e)}")
    
    def _policy_to_dict(self, policy: Policy) -> Dict[str, Any]:
        """
        Convert a Policy object to a dictionary for API response.
        
        Args:
            policy: Policy object
            
        Returns:
            Dictionary representation
        """
        return {
            "id": policy.id,
            "name": policy.name,
            "description": policy.description,
            "category": policy.category,
            "issuing_authority": policy.issuing_authority,
            "effective_date": policy.effective_date.isoformat() if policy.effective_date else None,
            "expiration_date": policy.expiration_date.isoformat() if policy.expiration_date else None,
            "jurisdiction_ids": policy.jurisdiction_ids,
            "status": policy.status,
            "source_url": policy.source_url,
            "tags": policy.tags
        }
    
    def _policy_implementation_to_dict(self, implementation: PolicyImplementation) -> Dict[str, Any]:
        """
        Convert a PolicyImplementation object to a dictionary for API response.
        
        Args:
            implementation: PolicyImplementation object
            
        Returns:
            Dictionary representation
        """
        geometry_dict = None
        if implementation.geometry:
            geometry_dict = json.loads(gpd.GeoSeries([implementation.geometry], crs="EPSG:4326").to_json())["features"][0]["geometry"]
        
        return {
            "id": implementation.id,
            "policy_id": implementation.policy_id,
            "name": implementation.name,
            "description": implementation.description,
            "start_date": implementation.start_date.isoformat() if implementation.start_date else None,
            "end_date": implementation.end_date.isoformat() if implementation.end_date else None,
            "jurisdiction_id": implementation.jurisdiction_id,
            "budget": implementation.budget,
            "status": implementation.status,
            "metrics": implementation.metrics,
            "geometry": geometry_dict
        }
    
    # Policy endpoints
    
    async def create_policy(self, policy_data: PolicyCreate) -> Dict[str, Any]:
        """
        Create a new policy.
        
        Args:
            policy_data: The policy data
            
        Returns:
            Success message with policy ID
        """
        try:
            # Create Policy object
            policy_id = f"policy-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            policy = Policy(
                id=policy_id,
                name=policy_data.name,
                description=policy_data.description or "",
                category=policy_data.category,
                issuing_authority=policy_data.issuing_authority,
                effective_date=policy_data.effective_date,
                expiration_date=policy_data.expiration_date,
                jurisdiction_ids=policy_data.jurisdiction_ids,
                status=policy_data.status,
                source_url=policy_data.source_url,
                tags=policy_data.tags or []
            )
            
            # Store policy
            self._policies[policy_id] = policy
            
            return {
                "status": "success",
                "message": "Policy created successfully",
                "policy_id": policy_id
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating policy: {str(e)}")
    
    async def list_policies(
        self,
        category: Optional[str] = Query(None, description="Filter by category"),
        jurisdiction_id: Optional[str] = Query(None, description="Filter by jurisdiction ID"),
        status: Optional[str] = Query(None, description="Filter by status"),
        tag: Optional[str] = Query(None, description="Filter by tag")
    ) -> List[Dict[str, Any]]:
        """
        List all policies, optionally filtered.
        
        Args:
            category: Optional category to filter by
            jurisdiction_id: Optional jurisdiction ID to filter by
            status: Optional status to filter by
            tag: Optional tag to filter by
            
        Returns:
            List of policies
        """
        try:
            policies = list(self._policies.values())
            
            if category:
                policies = [p for p in policies if p.category == category]
            
            if jurisdiction_id:
                policies = [p for p in policies if jurisdiction_id in p.jurisdiction_ids]
            
            if status:
                policies = [p for p in policies if p.status == status]
            
            if tag:
                policies = [p for p in policies if tag in (p.tags or [])]
            
            return [self._policy_to_dict(p) for p in policies]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error listing policies: {str(e)}")
    
    async def get_policy(
        self,
        policy_id: str = Path(..., description="ID of the policy")
    ) -> Dict[str, Any]:
        """
        Get a policy by ID.
        
        Args:
            policy_id: The ID of the policy
            
        Returns:
            Policy details
        """
        try:
            policy = self._policies.get(policy_id)
            
            if not policy:
                raise HTTPException(status_code=404, detail=f"Policy with ID {policy_id} not found")
            
            return self._policy_to_dict(policy)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting policy: {str(e)}")
    
    # Policy implementation endpoints
    
    async def create_policy_implementation(self, implementation_data: PolicyImplementationCreate) -> Dict[str, Any]:
        """
        Create a new policy implementation.
        
        Args:
            implementation_data: The policy implementation data
            
        Returns:
            Success message with implementation ID
        """
        try:
            # Check if policy exists
            if implementation_data.policy_id not in self._policies:
                raise HTTPException(status_code=404, detail=f"Policy with ID {implementation_data.policy_id} not found")
            
            # Convert geometry model to shapely geometry
            geometry = self._geometry_from_model(implementation_data.geometry)
            
            # Create PolicyImplementation object
            implementation_id = f"impl-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            implementation = PolicyImplementation(
                id=implementation_id,
                policy_id=implementation_data.policy_id,
                name=implementation_data.name,
                description=implementation_data.description or "",
                start_date=implementation_data.start_date,
                end_date=implementation_data.end_date,
                jurisdiction_id=implementation_data.jurisdiction_id,
                geometry=geometry,
                budget=implementation_data.budget,
                status=implementation_data.status,
                metrics=implementation_data.metrics or {}
            )
            
            # Store implementation
            self._implementations[implementation_id] = implementation
            
            return {
                "status": "success",
                "message": "Policy implementation created successfully",
                "implementation_id": implementation_id
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating policy implementation: {str(e)}")
    
    async def list_policy_implementations(
        self,
        status: Optional[str] = Query(None, description="Filter by status"),
        jurisdiction_id: Optional[str] = Query(None, description="Filter by jurisdiction ID")
    ) -> List[Dict[str, Any]]:
        """
        List all policy implementations, optionally filtered.
        
        Args:
            status: Optional status to filter by
            jurisdiction_id: Optional jurisdiction ID to filter by
            
        Returns:
            List of policy implementations
        """
        try:
            implementations = list(self._implementations.values())
            
            if status:
                implementations = [i for i in implementations if i.status == status]
            
            if jurisdiction_id:
                implementations = [i for i in implementations if i.jurisdiction_id == jurisdiction_id]
            
            return [self._policy_implementation_to_dict(i) for i in implementations]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error listing policy implementations: {str(e)}")
    
    async def get_policy_implementation(
        self,
        implementation_id: str = Path(..., description="ID of the policy implementation")
    ) -> Dict[str, Any]:
        """
        Get a policy implementation by ID.
        
        Args:
            implementation_id: The ID of the policy implementation
            
        Returns:
            Policy implementation details
        """
        try:
            implementation = self._implementations.get(implementation_id)
            
            if not implementation:
                raise HTTPException(status_code=404, detail=f"Policy implementation with ID {implementation_id} not found")
            
            return self._policy_implementation_to_dict(implementation)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting policy implementation: {str(e)}")
    
    async def get_implementations_by_policy(
        self,
        policy_id: str = Path(..., description="ID of the policy")
    ) -> List[Dict[str, Any]]:
        """
        Get all implementations for a specific policy.
        
        Args:
            policy_id: The ID of the policy
            
        Returns:
            List of policy implementations
        """
        try:
            # Check if policy exists
            if policy_id not in self._policies:
                raise HTTPException(status_code=404, detail=f"Policy with ID {policy_id} not found")
            
            implementations = [i for i in self._implementations.values() if i.policy_id == policy_id]
            
            return [self._policy_implementation_to_dict(i) for i in implementations]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting implementations by policy: {str(e)}")
    
    # Impact assessment endpoints
    
    async def assess_policy_impact(self, assessment_request: ImpactAssessmentRequest) -> Dict[str, Any]:
        """
        Assess the impact of a policy.
        
        Args:
            assessment_request: The impact assessment request
            
        Returns:
            Impact assessment results
        """
        try:
            # Check if policy exists
            if assessment_request.policy_id not in self._policies:
                raise HTTPException(status_code=404, detail=f"Policy with ID {assessment_request.policy_id} not found")
            
            policy = self._policies[assessment_request.policy_id]
            
            # Convert geometry model to shapely geometry
            spatial_extent = self._geometry_from_model(assessment_request.spatial_extent)
            
            # This would be a real impact assessment in a production implementation
            # For now, generate a mock response
            assessment_id = f"impact-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            assessment_date = assessment_request.assessment_date or datetime.datetime.now()
            
            # Generate mock assessment results based on type
            if assessment_request.assessment_type == "environmental":
                metrics = {
                    "water_quality_improvement": {"value": 25, "unit": "percent"},
                    "carbon_sequestration": {"value": 150, "unit": "tons/year"},
                    "habitat_improvement": {"value": 18, "unit": "hectares"}
                }
            elif assessment_request.assessment_type == "economic":
                metrics = {
                    "implementation_cost": {"value": 750000, "unit": "USD"},
                    "economic_benefit": {"value": 1250000, "unit": "USD"},
                    "jobs_created": {"value": 45, "unit": "jobs"},
                    "return_on_investment": {"value": 1.67, "unit": "ratio"}
                }
            elif assessment_request.assessment_type == "social":
                metrics = {
                    "community_engagement": {"value": 85, "unit": "percent"},
                    "equity_distribution": {"value": 0.72, "unit": "index"},
                    "public_health_benefit": {"value": "moderate", "unit": "qualitative"},
                    "quality_of_life_improvement": {"value": 18, "unit": "percent"}
                }
            else:
                metrics = {"status": "unknown assessment type"}
            
            assessment_result = {
                "assessment_id": assessment_id,
                "policy_id": policy.id,
                "policy_name": policy.name,
                "assessment_type": assessment_request.assessment_type,
                "assessment_date": assessment_date.isoformat(),
                "metrics": metrics,
                "parameters": assessment_request.parameters,
                "spatial_extent": assessment_request.spatial_extent,
                "conclusion": f"The {policy.name} policy is projected to have significant positive impacts in the assessed area."
            }
            
            return {
                "status": "success",
                "message": "Policy impact assessment completed",
                "assessment": assessment_result
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error assessing policy impact: {str(e)}")
    
    async def get_impact_assessment_history(
        self,
        policy_id: str = Path(..., description="ID of the policy")
    ) -> List[Dict[str, Any]]:
        """
        Get the history of impact assessments for a policy.
        
        Args:
            policy_id: The ID of the policy
            
        Returns:
            List of impact assessments
        """
        try:
            # Check if policy exists
            if policy_id not in self._policies:
                raise HTTPException(status_code=404, detail=f"Policy with ID {policy_id} not found")
            
            # This would query a database of assessments in a real implementation
            # For now, return a mock response
            policy = self._policies[policy_id]
            
            # Mock assessment history
            assessments = [
                {
                    "assessment_id": f"impact-{policy_id}-20230301",
                    "policy_id": policy_id,
                    "assessment_type": "environmental",
                    "assessment_date": "2023-03-01T00:00:00Z",
                    "summary": "Initial environmental impact assessment",
                    "metrics": {
                        "water_quality_improvement": {"value": 20, "unit": "percent"},
                        "carbon_sequestration": {"value": 120, "unit": "tons/year"}
                    }
                },
                {
                    "assessment_id": f"impact-{policy_id}-20230615",
                    "policy_id": policy_id,
                    "assessment_type": "economic",
                    "assessment_date": "2023-06-15T00:00:00Z",
                    "summary": "Mid-year economic impact assessment",
                    "metrics": {
                        "implementation_cost": {"value": 350000, "unit": "USD"},
                        "economic_benefit": {"value": 580000, "unit": "USD"}
                    }
                }
            ]
            
            return assessments
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting impact assessment history: {str(e)}")
    
    # Regulatory comparison endpoints
    
    async def compare_regulations(self, comparison_request: RegulationComparisonRequest) -> Dict[str, Any]:
        """
        Compare multiple regulations.
        
        Args:
            comparison_request: The regulation comparison request
            
        Returns:
            Comparison results
        """
        try:
            # This would be implemented by querying regulation data in a real implementation
            # For now, return a mock response
            
            # Create mock comparison results
            comparison_id = f"comp-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Generate mock data for each regulation
            regulations_data = []
            for i, reg_id in enumerate(comparison_request.regulation_ids):
                reg_data = {
                    "regulation_id": reg_id,
                    "name": f"Regulation {i+1}",
                    "metrics": {}
                }
                
                # Generate metrics data
                for metric in comparison_request.comparison_metrics:
                    if metric == "compliance_cost":
                        reg_data["metrics"][metric] = 75000 + i * 25000
                    elif metric == "environmental_benefit":
                        reg_data["metrics"][metric] = 8.5 - i * 1.5
                    elif metric == "implementation_timeline":
                        reg_data["metrics"][metric] = 12 + i * 6
                    else:
                        reg_data["metrics"][metric] = f"Value for {metric}"
                
                regulations_data.append(reg_data)
            
            # Create comparison summary
            metrics_summary = {}
            for metric in comparison_request.comparison_metrics:
                if metric == "compliance_cost":
                    best_reg = min(regulations_data, key=lambda r: r["metrics"][metric])
                    metrics_summary[metric] = {
                        "best_regulation": best_reg["regulation_id"],
                        "range": [
                            min(r["metrics"][metric] for r in regulations_data),
                            max(r["metrics"][metric] for r in regulations_data)
                        ],
                        "unit": "USD"
                    }
                elif metric == "environmental_benefit":
                    best_reg = max(regulations_data, key=lambda r: r["metrics"][metric])
                    metrics_summary[metric] = {
                        "best_regulation": best_reg["regulation_id"],
                        "range": [
                            min(r["metrics"][metric] for r in regulations_data),
                            max(r["metrics"][metric] for r in regulations_data)
                        ],
                        "unit": "index (0-10)"
                    }
                elif metric == "implementation_timeline":
                    best_reg = min(regulations_data, key=lambda r: r["metrics"][metric])
                    metrics_summary[metric] = {
                        "best_regulation": best_reg["regulation_id"],
                        "range": [
                            min(r["metrics"][metric] for r in regulations_data),
                            max(r["metrics"][metric] for r in regulations_data)
                        ],
                        "unit": "months"
                    }
            
            return {
                "status": "success",
                "message": "Regulation comparison completed",
                "comparison_id": comparison_id,
                "regulations": regulations_data,
                "metrics_summary": metrics_summary,
                "jurisdiction_id": comparison_request.jurisdiction_id,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error comparing regulations: {str(e)}")
    
    # Export endpoints
    
    async def export_to_geojson(
        self,
        policy_id: Optional[str] = Query(None, description="Filter by policy ID"),
        status: Optional[str] = Query(None, description="Filter by implementation status")
    ) -> Dict[str, Any]:
        """
        Export policy implementations to GeoJSON.
        
        Args:
            policy_id: Optional policy ID to filter by
            status: Optional implementation status to filter by
            
        Returns:
            GeoJSON data
        """
        try:
            # Filter implementations
            implementations = list(self._implementations.values())
            
            if policy_id:
                implementations = [i for i in implementations if i.policy_id == policy_id]
            
            if status:
                implementations = [i for i in implementations if i.status == status]
            
            # Create GeoDataFrame
            data = []
            for impl in implementations:
                if impl.geometry is not None:
                    # Get policy name
                    policy = self._policies.get(impl.policy_id)
                    policy_name = policy.name if policy else "Unknown policy"
                    
                    data.append({
                        'id': impl.id,
                        'name': impl.name,
                        'policy_id': impl.policy_id,
                        'policy_name': policy_name,
                        'jurisdiction_id': impl.jurisdiction_id,
                        'status': impl.status,
                        'budget': impl.budget,
                        'start_date': impl.start_date.isoformat() if impl.start_date else None,
                        'end_date': impl.end_date.isoformat() if impl.end_date else None,
                        'geometry': impl.geometry
                    })
            
            if not data:
                return {
                    "status": "warning",
                    "message": "No policy implementations with geometry found for GeoJSON export",
                    "geojson": None
                }
            
            gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")
            
            # Convert to GeoJSON
            geojson = json.loads(gdf.to_json())
            
            return {
                "status": "success",
                "message": "Policy implementations exported to GeoJSON successfully",
                "feature_count": len(geojson["features"]),
                "geojson": geojson
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error exporting to GeoJSON: {str(e)}") 