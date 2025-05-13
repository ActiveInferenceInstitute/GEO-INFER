"""
Tests for the legal frameworks functionality in the GEO-INFER-NORMS module.

This module tests the LegalFramework and JurisdictionHandler classes and their methods
for managing legal frameworks and jurisdictions.
"""

import pytest
from shapely.geometry import Point, Polygon, MultiPolygon
import geopandas as gpd
import datetime

from geo_infer_norms.core.legal_frameworks import LegalFramework, JurisdictionHandler
from geo_infer_norms.models.legal_entity import Jurisdiction
from geo_infer_norms.models.regulation import Regulation


class TestJurisdictionHandler:
    """Test cases for the JurisdictionHandler class."""
    
    def setup_method(self):
        """Set up test data for each test."""
        # Create test jurisdictions with simple geometries
        self.country = Jurisdiction(
            id="jur1",
            name="Test Country",
            level="federal",
            code="TC",
            geometry=MultiPolygon([Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])])
        )
        
        self.state = Jurisdiction(
            id="jur2",
            name="Test State",
            level="state",
            code="TS",
            parent_id="jur1",
            geometry=MultiPolygon([Polygon([(2, 2), (2, 8), (8, 8), (8, 2), (2, 2)])])
        )
        
        self.county = Jurisdiction(
            id="jur3",
            name="Test County",
            level="county",
            parent_id="jur2",
            geometry=MultiPolygon([Polygon([(3, 3), (3, 7), (7, 7), (7, 3), (3, 3)])])
        )
        
        self.city = Jurisdiction(
            id="jur4",
            name="Test City",
            level="city",
            parent_id="jur3",
            geometry=MultiPolygon([Polygon([(4, 4), (4, 6), (6, 6), (6, 4), (4, 4)])])
        )
        
        # Initialize the JurisdictionHandler with the test data
        self.handler = JurisdictionHandler([
            self.country,
            self.state,
            self.county,
            self.city
        ])
    
    def test_get_jurisdiction_by_id(self):
        """Test retrieving a jurisdiction by ID."""
        jurisdiction = self.handler.get_jurisdiction_by_id("jur1")
        assert jurisdiction == self.country
        
        jurisdiction = self.handler.get_jurisdiction_by_id("nonexistent")
        assert jurisdiction is None
    
    def test_get_jurisdiction_hierarchy(self):
        """Test retrieving the hierarchy chain of jurisdictions."""
        # Test city's hierarchy
        hierarchy = self.handler.get_jurisdiction_hierarchy("jur4")
        assert len(hierarchy) == 4
        assert hierarchy[0].id == "jur4"  # City
        assert hierarchy[1].id == "jur3"  # County
        assert hierarchy[2].id == "jur2"  # State
        assert hierarchy[3].id == "jur1"  # Country
        
        # Test state's hierarchy
        hierarchy = self.handler.get_jurisdiction_hierarchy("jur2")
        assert len(hierarchy) == 2
        assert hierarchy[0].id == "jur2"  # State
        assert hierarchy[1].id == "jur1"  # Country
        
        # Test nonexistent jurisdiction
        hierarchy = self.handler.get_jurisdiction_hierarchy("nonexistent")
        assert len(hierarchy) == 0
    
    def test_find_jurisdictions_by_name(self):
        """Test finding jurisdictions by name."""
        # Exact match
        jurisdictions = self.handler.find_jurisdictions_by_name("Test State")
        assert len(jurisdictions) == 1
        assert jurisdictions[0].id == "jur2"
        
        # Partial match
        jurisdictions = self.handler.find_jurisdictions_by_name("Test", partial_match=True)
        assert len(jurisdictions) == 4
        
        # No match
        jurisdictions = self.handler.find_jurisdictions_by_name("Nonexistent")
        assert len(jurisdictions) == 0
    
    def test_find_jurisdictions_at_level(self):
        """Test finding jurisdictions at a specific level."""
        # Federal level
        jurisdictions = self.handler.find_jurisdictions_at_level("federal")
        assert len(jurisdictions) == 1
        assert jurisdictions[0].id == "jur1"
        
        # State level
        jurisdictions = self.handler.find_jurisdictions_at_level("state")
        assert len(jurisdictions) == 1
        assert jurisdictions[0].id == "jur2"
        
        # Nonexistent level
        jurisdictions = self.handler.find_jurisdictions_at_level("nonexistent")
        assert len(jurisdictions) == 0
    
    def test_get_overlapping_jurisdictions(self):
        """Test finding jurisdictions that overlap with a geometry."""
        # Point in the city
        point = Point(5, 5)
        jurisdictions = self.handler.get_overlapping_jurisdictions(point)
        assert len(jurisdictions) == 4
        assert set(j.id for j in jurisdictions) == {"jur1", "jur2", "jur3", "jur4"}
        
        # Point in the county but outside the city
        point = Point(3.5, 3.5)
        jurisdictions = self.handler.get_overlapping_jurisdictions(point)
        assert len(jurisdictions) == 3
        assert set(j.id for j in jurisdictions) == {"jur1", "jur2", "jur3"}
        
        # Point outside all jurisdictions
        point = Point(15, 15)
        jurisdictions = self.handler.get_overlapping_jurisdictions(point)
        assert len(jurisdictions) == 0
        
        # Polygon overlapping multiple jurisdictions
        polygon = Polygon([(3, 3), (3, 5), (5, 5), (5, 3), (3, 3)])
        jurisdictions = self.handler.get_overlapping_jurisdictions(polygon)
        assert len(jurisdictions) == 4
    
    def test_create_jurisdiction_graph(self):
        """Test creating a graph representation of the jurisdictional hierarchy."""
        graph = self.handler.create_jurisdiction_graph()
        
        assert len(graph) == 4
        assert set(graph.keys()) == {"jur1", "jur2", "jur3", "jur4"}
        
        assert "jur2" in graph["jur1"]  # State is a child of Country
        assert "jur3" in graph["jur2"]  # County is a child of State
        assert "jur4" in graph["jur3"]  # City is a child of County
        assert graph["jur4"] == []      # City has no children
    
    def test_export_to_geodataframe(self):
        """Test exporting jurisdictions to a GeoDataFrame."""
        gdf = self.handler.export_to_geodataframe()
        
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) == 4
        assert set(gdf.columns) >= {'id', 'name', 'level', 'parent_id', 'geometry'}
        assert gdf.crs == "EPSG:4326"


