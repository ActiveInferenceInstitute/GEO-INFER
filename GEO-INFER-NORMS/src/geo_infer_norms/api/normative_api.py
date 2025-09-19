"""
Normative API module for inferring, analyzing, and simulating social norms.

This module provides API endpoints for working with the normative inference system
to analyze, model, and predict the diffusion of social norms across geographies.
"""

from typing import Dict, List, Optional, Union, Any
import datetime
from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends
from pydantic import BaseModel, Field
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon, shape
import json
from shapely.geometry.base import BaseGeometry

from geo_infer_norms.core.normative_inference import NormativeInference, SocialNormDiffusion


# Pydantic models for API request/response
class GeometryModel(BaseModel):
    """Model for GeoJSON geometry data"""
    type: str
    coordinates: Any
    
    class Config:
        arbitrary_types_allowed = True


class SocialNormCreate(BaseModel):
    """Request model for creating a social norm"""
    name: str = Field(..., description="Name of the social norm")
    description: Optional[str] = Field(None, description="Description of the norm")
    category: str = Field(..., description="Category of norm (e.g., environmental, health, etc.)")
    strength: float = Field(..., ge=0.0, le=1.0, description="Initial strength of the norm (0.0 to 1.0)")
    jurisdiction_ids: List[str] = Field(..., description="IDs of jurisdictions where this norm applies")
    factors: Optional[Dict[str, float]] = Field(None, description="Factors that influence norm strength")
    related_policies: Optional[List[str]] = Field(None, description="IDs of related policies")
    tags: Optional[List[str]] = Field(None, description="Tags for the norm")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Recycling Behavior",
                "description": "Social norm around household recycling behavior",
                "category": "environmental",
                "strength": 0.65,
                "jurisdiction_ids": ["city-001", "city-002"],
                "factors": {
                    "infrastructure_access": 0.8,
                    "public_education": 0.7,
                    "peer_pressure": 0.6
                },
                "related_policies": ["policy-001"],
                "tags": ["recycling", "waste", "environmental"]
            }
        }


class NormDiffusionRequest(BaseModel):
    """Request model for social norm diffusion simulation"""
    norm_id: str = Field(..., description="ID of the norm to simulate")
    time_steps: int = Field(..., gt=0, description="Number of time steps to simulate")
    initial_conditions: Optional[Dict[str, Any]] = Field(None, description="Initial conditions for simulation")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Simulation parameters")
    spatial_extent: Optional[GeometryModel] = Field(None, description="GeoJSON geometry of simulation area")
    
    class Config:
        schema_extra = {
            "example": {
                "norm_id": "norm-001",
                "time_steps": 20,
                "initial_conditions": {
                    "seed_jurisdictions": ["city-001"],
                    "initial_strength": 0.8
                },
                "parameters": {
                    "diffusion_rate": 0.1,
                    "decay_rate": 0.02,
                    "influence_distance": 50000  # meters
                },
                "spatial_extent": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
                }
            }
        }


class NormativeInferenceRequest(BaseModel):
    """Request model for normative inference from data"""
    data_source: str = Field(..., description="Source of data for inference")
    inference_type: str = Field(..., description="Type of inference to perform")
    spatial_extent: Optional[GeometryModel] = Field(None, description="GeoJSON geometry of inference area")
    temporal_range: Optional[Dict[str, str]] = Field(None, description="Temporal range for inference")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Inference parameters")
    
    class Config:
        schema_extra = {
            "example": {
                "data_source": "survey_responses",
                "inference_type": "bayesian",
                "spatial_extent": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
                },
                "temporal_range": {
                    "start_date": "2022-01-01",
                    "end_date": "2022-12-31"
                },
                "parameters": {
                    "confidence_threshold": 0.7,
                    "prior_strength": 0.5,
                    "included_factors": ["income", "education", "age"]
                }
            }
        }


