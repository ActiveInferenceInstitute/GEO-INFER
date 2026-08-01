"""
DOMAIN-02 Acceptance tests for GEO-INFER-METAGOV documented features.

These tests exercise real implemented behavior for documented features that
previously lacked focused acceptance tests:

1. PolycentricGovernanceSystem — multi-center governance design, authority
   relationship analysis, redundancy assessment.
2. StakeholderGovernanceCoordinator — stakeholder analysis, power dynamics,
   governance platform establishment, participatory process design.
3. ConflictResolver — Nash bargaining negotiation, mediation, arbitration,
   consensus building, auto-method selection.
4. AccountabilityFramework — accountability mechanisms, audit trails,
   transparency scoring.
5. MultiLevelGovernanceFramework — governance structure design, vertical
   coordination, subsidiarity principle, performance metrics.

No mocks, stubs, or placeholders: every assertion exercises actual code paths.
"""

import pytest

from geo_infer_metagov.core.polycentric import (
    PolycentricGovernanceSystem,
    PolycentricDesign,
)
from geo_infer_metagov.core.stakeholder import (
    StakeholderGovernanceCoordinator,
    Stakeholder,
    GovernancePlatform,
)
from geo_infer_metagov.core.conflict_resolution import (
    ConflictResolver,
    ConflictResolutionMethod,
    ConflictResolution,
)
from geo_infer_metagov.core.accountability import (
    AccountabilityFramework,
    AccountabilityMechanisms,
    TransparencySystem,
)
from geo_infer_metagov.core.multi_level import (
    MultiLevelGovernanceFramework,
)
from geo_infer_metagov.core.institutional import InstitutionalDesigner


# ---------------------------------------------------------------------------
# PolycentricGovernanceSystem
# ---------------------------------------------------------------------------

class TestPolycentricGovernance:
    """Acceptance: polycentric governance design and authority analysis."""

    @pytest.fixture
    def system(self) -> PolycentricGovernanceSystem:
        return PolycentricGovernanceSystem()

    def test_design_polycentric_structure(self, system):
        """design_polycentric_structure creates and stores a PolycentricDesign."""
        design = system.design_polycentric_structure(
            governing_bodies=[
                {"id": "local", "domains": ["water", "land"]},
                {"id": "regional", "domains": ["water", "energy"]},
            ],
            jurisdictional_overlaps={"local": ["regional"]},
            spatial_scales=["local", "regional"],
            functional_domains=["water", "energy", "land"],
            feedback_mechanisms={"type": "public_review"},
        )
        assert isinstance(design, PolycentricDesign)
        assert design.design_id == "polycentric_0"
        assert "redundancy_assessment" in design.__dict__ or hasattr(design, "redundancy_assessment")
        assert "polycentric_0" in system.polycentric_designs

    def test_assess_redundancy_returns_metrics(self, system):
        """_assess_redundancy computes redundancy ratio and resilience level."""
        redundancy = system._assess_redundancy(
            governing_bodies=[{"id": "a"}, {"id": "b"}],
            jurisdictional_overlaps={"a": ["b", "c"]},
        )
        assert "redundancy_ratio" in redundancy
        assert "resilience_level" in redundancy
        assert "efficiency_impact" in redundancy
        assert 0 <= redundancy["redundancy_ratio"] <= 1.0

    def test_analyze_authority_relationships(self, system):
        """analyze_authority_relationships computes coordination index and density."""
        authorities = [
            {"id": "auth1", "domains": ["water"], "jurisdiction": ["zone_a"]},
            {"id": "auth2", "domains": ["water", "energy"], "jurisdiction": ["zone_a", "zone_b"]},
            {"id": "auth3", "domains": ["energy"], "jurisdiction": ["zone_c"]},
        ]
        result = system.analyze_authority_relationships(
            authorities=authorities,
            relationships=["coordination", "cooperation"],
            effectiveness_measures=["response_time"],
        )
        assert result["authority_count"] == 3
        assert "coordination_index" in result
        assert "network_density" in result
        assert "redundancy_metrics" in result
        assert "resilience_score" in result

    def test_analyze_empty_authorities(self, system):
        """Empty authority list returns zero coordination index."""
        result = system.analyze_authority_relationships(
            authorities=[],
            relationships=["coordination"],
            effectiveness_measures=["speed"],
        )
        assert result["authority_count"] == 0
        assert result["coordination_index"] == 0.0


