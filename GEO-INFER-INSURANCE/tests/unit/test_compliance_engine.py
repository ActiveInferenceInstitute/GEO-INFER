"""Behavioral tests for the compliance engine (GS-146).

Covers requirement applicability, framework-specific requirement loading,
compliance check outcomes against declared thresholds, and report/status
aggregation over stored checks.
"""

from geo_infer_insurance.underwriting.utils.compliance import (
    ComplianceEngine,
    ComplianceFramework,
    ComplianceStatus,
    RegulatoryRequirement,
)


class TestFrameworkRequirements:
    def test_standard_framework_loads_standard_requirements(self) -> None:
        engine = ComplianceEngine(ComplianceFramework.STANDARD)

        assert "std_capital_adequacy" in engine.requirements
        assert "std_reporting_accuracy" in engine.requirements
        assert all(
            req.framework == ComplianceFramework.STANDARD
            for req in engine.requirements.values()
        )

    def test_solvency_ii_framework_loads_solvency_requirements(self) -> None:
        engine = ComplianceEngine(ComplianceFramework.SOLVENCY_II)

        assert "sii_scr_coverage" in engine.requirements
        assert "sii_or_reporting" in engine.requirements

    def test_basel_iii_framework_loads_basel_requirements(self) -> None:
        engine = ComplianceEngine(ComplianceFramework.BASEL_III)

        assert "basel_tier1_capital" in engine.requirements
        assert engine.requirements["basel_tier1_capital"].compliance_threshold == 0.06

    def test_us_insurance_framework_loads_rbc_requirements(self) -> None:
        engine = ComplianceEngine(ComplianceFramework.US_INSURANCE_REGULATION)

        assert "us_risk_based_capital" in engine.requirements
        assert engine.requirements["us_risk_based_capital"].compliance_threshold == 2.0


class TestRequirementApplicability:
    def test_requirement_applicable_when_all_criteria_match(self) -> None:
        req = RegulatoryRequirement(
            requirement_id="r1",
            framework=ComplianceFramework.STANDARD,
            category="capital",
            description="test",
            regulation_reference="ref",
            applicability_criteria={"entity_type": "insurer", "region": "eu"},
        )

        assert req.is_applicable({"entity_type": "insurer", "region": "eu"}) is True

    def test_requirement_not_applicable_when_criteria_mismatch(self) -> None:
        req = RegulatoryRequirement(
            requirement_id="r1",
            framework=ComplianceFramework.STANDARD,
            category="capital",
            description="test",
            regulation_reference="ref",
            applicability_criteria={"entity_type": "insurer"},
        )

        assert req.is_applicable({"entity_type": "bank"}) is False

    def test_requirement_applicable_when_context_key_absent(self) -> None:
        req = RegulatoryRequirement(
            requirement_id="r1",
            framework=ComplianceFramework.STANDARD,
            category="capital",
            description="test",
            regulation_reference="ref",
            applicability_criteria={"entity_type": "insurer"},
        )

        assert req.is_applicable({}) is True

    def test_empty_criteria_always_applicable(self) -> None:
        req = RegulatoryRequirement(
            requirement_id="r1",
            framework=ComplianceFramework.STANDARD,
            category="reporting",
            description="test",
            regulation_reference="ref",
        )

        assert req.is_applicable({"anything": 1}) is True