class TestLegalFramework:
    """Test cases for the LegalFramework class."""
    
    def setup_method(self):
        """Set up test data for each test."""
        # Create test jurisdictions
        self.country = Jurisdiction(
            id="jur1",
            name="Test Country",
            level="federal",
            geometry=MultiPolygon([Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])])
        )
        
        self.state = Jurisdiction(
            id="jur2",
            name="Test State",
            level="state",
            parent_id="jur1",
            geometry=MultiPolygon([Polygon([(2, 2), (2, 8), (8, 8), (8, 2), (2, 2)])])
        )
        
        # Create test regulations
        self.federal_reg = Regulation(
            id="reg1",
            name="Federal Environmental Regulation",
            description="A federal environmental protection regulation",
            regulation_type="environmental",
            issuing_authority="EPA",
            effective_date=datetime.date(2020, 1, 1),
            applicable_jurisdictions=["jur1"]  # Applies to entire country
        )
        
        self.state_reg = Regulation(
            id="reg2",
            name="State Zoning Regulation",
            description="A state zoning regulation",
            regulation_type="zoning",
            issuing_authority="State Planning Department",
            effective_date=datetime.date(2019, 6, 1),
            applicable_jurisdictions=["jur2"]  # Applies only to the state
        )
        
        # Initialize the LegalFramework with the test data
        self.framework = LegalFramework(
            name="Test Legal Framework",
            description="A test framework for environmental and zoning regulations",
            jurisdictions=[self.country, self.state],
            regulations=[self.federal_reg, self.state_reg]
        )
    
    def test_add_jurisdiction(self):
        """Test adding a jurisdiction to the framework."""
        # Create a new jurisdiction
        city = Jurisdiction(
            id="jur3",
            name="Test City",
            level="city",
            parent_id="jur2",
            geometry=MultiPolygon([Polygon([(4, 4), (4, 6), (6, 6), (6, 4), (4, 4)])])
        )
        
        # Add it to the framework
        self.framework.add_jurisdiction(city)
        
        # Check that it was added correctly
        assert len(self.framework.jurisdictions) == 3
        assert self.framework._jurisdiction_index["jur3"] == city
    
    def test_add_regulation(self):
        """Test adding a regulation to the framework."""
        # Create a new regulation
        city_reg = Regulation(
            id="reg3",
            name="City Building Code",
            description="A city building code regulation",
            regulation_type="building",
            issuing_authority="City Building Department",
            effective_date=datetime.date(2021, 3, 15),
            applicable_jurisdictions=["jur3"]
        )
        
        # Add it to the framework
        self.framework.add_regulation(city_reg)
        
        # Check that it was added correctly
        assert len(self.framework.regulations) == 3
        assert self.framework._regulation_index["reg3"] == city_reg
    
    def test_get_regulations_by_jurisdiction(self):
        """Test retrieving regulations for a specific jurisdiction."""
        # Federal regulations apply to the country
        regs = self.framework.get_regulations_by_jurisdiction("jur1")
        assert len(regs) == 1
        assert regs[0].id == "reg1"
        
        # Both federal and state regulations apply to the state
        regs = self.framework.get_regulations_by_jurisdiction("jur2")
        assert len(regs) == 2
        assert set(r.id for r in regs) == {"reg1", "reg2"}
        
        # Nonexistent jurisdiction
        regs = self.framework.get_regulations_by_jurisdiction("nonexistent")
        assert len(regs) == 0
    
    def test_get_jurisdictions_by_point(self):
        """Test retrieving jurisdictions that contain a specific point."""
        # Point in both country and state
        point = Point(5, 5)
        jurisdictions = self.framework.get_jurisdictions_by_point(point)
        assert len(jurisdictions) == 2
        assert set(j.id for j in jurisdictions) == {"jur1", "jur2"}
        
        # Point in country but outside state
        point = Point(1, 1)
        jurisdictions = self.framework.get_jurisdictions_by_point(point)
        assert len(jurisdictions) == 1
        assert jurisdictions[0].id == "jur1"
        
        # Point outside all jurisdictions
        point = Point(15, 15)
        jurisdictions = self.framework.get_jurisdictions_by_point(point)
        assert len(jurisdictions) == 0
    
    def test_get_regulations_by_point(self):
        """Test retrieving regulations applicable to a specific point."""
        # Point in both country and state should have both regulations
        point = Point(5, 5)
        regs = self.framework.get_regulations_by_point(point)
        assert len(regs) == 2
        assert set(r.id for r in regs) == {"reg1", "reg2"}
        
        # Point in country but outside state should only have federal regulation
        point = Point(1, 1)
        regs = self.framework.get_regulations_by_point(point)
        assert len(regs) == 1
        assert regs[0].id == "reg1"
        
        # Point outside all jurisdictions should have no regulations
        point = Point(15, 15)
        regs = self.framework.get_regulations_by_point(point)
        assert len(regs) == 0
    
    def test_export_to_geodataframe(self):
        """Test exporting the framework's jurisdictions to a GeoDataFrame."""
        gdf = self.framework.export_to_geodataframe()
        
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) == 2
        assert set(gdf.columns) >= {'id', 'name', 'level', 'parent_id', 'geometry', 'regulation_count'}
        assert gdf.crs == "EPSG:4326"
        
        # The country should have 1 regulation
        country_row = gdf[gdf.id == "jur1"].iloc[0]
        assert country_row.regulation_count == 1
        
        # The state should have 2 regulations (its own plus inherited from country)
        state_row = gdf[gdf.id == "jur2"].iloc[0]
        assert state_row.regulation_count == 2 