class NormPolicyImpactRequest(BaseModel):
    """Request model for assessing policy impact on norms"""
    norm_id: str = Field(..., description="ID of the norm to assess")
    policy_id: str = Field(..., description="ID of the policy to assess")
    time_horizon: int = Field(..., gt=0, description="Time horizon for assessment (in months)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Assessment parameters")
    
    class Config:
        schema_extra = {
            "example": {
                "norm_id": "norm-001",
                "policy_id": "policy-001",
                "time_horizon": 24,
                "parameters": {
                    "policy_effectiveness": 0.7,
                    "public_awareness": 0.6,
                    "enforcement_level": 0.8
                }
            }
        }


class PointLocation(BaseModel):
    """Model for a geographic point location"""
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude")
    lon: float = Field(..., ge=-180.0, le=180.0, description="Longitude")


class NormativeAPI:
    """API for normative inference and social norm analysis"""
    
    def __init__(
        self, 
        normative_inference: Optional[NormativeInference] = None,
        social_norm_diffusion: Optional[SocialNormDiffusion] = None
    ):
        """
        Initialize the NormativeAPI.
        
        Args:
            normative_inference: Optional NormativeInference instance to use
            social_norm_diffusion: Optional SocialNormDiffusion instance to use
        """
        self.normative_inference = normative_inference or NormativeInference()
        self.social_norm_diffusion = social_norm_diffusion or SocialNormDiffusion()
        self.router = APIRouter()
        self._setup_routes()
        
        # Temporary storage for social norms
        self._social_norms = {}
    
    def _setup_routes(self) -> None:
        """Set up API routes"""
        # Social norm endpoints
        self.router.post("/norms", response_model=Dict[str, Any])(self.create_social_norm)
        self.router.get("/norms", response_model=List[Dict[str, Any]])(self.list_social_norms)
        self.router.get("/norms/{norm_id}", response_model=Dict[str, Any])(self.get_social_norm)
        
        # Norm diffusion endpoints
        self.router.post("/diffusion/simulate", response_model=Dict[str, Any])(self.simulate_norm_diffusion)
        self.router.get("/diffusion/factors/{norm_id}", response_model=Dict[str, Any])(self.get_diffusion_factors)
        
        # Normative inference endpoints
        self.router.post("/inference/analyze", response_model=Dict[str, Any])(self.perform_normative_inference)
        self.router.post("/inference/spatial-patterns", response_model=Dict[str, Any])(self.analyze_spatial_patterns)
        
        # Policy impact endpoints
        self.router.post("/policy-impact", response_model=Dict[str, Any])(self.assess_policy_impact)
        
        # Spatial query endpoints
        self.router.post("/spatial/norms-at-point", response_model=List[Dict[str, Any]])(self.get_norms_at_point)
        
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
    
    def _social_norm_to_dict(self, norm: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a social norm to a dictionary for API response.
        
        Args:
            norm: Social norm dictionary
            
        Returns:
            Dictionary representation
        """
        return {
            "id": norm["id"],
            "name": norm["name"],
            "description": norm["description"],
            "category": norm["category"],
            "strength": norm["strength"],
            "jurisdiction_ids": norm["jurisdiction_ids"],
            "factors": norm["factors"],
            "related_policies": norm["related_policies"],
            "tags": norm["tags"],
            "created_at": norm["created_at"]
        }
    
    # Social norm endpoints
    
    async def create_social_norm(self, norm_data: SocialNormCreate) -> Dict[str, Any]:
        """
        Create a new social norm.
        
        Args:
            norm_data: The social norm data
            
        Returns:
            Success message with norm ID
        """
        try:
            # Create norm object
            norm_id = f"norm-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            norm = {
                "id": norm_id,
                "name": norm_data.name,
                "description": norm_data.description or "",
                "category": norm_data.category,
                "strength": norm_data.strength,
                "jurisdiction_ids": norm_data.jurisdiction_ids,
                "factors": norm_data.factors or {},
                "related_policies": norm_data.related_policies or [],
                "tags": norm_data.tags or [],
                "created_at": datetime.datetime.now().isoformat()
            }
            
            # Store norm
            self._social_norms[norm_id] = norm
            
            return {
                "status": "success",
                "message": "Social norm created successfully",
                "norm_id": norm_id
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating social norm: {str(e)}")
    
    async def list_social_norms(
        self,
        category: Optional[str] = Query(None, description="Filter by category"),
        jurisdiction_id: Optional[str] = Query(None, description="Filter by jurisdiction ID"),
        tag: Optional[str] = Query(None, description="Filter by tag"),
        min_strength: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum strength")
    ) -> List[Dict[str, Any]]:
        """
        List all social norms, optionally filtered.
        
        Args:
            category: Optional category to filter by
            jurisdiction_id: Optional jurisdiction ID to filter by
            tag: Optional tag to filter by
            min_strength: Optional minimum strength to filter by
            
        Returns:
            List of social norms
        """
        try:
            norms = list(self._social_norms.values())
            
            if category:
                norms = [n for n in norms if n["category"] == category]
            
            if jurisdiction_id:
                norms = [n for n in norms if jurisdiction_id in n["jurisdiction_ids"]]
            
            if tag:
                norms = [n for n in norms if tag in n["tags"]]
            
            if min_strength is not None:
                norms = [n for n in norms if n["strength"] >= min_strength]
            
            return [self._social_norm_to_dict(n) for n in norms]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error listing social norms: {str(e)}")
    
    async def get_social_norm(
        self,
        norm_id: str = Path(..., description="ID of the social norm")
    ) -> Dict[str, Any]:
        """
        Get a social norm by ID.
        
        Args:
            norm_id: The ID of the social norm
            
        Returns:
            Social norm details
        """
        try:
            norm = self._social_norms.get(norm_id)
            
            if not norm:
                raise HTTPException(status_code=404, detail=f"Social norm with ID {norm_id} not found")
            
            return self._social_norm_to_dict(norm)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting social norm: {str(e)}")
    
    # Norm diffusion endpoints
    
    async def simulate_norm_diffusion(self, diffusion_request: NormDiffusionRequest) -> Dict[str, Any]:
        """
        Simulate the diffusion of a social norm over time.
        
        Args:
            diffusion_request: The norm diffusion request
            
        Returns:
            Diffusion simulation results
        """
        try:
            # Check if norm exists
            if diffusion_request.norm_id not in self._social_norms:
                raise HTTPException(status_code=404, detail=f"Social norm with ID {diffusion_request.norm_id} not found")
            
            norm = self._social_norms[diffusion_request.norm_id]
            
            # Convert geometry model to shapely geometry
            spatial_extent = self._geometry_from_model(diffusion_request.spatial_extent)
            
            # This would be a real simulation in a production implementation
            # For now, generate a mock response
            
            # Generate mock time series data
            time_series = []
            initial_strength = norm["strength"]
            diffusion_rate = diffusion_request.parameters.get("diffusion_rate", 0.1) if diffusion_request.parameters else 0.1
            decay_rate = diffusion_request.parameters.get("decay_rate", 0.02) if diffusion_request.parameters else 0.02
            
            # Simple logistic growth model
            for t in range(diffusion_request.time_steps + 1):
                # Simple model: strength grows logistically but with some decay
                strength = initial_strength + (1 - initial_strength) * (1 - 1 / (1 + diffusion_rate * t)) - decay_rate * t / diffusion_request.time_steps
                strength = max(0, min(1, strength))  # Ensure bounds of [0, 1]
                
                time_series.append({
                    "time_step": t,
                    "strength": strength,
                    "spread": initial_strength + (t / diffusion_request.time_steps) * (1 - initial_strength) * 0.8  # Spread as % of jurisdictions
                })
            
            # Generate mock spatial data
            jurisdictions = [
                {"id": jid, "name": f"Jurisdiction {i+1}", "initial_strength": initial_strength * (0.8 + 0.4 * (i / len(norm["jurisdiction_ids"])))}
                for i, jid in enumerate(norm["jurisdiction_ids"])
            ]
            
            return {
                "status": "success",
                "message": "Norm diffusion simulation completed",
                "norm_id": norm["id"],
                "norm_name": norm["name"],
                "time_steps": diffusion_request.time_steps,
                "time_series": time_series,
                "jurisdictions": jurisdictions,
                "parameters": diffusion_request.parameters or {},
                "final_strength": time_series[-1]["strength"],
                "final_spread": time_series[-1]["spread"]
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error simulating norm diffusion: {str(e)}")
    
    async def get_diffusion_factors(
        self,
        norm_id: str = Path(..., description="ID of the social norm")
    ) -> Dict[str, Any]:
        """
        Get the factors that influence the diffusion of a social norm.
        
        Args:
            norm_id: The ID of the social norm
            
        Returns:
            Diffusion factors
        """
        try:
            # Check if norm exists
            if norm_id not in self._social_norms:
                raise HTTPException(status_code=404, detail=f"Social norm with ID {norm_id} not found")
            
            norm = self._social_norms[norm_id]
            
            # In a real implementation, this would analyze various factors
            # For now, return factors from the norm plus some additional analysis
            
            norm_factors = norm["factors"] or {}
            
            # Add some additional mock analysis
            factor_analysis = {
                "geographic_proximity": {
                    "importance": 0.85,
                    "description": "The influence of geographic proximity on norm diffusion",
                    "effect": "Strong positive effect on diffusion speed"
                },
                "social_networks": {
                    "importance": 0.75,
                    "description": "The influence of social networks on norm diffusion",
                    "effect": "Moderate positive effect on diffusion breadth"
                },
                "institutional_support": {
                    "importance": 0.65,
                    "description": "The influence of institutional support on norm sustainability",
                    "effect": "Strong positive effect on norm stability"
                }
            }
            
            # Include original factors
            for factor, value in norm_factors.items():
                if factor not in factor_analysis:
                    factor_analysis[factor] = {
                        "importance": value,
                        "description": f"User-defined factor: {factor}",
                        "effect": "Effect undetermined"
                    }
            
            return {
                "status": "success",
                "norm_id": norm_id,
                "norm_name": norm["name"],
                "factors": factor_analysis,
                "overall_diffusion_potential": sum(f["importance"] for f in factor_analysis.values()) / len(factor_analysis) if factor_analysis else 0
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting diffusion factors: {str(e)}")
    
    # Normative inference endpoints
    
    async def perform_normative_inference(self, inference_request: NormativeInferenceRequest) -> Dict[str, Any]:
        """
        Perform normative inference from data.
        
        Args:
            inference_request: The normative inference request
            
        Returns:
            Inference results
        """
        try:
            # Convert geometry model to shapely geometry
            spatial_extent = self._geometry_from_model(inference_request.spatial_extent)
            
            # This would be a real inference in a production implementation
            # For now, generate a mock response
            
            # Generate mock inferred norms based on inference type
            inferred_norms = []
            
            if inference_request.inference_type == "bayesian":
                # Mock Bayesian inference results
                inferred_norms = [
                    {
                        "name": "Environmental Conservation",
                        "inferred_strength": 0.72,
                        "confidence": 0.85,
                        "factors": {
                            "education_level": 0.65,
                            "income": 0.45,
                            "age": -0.20
                        },
                        "spatial_variation": "moderate"
                    },
                    {
                        "name": "Public Health Compliance",
                        "inferred_strength": 0.68,
                        "confidence": 0.78,
                        "factors": {
                            "education_level": 0.70,
                            "income": 0.30,
                            "age": 0.25
                        },
                        "spatial_variation": "low"
                    }
                ]
            elif inference_request.inference_type == "frequentist":
                # Mock frequentist inference results
                inferred_norms = [
                    {
                        "name": "Community Participation",
                        "inferred_strength": 0.54,
                        "p_value": 0.01,
                        "factors": {
                            "population_density": 0.40,
                            "community_age": 0.65
                        },
                        "spatial_variation": "high"
                    }
                ]
            else:
                # Generic mock inference
                inferred_norms = [
                    {
                        "name": "Generic Social Norm",
                        "inferred_strength": 0.60,
                        "confidence": 0.70,
                        "factors": {},
                        "spatial_variation": "unknown"
                    }
                ]
            
            return {
                "status": "success",
                "message": "Normative inference completed",
                "data_source": inference_request.data_source,
                "inference_type": inference_request.inference_type,
                "temporal_range": inference_request.temporal_range,
                "parameters": inference_request.parameters,
                "inferred_norms": inferred_norms,
                "inference_id": f"infer-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error performing normative inference: {str(e)}")
    
    async def analyze_spatial_patterns(self, inference_request: NormativeInferenceRequest) -> Dict[str, Any]:
        """
        Analyze spatial patterns of social norms.
        
        Args:
            inference_request: The normative inference request
            
        Returns:
            Spatial pattern analysis results
        """
        try:
            # Convert geometry model to shapely geometry
            spatial_extent = self._geometry_from_model(inference_request.spatial_extent)
            
            # This would be a real spatial analysis in a production implementation
            # For now, generate a mock response
            
            # Generate mock spatial analysis
            
            return {
                "status": "success",
                "message": "Spatial pattern analysis completed",
                "data_source": inference_request.data_source,
                "spatial_patterns": [
                    {
                        "pattern_type": "cluster",
                        "description": "High-strength norm clusters in urban areas",
                        "spatial_autocorrelation": 0.65,
                        "hotspots": [
                            {"name": "Downtown Area", "strength": 0.82},
                            {"name": "University District", "strength": 0.78}
                        ],
                        "coldspots": [
                            {"name": "Industrial Zone", "strength": 0.32},
                            {"name": "Rural Periphery", "strength": 0.45}
                        ]
                    },
                    {
                        "pattern_type": "gradient",
                        "description": "Strength decreases with distance from city center",
                        "gradient_direction": "center to periphery",
                        "gradient_strength": 0.58
                    }
                ],
                "analysis_id": f"spatial-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error analyzing spatial patterns: {str(e)}")
    
    # Policy impact endpoints
    
    async def assess_policy_impact(self, impact_request: NormPolicyImpactRequest) -> Dict[str, Any]:
        """
        Assess the impact of a policy on a social norm.
        
        Args:
            impact_request: The policy impact assessment request
            
        Returns:
            Impact assessment results
        """
        try:
            # Check if norm exists
            if impact_request.norm_id not in self._social_norms:
                raise HTTPException(status_code=404, detail=f"Social norm with ID {impact_request.norm_id} not found")
            
            norm = self._social_norms[impact_request.norm_id]
            
            # This would be a real impact assessment in a production implementation
            # For now, generate a mock response
            
            # Extract parameters
            effectiveness = impact_request.parameters.get("policy_effectiveness", 0.5) if impact_request.parameters else 0.5
            awareness = impact_request.parameters.get("public_awareness", 0.5) if impact_request.parameters else 0.5
            enforcement = impact_request.parameters.get("enforcement_level", 0.5) if impact_request.parameters else 0.5
            
            # Generate impact projections
            time_points = [0, 6, 12, 18, 24]
            if impact_request.time_horizon <= 24:
                time_points = [t for t in time_points if t <= impact_request.time_horizon]
                if impact_request.time_horizon not in time_points:
                    time_points.append(impact_request.time_horizon)
            else:
                step = impact_request.time_horizon // 5
                time_points = [i * step for i in range(6)]
            
            initial_strength = norm["strength"]
            
            # Simple model for impact
            combined_effect = (effectiveness + awareness + enforcement) / 3
            impact_projections = []
            
            for t in time_points:
                # Sigmoid growth curve with max at combined_effect
                relative_t = t / impact_request.time_horizon
                if relative_t == 0:
                    impact = 0
                else:
                    # S-curve: slow start, accelerate, then plateau
                    impact = combined_effect * (1 / (1 + np.exp(-10 * (relative_t - 0.5))))
                
                new_strength = min(1.0, initial_strength + impact * (1 - initial_strength))
                
                impact_projections.append({
                    "time_point": t,  # months
                    "norm_strength": new_strength,
                    "impact": new_strength - initial_strength
                })
            
            return {
                "status": "success",
                "message": "Policy impact assessment completed",
                "norm_id": norm["id"],
                "norm_name": norm["name"],
                "policy_id": impact_request.policy_id,
                "time_horizon": impact_request.time_horizon,
                "initial_strength": initial_strength,
                "final_strength": impact_projections[-1]["norm_strength"],
                "max_impact": max(p["impact"] for p in impact_projections),
                "impact_projections": impact_projections,
                "key_factors": {
                    "policy_effectiveness": effectiveness,
                    "public_awareness": awareness,
                    "enforcement_level": enforcement,
                    "combined_effect": combined_effect
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error assessing policy impact: {str(e)}")
    
    # Spatial query endpoints
    
    async def get_norms_at_point(self, point: PointLocation) -> List[Dict[str, Any]]:
        """
        Get all social norms that apply to a specific geographic point.
        
        Args:
            point: Geographic point location
            
        Returns:
            List of applicable social norms
        """
        try:
            # This would be implemented with spatial queries in a real implementation
            # For now, return a subset of norms
            
            # Mock implementation - return all norms
            norms = list(self._social_norms.values())
            
            # In reality, we would filter by jurisdictions that contain the point
            return [self._social_norm_to_dict(n) for n in norms]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting norms at point: {str(e)}")
    
    # Export endpoints
    
    async def export_to_geojson(
        self,
        category: Optional[str] = Query(None, description="Filter by category"),
        min_strength: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum strength")
    ) -> Dict[str, Any]:
        """
        Export social norm spatial distribution to GeoJSON.
        
        Args:
            category: Optional category to filter by
            min_strength: Optional minimum strength to filter by
            
        Returns:
            GeoJSON data
        """
        try:
            # This would create a proper GeoJSON with real jurisdictions in a production implementation
            # For now, generate a mock response
            
            # Filter norms
            norms = list(self._social_norms.values())
            
            if category:
                norms = [n for n in norms if n["category"] == category]
            
            if min_strength is not None:
                norms = [n for n in norms if n["strength"] >= min_strength]
            
            # Create mock features for each jurisdiction with norm data
            features = []
            
            for norm in norms:
                for i, jid in enumerate(norm["jurisdiction_ids"]):
                    # Create a simple square as mock geometry for each jurisdiction
                    center_x = i * 0.2
                    center_y = i * 0.2
                    coords = [
                        [[center_x - 0.1, center_y - 0.1],
                         [center_x + 0.1, center_y - 0.1],
                         [center_x + 0.1, center_y + 0.1],
                         [center_x - 0.1, center_y + 0.1],
                         [center_x - 0.1, center_y - 0.1]]
                    ]
                    
                    features.append({
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": coords
                        },
                        "properties": {
                            "jurisdiction_id": jid,
                            "jurisdiction_name": f"Jurisdiction {i+1}",
                            "norm_id": norm["id"],
                            "norm_name": norm["name"],
                            "norm_strength": norm["strength"],
                            "norm_category": norm["category"]
                        }
                    })
            
            geojson = {
                "type": "FeatureCollection",
                "features": features
            }
            
            return {
                "status": "success",
                "message": "Social norms exported to GeoJSON successfully",
                "feature_count": len(features),
                "geojson": geojson
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error exporting to GeoJSON: {str(e)}") 