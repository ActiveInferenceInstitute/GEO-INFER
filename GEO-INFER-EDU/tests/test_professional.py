"""Tests for professional development module."""

import pytest
from geo_infer_edu.core.professional import (
    ProfessionalDevelopment,
    ProfessionalProfile,
    CertificationPathway,
    ContinuingEducationActivity,
)


class TestProfessionalDataclasses:
    """Tests for professional dataclass creation."""

    def test_professional_profile_creation(self) -> None:
        profile = ProfessionalProfile(
            professional_id="p1",
            name="Jane Doe",
            current_role="GIS Analyst",
            years_experience=5,
            skills=["python", "arcgis"],
        )
        assert profile.years_experience == 5
        assert profile.continuing_education_credits == 0


class TestProfessionalDevelopmentInit:
    """Tests for ProfessionalDevelopment initialization."""

    def test_default_initialization(self) -> None:
        pd = ProfessionalDevelopment()
        assert pd is not None
        assert "gisp" in pd.certification_bodies
        assert pd.credit_tracking is True

    def test_register_professional(self) -> None:
        pd = ProfessionalDevelopment()
        profile = pd.register_professional({
            "id": "p1",
            "name": "John Smith",
            "role": "GIS Developer",
            "experience_years": 8,
            "skills": ["python", "javascript"],
            "certifications": ["gisp"],
        })
        assert profile.professional_id == "p1"
        assert profile.years_experience == 8
        assert "gisp" in profile.certifications


class TestContinuingEducation:
    """Tests for CE tracking."""

    def test_track_activities(self) -> None:
        pd = ProfessionalDevelopment()
        pd.register_professional({"id": "p1", "name": "Jane", "role": "Analyst"})

        result = pd.track_continuing_education(
            professional_id="p1",
            activities=[
                {"id": "ce1", "title": "GIS Workshop", "type": "workshop",
                 "provider": "Esri", "credits": 8, "category": "technical"},
                {"id": "ce2", "title": "Ethics Course", "type": "course",
                 "provider": "URISA", "credits": 4, "category": "ethics"},
            ],
        )
        assert result["activities_tracked"] == 2
        assert result["credits_added"] == 12
        assert result["total_credits"] == 12
        assert "technical" in result["by_category"]
        assert result["by_category"]["technical"] == 8

    def test_track_for_unknown_professional(self) -> None:
        pd = ProfessionalDevelopment()
        result = pd.track_continuing_education(
            professional_id="nonexistent",
            activities=[],
        )
        assert "error" in result


class TestCertificationPathway:
    """Tests for certification pathway creation."""

    def test_create_gisp_pathway(self) -> None:
        pd = ProfessionalDevelopment()
        pathway = pd.create_certification_pathway(
            target_certification="GISP",
            current_qualifications={
                "education_points": 15,
                "experience_years": 3,
                "contributions_points": 20,
            },
            timeline="12_months",
        )
        assert isinstance(pathway, CertificationPathway)
        assert pathway.target_certification == "GISP"
        assert 0 <= pathway.current_progress["education"] <= 1.0
        assert len(pathway.next_steps) > 0

    def test_fully_qualified_pathway(self) -> None:
        pd = ProfessionalDevelopment()
        pathway = pd.create_certification_pathway(
            target_certification="GISP",
            current_qualifications={
                "education_points": 50,
                "experience_years": 100,
                "contributions_points": 100,
            },
        )
        assert all(v >= 1.0 for v in pathway.current_progress.values())


class TestCareerSkillsAnalysis:
    """Tests for career skills analysis."""

    def test_analyze_skills_for_data_scientist(self) -> None:
        pd = ProfessionalDevelopment()
        analysis = pd.analyze_career_skills(
            current_skills=["spatial_analysis", "python", "statistics"],
            target_role="Geospatial Data Scientist",
        )
        assert analysis["match_percentage"] > 0
        assert analysis["gap_count"] > 0
        assert "machine_learning" in analysis["skill_gaps"]
        assert len(analysis["recommendations"]) > 0

    def test_analyze_skills_full_match(self) -> None:
        pd = ProfessionalDevelopment()
        analysis = pd.analyze_career_skills(
            current_skills=[
                "spatial_analysis", "machine_learning", "python",
                "statistics", "big_data", "cloud_computing", "deep_learning"
            ],
            target_role="Geospatial Data Scientist",
        )
        assert analysis["match_percentage"] == 100.0
        assert analysis["gap_count"] == 0

    def test_analyze_skills_unknown_role(self) -> None:
        pd = ProfessionalDevelopment()
        analysis = pd.analyze_career_skills(
            current_skills=["python"],
            target_role="Unknown Role",
        )
        assert analysis["match_percentage"] == 100.0  # No required skills for unknown role


class TestPortfolioDevelopment:
    """Tests for portfolio development."""

    def test_develop_portfolio(self) -> None:
        pd = ProfessionalDevelopment()
        portfolio = pd.develop_portfolio(
            projects=[
                {"id": "p1", "title": "Flood Analysis", "description": "GIS flood mapping",
                 "technologies": ["arcgis", "python"], "outcomes": ["flood risk map"]},
                {"id": "p2", "title": "Transit Study", "description": "Transit optimization",
                 "technologies": ["python", "networkx"]},
            ],
            competencies_demonstrated={
                "p1": ["spatial_analysis", "cartography"],
                "p2": ["network_analysis", "optimization"],
            },
        )
        assert portfolio["project_count"] == 2
        assert len(portfolio["sections"]) >= 3
        assert "spatial_analysis" in portfolio["competency_summary"]
        assert portfolio["competency_summary"]["spatial_analysis"]["demonstrated"] is True


class TestRecertificationStatus:
    """Tests for recertification status check."""

    def test_recertification_status(self) -> None:
        pd = ProfessionalDevelopment()
        pd.register_professional({"id": "p1", "name": "Jane", "role": "Analyst"})
        status = pd.get_recertification_status("p1", "GISP")
        assert status["certification"] == "GISP"
        assert status["required_credits"] == 60
        assert status["remaining_credits"] == 60  # No credits yet

    def test_recertification_unknown_professional(self) -> None:
        pd = ProfessionalDevelopment()
        status = pd.get_recertification_status("unknown", "GISP")
        assert "error" in status