# ---------------------------------------------------------------------------
# StakeholderGovernanceCoordinator
# ---------------------------------------------------------------------------

class TestStakeholderGovernance:
    """Acceptance: stakeholder analysis and governance platform management."""

    @pytest.fixture
    def coordinator(self) -> StakeholderGovernanceCoordinator:
        return StakeholderGovernanceCoordinator()

    def test_analyze_stakeholders_returns_groups(self, coordinator):
        """analyze_stakeholders creates stakeholder groups for each category."""
        analysis = coordinator.analyze_stakeholders(
            governance_domain="watershed",
            spatial_extent={"region": "basin-7"},
            stakeholder_categories=["government", "community", "ngo"],
        )
        assert analysis["governance_domain"] == "watershed"
        assert len(analysis["stakeholder_groups"]) == 3
        assert all(isinstance(s, Stakeholder) for s in analysis["stakeholder_groups"])

    def test_analyze_stakeholders_power_dynamics(self, coordinator):
        """power_dynamics includes Herfindahl index and Gini coefficient."""
        analysis = coordinator.analyze_stakeholders(
            governance_domain="forest",
            spatial_extent={"region": "north"},
            stakeholder_categories=["government", "business", "community"],
        )
        pd = analysis["power_dynamics"]
        assert "herfindahl_index" in pd
        assert "gini_coefficient" in pd
        assert "power_balance_assessment" in pd
        assert pd["num_stakeholders"] == 3

    def test_analyze_stakeholders_collaboration_potential(self, coordinator):
        """collaboration_potential is a float in [0, 1]."""
        analysis = coordinator.analyze_stakeholders(
            governance_domain="fishery",
            spatial_extent={"region": "coast"},
            stakeholder_categories=["government", "community", "business", "ngo"],
        )
        cp = analysis["collaboration_potential"]
        assert isinstance(cp, float)
        assert 0.0 <= cp <= 1.0

    def test_establish_governance_platform(self, coordinator):
        """establish_governance_platform stores and returns a GovernancePlatform."""
        participants = [
            {"name": "City Council", "category": "government", "influence": 0.9, "power": 0.85},
            {"name": "Citizens Group", "category": "community", "influence": 0.4, "power": 0.35},
        ]
        platform = coordinator.establish_governance_platform(
            participants=participants,
            governance_mechanisms=["voting", "consultation"],
            decision_domains=["budget", "planning"],
            conflict_resolution_capacity=True,
        )
        assert isinstance(platform, GovernancePlatform)
        assert len(platform.stakeholders) == 2
        assert platform.conflict_resolution_capacity is True
        assert "platform_0" in coordinator.governance_platforms

    def test_design_participatory_process(self, coordinator):
        """design_participatory_process returns phased process with equity mechanisms."""
        process = coordinator.design_participatory_process(
            stakeholder_groups=["government", "community"],
            decision_type="resource_allocation",
            equity_principles=["procedural_fairness", "distributive_justice"],
            transparency_requirements=True,
        )
        assert "process_design" in process
        assert process["process_design"]["decision_type"] == "resource_allocation"
        assert "phases" in process["process_design"]
        assert len(process["process_design"]["phases"]) >= 4
        assert "equity_mechanisms" in process


# ---------------------------------------------------------------------------
# ConflictResolver
# ---------------------------------------------------------------------------

