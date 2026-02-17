"""Tests for NORMS data models: Regulation, LegalEntity, ComplianceStatus, ComplianceMetric."""
import datetime
import pytest
from shapely.geometry import Point, Polygon, MultiPolygon

from geo_infer_norms.models.regulation import Regulation, RegulatoryFramework
from geo_infer_norms.models.legal_entity import LegalEntity, Jurisdiction
from geo_infer_norms.models.compliance_status import ComplianceStatus, ComplianceMetric


class TestRegulation:
    def test_create_regulation(self):
        reg = Regulation.create(
            name="Clean Water Act",
            description="Regulates water quality",
            regulation_type="environmental",
            issuing_authority="EPA",
            effective_date=datetime.date(2020, 1, 1),
        )
        assert reg.name == "Clean Water Act"
        assert reg.id is not None

    def test_is_active_effective(self):
        reg = Regulation.create(
            name="Test",
            description="Test",
            regulation_type="environmental",
            issuing_authority="EPA",
            effective_date=datetime.date(2020, 1, 1),
        )
        assert reg.is_active() is True

    def test_is_active_expired(self):
        reg = Regulation.create(
            name="Test",
            description="Test",
            regulation_type="environmental",
            issuing_authority="EPA",
            effective_date=datetime.date(2020, 1, 1),
            expiration_date=datetime.date(2021, 1, 1),
        )
        assert reg.is_active() is False

    def test_add_jurisdiction(self):
        reg = Regulation.create(
            name="Test",
            description="Test",
            regulation_type="environmental",
            issuing_authority="EPA",
            effective_date=datetime.date(2020, 1, 1),
        )
        reg.add_jurisdiction("CA")
        assert "CA" in reg.applicable_jurisdictions
        reg.add_jurisdiction("CA")  # Duplicate
        assert reg.applicable_jurisdictions.count("CA") == 1

    def test_amend(self):
        reg = Regulation.create(
            name="Test",
            description="Original",
            regulation_type="environmental",
            issuing_authority="EPA",
            effective_date=datetime.date(2020, 1, 1),
        )
        reg.amend("Updated description")
        assert reg.description == "Updated description"
        assert reg.amendment_date is not None


class TestRegulatoryFramework:
    def test_create_framework(self):
        fw = RegulatoryFramework.create(
            name="Environmental Framework",
            description="Test framework",
            domain="environment",
            issuing_authority="EPA",
        )
        assert fw.name == "Environmental Framework"
        assert fw.version == "1.0"

    def test_add_remove_regulation(self):
        fw = RegulatoryFramework.create(
            name="Test", description="Test", domain="test", issuing_authority="EPA"
        )
        fw.add_regulation("reg-1")
        assert "reg-1" in fw.regulations
        fw.remove_regulation("reg-1")
        assert "reg-1" not in fw.regulations


class TestLegalEntity:
    def test_create_entity(self):
        entity = LegalEntity.create(
            name="Acme Corp",
            entity_type="organization",
        )
        assert entity.name == "Acme Corp"
        assert entity.id is not None

    def test_set_geometry(self):
        entity = LegalEntity.create(name="Site A", entity_type="facility")
        poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        entity.set_geometry(poly)
        assert entity.geometry is not None
        assert entity.point_location is not None

    def test_jurisdiction_management(self):
        entity = LegalEntity.create(name="Test", entity_type="facility")
        entity.add_jurisdiction("CA")
        entity.add_jurisdiction("NY")
        assert len(entity.jurisdiction_ids) == 2
        entity.remove_jurisdiction("CA")
        assert len(entity.jurisdiction_ids) == 1


class TestJurisdiction:
    def test_create_jurisdiction(self):
        jur = Jurisdiction.create(name="California", level="state", code="CA")
        assert jur.name == "California"
        assert jur.code == "CA"

    def test_contains_point(self):
        poly = MultiPolygon([Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])])
        jur = Jurisdiction.create(name="Test", level="county", geometry=poly)
        assert jur.contains_point(Point(5, 5)) is True
        assert jur.contains_point(Point(15, 15)) is False

    def test_contains_point_no_geometry(self):
        jur = Jurisdiction.create(name="Test", level="county")
        assert jur.contains_point(Point(5, 5)) is False


class TestComplianceStatus:
    def test_create_status(self):
        status = ComplianceStatus.create(
            entity_id="ent-1",
            regulation_id="reg-1",
            is_compliant=True,
            compliance_level=0.95,
        )
        assert status.is_compliant is True
        assert status.compliance_level == 0.95
        assert status.id is not None

    def test_add_evidence(self):
        status = ComplianceStatus.create(
            entity_id="ent-1",
            regulation_id="reg-1",
            is_compliant=True,
            compliance_level=1.0,
        )
        status.add_evidence("report", "annual_report.pdf")
        assert status.evidence["report"] == "annual_report.pdf"

    def test_is_recent(self):
        status = ComplianceStatus.create(
            entity_id="ent-1",
            regulation_id="reg-1",
            is_compliant=True,
            compliance_level=1.0,
        )
        assert status.is_recent(days=30) is True


class TestComplianceMetric:
    def test_create_threshold_metric(self):
        metric = ComplianceMetric.create(
            name="Emission Level",
            description="Max emission level",
            regulation_id="reg-1",
            evaluation_type="threshold",
            primary_field="emission_level",
            threshold_value=50.0,
            comparison="less_than",
        )
        assert metric.evaluation_type == "threshold"
        assert metric.threshold_value == 50.0

    def test_set_range(self):
        metric = ComplianceMetric.create(
            name="pH", description="pH range", regulation_id="reg-1",
            evaluation_type="range", primary_field="ph",
        )
        metric.set_range(6.5, 8.5)
        assert metric.range_min == 6.5
        assert metric.range_max == 8.5

    def test_set_range_wrong_type(self):
        metric = ComplianceMetric.create(
            name="Test", description="Test", regulation_id="reg-1",
            evaluation_type="threshold", primary_field="val",
        )
        with pytest.raises(ValueError):
            metric.set_range(0, 10)

    def test_add_sub_metric(self):
        metric = ComplianceMetric.create(
            name="Composite", description="Composite metric", regulation_id="reg-1",
            evaluation_type="composite", primary_field="overall",
        )
        metric.add_sub_metric("sub-1")
        assert "sub-1" in metric.sub_metrics