class TestComplianceChecks:
    def _engine(self) -> ComplianceEngine:
        return ComplianceEngine(ComplianceFramework.STANDARD)

    def test_compliant_entity_passes_all_applicable_requirements(self) -> None:
        engine = self._engine()

        result = engine.perform_compliance_check(
            "entity-1",
            {
                "entity_type": "insurer",
                "capital_ratio": 1.2,
                "reporting_accuracy": 0.99,
            },
        )

        assert result["overall_status"] == "compliant"
        assert result["compliant_requirements"] == result["total_requirements"]
        assert result["non_compliant_requirements"] == 0

    def test_below_threshold_capital_ratio_is_non_compliant(self) -> None:
        engine = self._engine()

        result = engine.perform_compliance_check(
            "entity-2", {"entity_type": "insurer", "capital_ratio": 0.5}
        )

        assert result["overall_status"] == "non_compliant"
        failed = [
            c
            for c in result["requirement_checks"]
            if c.status == ComplianceStatus.NON_COMPLIANT
        ]
        assert [c.requirement_id for c in failed] == ["std_capital_adequacy"]
        assert failed[0].findings
        assert failed[0].evidence["compliance_value"] == 0.5

    def test_inapplicable_requirements_are_skipped(self) -> None:
        engine = self._engine()

        result = engine.perform_compliance_check("entity-3", {"entity_type": "bank"})

        checked_ids = [c.requirement_id for c in result["requirement_checks"]]
        assert "std_capital_adequacy" not in checked_ids
        assert "std_reporting_accuracy" in checked_ids

    def test_check_stored_for_entity_status_lookup(self) -> None:
        engine = self._engine()

        engine.perform_compliance_check("entity-4", {"capital_ratio": 1.5})

        status = engine.get_compliance_status("entity-4")
        assert status["status"] == "compliant"
        assert status["last_check"] is not None

    def test_status_unknown_without_checks(self) -> None:
        engine = self._engine()

        status = engine.get_compliance_status("never-checked")

        assert status == {"status": "unknown", "last_check": None}

    def test_non_compliant_check_dominates_status(self) -> None:
        engine = self._engine()

        engine.perform_compliance_check("entity-5", {"capital_ratio": 0.1})

        status = engine.get_compliance_status("entity-5")
        assert status["status"] == "non_compliant"

    def test_remove_requirement_stops_checking_it(self) -> None:
        engine = self._engine()
        assert engine.remove_requirement("std_capital_adequacy") is True
        assert engine.remove_requirement("std_capital_adequacy") is False

        result = engine.perform_compliance_check("entity-6", {"entity_type": "insurer"})

        checked_ids = [c.requirement_id for c in result["requirement_checks"]]
        assert "std_capital_adequacy" not in checked_ids

    def test_custom_requirement_drives_check_outcome(self) -> None:
        engine = self._engine()
        engine.add_requirement(
            RegulatoryRequirement(
                requirement_id="custom_data_quality",
                framework=ComplianceFramework.STANDARD,
                category="reporting",
                description="data quality above threshold",
                regulation_reference="Internal Policy",
                compliance_threshold=0.9,
            )
        )

        passing = engine.perform_compliance_check("good", {"reporting_accuracy": 0.97})
        failing = engine.perform_compliance_check("bad", {"reporting_accuracy": 0.5})

        good = [
            c
            for c in passing["requirement_checks"]
            if c.requirement_id == "custom_data_quality"
        ]
        bad = [
            c
            for c in failing["requirement_checks"]
            if c.requirement_id == "custom_data_quality"
        ]
        assert good[0].status == ComplianceStatus.COMPLIANT
        assert bad[0].status == ComplianceStatus.NON_COMPLIANT


class TestComplianceReporting:
    def test_report_aggregates_check_counts(self) -> None:
        engine = ComplianceEngine(ComplianceFramework.STANDARD)
        engine.perform_compliance_check("entity-r", {"capital_ratio": 1.5})

        report = engine.generate_compliance_report("entity-r")

        assert report["entity_id"] == "entity-r"
        assert report["framework"] == "standard"
        assert report["total_checks"] >= 2
        assert report["compliance_rate"] == 1.0
        assert report["issues"] == []

    def test_report_collects_issues_from_failed_checks(self) -> None:
        engine = ComplianceEngine(ComplianceFramework.STANDARD)
        engine.perform_compliance_check("entity-bad", {"capital_ratio": 0.1})

        report = engine.generate_compliance_report("entity-bad")

        assert report["compliance_rate"] < 1.0
        assert len(report["issues"]) >= 1

    def test_report_for_unknown_entity_is_empty(self) -> None:
        engine = ComplianceEngine(ComplianceFramework.STANDARD)
        engine.perform_compliance_check("entity-r", {"capital_ratio": 1.5})

        report = engine.generate_compliance_report("someone-else")

        assert report["total_checks"] == 0
        assert report["compliance_rate"] == 0