class TestConflictResolver:
    """Acceptance: conflict resolution methods and auto-selection."""

    @pytest.fixture
    def resolver(self) -> ConflictResolver:
        return ConflictResolver()

    def test_negotiation_resolves_with_agreement(self, resolver):
        """Nash bargaining succeeds when all parties have utility > BATNA."""
        resolution = resolver.resolve_conflict(
            conflict={"id": "c1", "type": "resource_dispute", "severity": "medium"},
            stakeholders=[
                {"id": "s1", "decision_power": 0.8, "interest_level": 0.7, "batna": 0.3},
                {"id": "s2", "decision_power": 0.6, "interest_level": 0.6, "batna": 0.2},
            ],
            method=ConflictResolutionMethod.NEGOTIATION,
        )
        assert isinstance(resolution, ConflictResolution)
        assert resolution.resolved is True
        assert resolution.resolution_agreement is not None
        assert len(resolver.resolution_history) == 1

    def test_negotiation_fails_with_low_utility(self, resolver):
        """Negotiation fails when a party's utility <= BATNA."""
        resolution = resolver.resolve_conflict(
            conflict={"id": "c2", "type": "resource"},
            stakeholders=[
                {"id": "s1", "decision_power": 0.1, "interest_level": 0.1, "batna": 0.5},
                {"id": "s2", "decision_power": 0.5, "interest_level": 0.5, "batna": 0.2},
            ],
            method=ConflictResolutionMethod.NEGOTIATION,
        )
        assert resolution.resolved is False

    def test_arbitration_always_resolves(self, resolver):
        """Arbitration produces a binding resolution."""
        resolution = resolver.resolve_conflict(
            conflict={"id": "c3", "type": "boundary"},
            stakeholders=[
                {"id": "s1", "decision_power": 0.7},
                {"id": "s2", "decision_power": 0.5},
            ],
            method=ConflictResolutionMethod.ARBITRATION,
        )
        assert resolution.resolved is True
        assert resolution.resolution_agreement is not None

    def test_consensus_building_converges(self, resolver):
        """Consensus building converges for close initial positions."""
        resolution = resolver.resolve_conflict(
            conflict={"id": "c4", "type": "policy"},
            stakeholders=[
                {"id": "s1", "position": 0.5},
                {"id": "s2", "position": 0.55},
                {"id": "s3", "position": 0.48},
            ],
            method=ConflictResolutionMethod.CONSENSUS_BUILDING,
        )
        assert resolution.resolution_agreement is not None
        assert "consensus_position" in resolution.resolution_agreement

    def test_auto_select_high_severity_arbitration(self, resolver):
        """High severity with >2 stakeholders auto-selects arbitration."""
        resolution = resolver.resolve_conflict(
            conflict={"type": "territorial", "severity": "high"},
            stakeholders=[
                {"id": "s1", "decision_power": 0.7},
                {"id": "s2", "decision_power": 0.5},
                {"id": "s3", "decision_power": 0.4},
            ],
            method=None,  # auto-select
        )
        assert resolution.resolution_method == ConflictResolutionMethod.ARBITRATION

    def test_auto_select_resource_conflict_negotiation(self, resolver):
        """Resource conflicts auto-select negotiation."""
        resolution = resolver.resolve_conflict(
            conflict={"type": "resource_allocation", "severity": "low"},
            stakeholders=[
                {"id": "s1", "decision_power": 0.6},
                {"id": "s2", "decision_power": 0.5},
            ],
            method=None,
        )
        assert resolution.resolution_method == ConflictResolutionMethod.NEGOTIATION


# ---------------------------------------------------------------------------
# AccountabilityFramework
# ---------------------------------------------------------------------------

class TestAccountabilityFramework:
    """Acceptance: accountability mechanisms and transparency."""

    @pytest.fixture
    def framework(self) -> AccountabilityFramework:
        return AccountabilityFramework()

    def test_establish_accountability(self, framework):
        """establish_accountability creates mechanisms with audit trails."""
        mechanisms = framework.establish_accountability(
            governing_bodies=[{"id": "council", "name": "City Council"}],
            stakeholder_groups=[{"id": "residents", "name": "Residents"}],
            accountability_directions=["upward", "downward", "horizontal"],
            enforcement_capacity="strong",
        )
        assert isinstance(mechanisms, AccountabilityMechanisms)
        assert "audit_trail_structure" in mechanisms.__dict__
        assert len(mechanisms.audit_mechanisms) > 0
        assert "accountability_0" in framework.accountability_systems

    def test_audit_mechanisms_include_direction_specific(self, framework):
        """Upward/downward/horizontal directions add specific audit mechanisms."""
        mechanisms = framework.establish_accountability(
            governing_bodies=[{"id": "b1"}],
            stakeholder_groups=[{"id": "s1"}],
            accountability_directions=["upward", "downward", "horizontal"],
            enforcement_capacity="moderate",
        )
        # upward adds upward_reporting, downward adds public_reporting
        assert "upward_reporting" in mechanisms.audit_mechanisms
        assert "public_reporting" in mechanisms.audit_mechanisms
        assert "peer_review" in mechanisms.audit_mechanisms

    def test_implement_transparency(self, framework):
        """implement_transparency creates a scored TransparencySystem."""
        system = framework.implement_transparency(
            information_types=["decisions", "budgets", "outcomes"],
            disclosure_frequency="real_time",
            accessibility_requirements=["multiple_languages", "digital_access"],
            documentation_standards="comprehensive",
        )
        assert isinstance(system, TransparencySystem)
        assert system.transparency_score > 0.5
        assert system.disclosure_coverage > 0
        assert "transparency_0" in framework.transparency_systems

    def test_transparency_score_real_time_higher_than_annual(self, framework):
        """Real-time disclosure scores higher than annual."""
        real_time = framework.implement_transparency(
            information_types=["decisions"],
            disclosure_frequency="real_time",
            accessibility_requirements=["digital_access"],
            documentation_standards="standard",
        )
        annual = framework.implement_transparency(
            information_types=["decisions"],
            disclosure_frequency="annual",
            accessibility_requirements=["digital_access"],
            documentation_standards="standard",
        )
        assert real_time.transparency_score > annual.transparency_score

    def test_enable_participation(self, framework):
        """enable_participation returns participation forms and channels."""
        result = framework.enable_participation(
            participation_forms=["consultation", "co_production"],
            barriers_to_remove=["language", "accessibility"],
            capacity_building="training_programs",
        )
        assert "participation_forms" in result
        assert "participation_channels" in result
        assert len(result["participation_channels"]) >= 3


# ---------------------------------------------------------------------------
# MultiLevelGovernanceFramework
# ---------------------------------------------------------------------------

class TestMultiLevelGovernance:
    """Acceptance: multi-level governance structure design."""

    @pytest.fixture
    def framework(self) -> MultiLevelGovernanceFramework:
        return MultiLevelGovernanceFramework()

    def test_design_governance_structure(self, framework):
        """design_governance_structure creates a multi-level structure."""
        structure = framework.design_governance_structure(
            spatial_scope={"region": "watershed", "levels": ["local", "regional", "national"]},
            stakeholder_groups=[
                {"id": "farmers", "interests": ["water_access"]},
                {"id": "city", "interests": ["water_supply"]},
            ],
            decision_domains=["water_allocation", "quality_standards"],
            time_horizons=[1, 5, 10],
        )
        assert structure is not None
        # The structure should have levels or tiers
        assert hasattr(structure, "governance_levels") or hasattr(structure, "levels")

    def test_calculate_performance_metrics(self, framework):
        """calculate_performance_metrics returns a metrics dictionary."""
        structure = framework.design_governance_structure(
            spatial_scope={"region": "fishery"},
            stakeholder_groups=[{"id": "fishers"}, {"id": "regulators"}],
            decision_domains=["quota"],
            time_horizons=[1, 5],
        )
        metrics = framework.calculate_performance_metrics(structure)
        assert isinstance(metrics, dict)
        assert len(metrics) > 0
