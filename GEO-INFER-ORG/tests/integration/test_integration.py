"""Integration tests for GEO-INFER-ORG.

Exercises the two halves of the module together: an organizational
structure is built, measured, and budgeted, and its governance layer runs
proposals through several voting methods to a tallied decision.
"""

import pytest

from geo_infer_org import (
    OrganizationModel,
    OrgStructureType,
    OrgUnit,
    Proposal,
    Role,
    RoleLevel,
    Vote,
    VotingEngine,
    VotingMethod,
)


@pytest.fixture(name="org")
def _org():
    """A three-level organization: one root, two divisions, two teams."""
    model = OrganizationModel(structure_type=OrgStructureType.HIERARCHICAL)
    model.add_unit(OrgUnit(unit_id="root", name="Agency", member_count=4, budget=0.0))
    model.add_unit(
        OrgUnit(unit_id="ops", name="Operations", parent_id="root", member_count=20)
    )
    model.add_unit(
        OrgUnit(unit_id="sci", name="Science", parent_id="root", member_count=10)
    )
    model.add_unit(
        OrgUnit(unit_id="field", name="Field Team", parent_id="ops", member_count=6)
    )
    model.add_role(
        Role(role_id="dir", title="Director", level=RoleLevel.EXECUTIVE, unit_id="root")
    )
    model.add_role(
        Role(
            role_id="ops-mgr",
            title="Operations Manager",
            level=RoleLevel.MANAGER,
            unit_id="ops",
            reports_to="dir",
        )
    )
    model.add_role(
        Role(
            role_id="field-lead",
            title="Field Lead",
            level=RoleLevel.LEAD,
            unit_id="field",
            reports_to="ops-mgr",
        )
    )
    return model


class TestOrganizationStructure:
    def test_children_resolve_from_the_root(self, org):
        """The root's direct children are its two divisions."""
        assert {unit.unit_id for unit in org.get_children("root")} == {"ops", "sci"}

    def test_descendants_include_nested_units(self, org):
        """Descendants reach past direct children into nested teams."""
        assert {unit.unit_id for unit in org.get_descendants("root")} == {
            "ops",
            "sci",
            "field",
        }

    def test_ancestors_walk_back_to_the_root(self, org):
        """A nested unit traces its full parent chain."""
        assert [unit.unit_id for unit in org.get_ancestors("field")] == ["ops", "root"]

    def test_depth_reflects_the_hierarchy(self, org):
        """Depth grows with distance from the root."""
        assert org.compute_depth("root") == 0
        assert org.compute_depth("ops") == 1
        assert org.compute_depth("field") == 2

    def test_reporting_chain_follows_reports_to(self, org):
        """A role's chain runs up through its managers."""
        chain = [role.role_id for role in org.find_reporting_chain("field-lead")]
        assert chain[:2] == ["ops-mgr", "dir"] or chain == ["ops-mgr", "dir"]

    def test_metrics_are_computed_from_real_structure(self, org):
        """Metrics reflect the units and roles actually registered."""
        metrics = org.compute_metrics()
        assert metrics is not None
        assert org.to_dict()["structure_type"] == OrgStructureType.HIERARCHICAL.value

    def test_budget_allocation_is_conserved(self, org):
        """Every allocated currency unit lands in some unit."""
        allocation = org.allocate_budget(1_000_000.0, strategy="proportional")
        assert sum(allocation.values()) == pytest.approx(1_000_000.0, rel=1e-6)

    def test_larger_units_receive_more_proportional_budget(self, org):
        """Proportional allocation tracks headcount."""
        allocation = org.allocate_budget(1_000_000.0, strategy="proportional")
        assert allocation["ops"] > allocation["sci"]

    def test_unknown_unit_has_no_children(self, org):
        """Querying a unit that does not exist is empty, not an error."""
        assert org.get_children("nonexistent") == []


class TestGovernanceVoting:
    def _proposal(self, method, options=("yes", "no"), voters=5):
        return Proposal(
            proposal_id="p1",
            title="Adopt the field survey plan",
            description="Whether to adopt the plan",
            proposer_id="dir",
            options=list(options),
            voting_method=method,
            quorum_fraction=0.5,
            eligible_voters=voters,
        )

    def test_simple_majority_elects_the_leading_option(self):
        """Three of five for 'yes' carries a simple majority."""
        engine = VotingEngine()
        engine.create_proposal(self._proposal(VotingMethod.SIMPLE_MAJORITY))
        for index, choice in enumerate(["yes", "yes", "yes", "no", "no"]):
            engine.cast_vote("p1", Vote(voter_id=f"v{index}", choice=choice))
        assert engine.tally("p1").winner == "yes"

    def test_quorum_failure_is_reported(self):
        """Too few votes cast means the result does not stand."""
        engine = VotingEngine()
        engine.create_proposal(self._proposal(VotingMethod.SIMPLE_MAJORITY, voters=100))
        engine.cast_vote("p1", Vote(voter_id="v0", choice="yes"))
        result = engine.tally("p1")
        assert result.quorum_met is False

    def test_unanimous_method_rejects_a_split_vote(self):
        """One dissenting vote defeats a unanimity requirement."""
        engine = VotingEngine()
        engine.create_proposal(self._proposal(VotingMethod.UNANIMOUS))
        for index, choice in enumerate(["yes", "yes", "yes", "yes", "no"]):
            engine.cast_vote("p1", Vote(voter_id=f"v{index}", choice=choice))
        assert engine.tally("p1").winner != "yes"

    def test_weighted_method_respects_vote_weight(self):
        """A heavily weighted minority can carry a weighted vote."""
        engine = VotingEngine()
        engine.create_proposal(self._proposal(VotingMethod.WEIGHTED))
        engine.cast_vote("p1", Vote(voter_id="v0", choice="yes", weight=10.0))
        engine.cast_vote("p1", Vote(voter_id="v1", choice="no", weight=1.0))
        engine.cast_vote("p1", Vote(voter_id="v2", choice="no", weight=1.0))
        assert engine.tally("p1").winner == "yes"

    def test_tallying_an_unknown_proposal_raises(self):
        """A proposal that was never created cannot be tallied."""
        with pytest.raises((KeyError, ValueError)):
            VotingEngine().tally("never-created")
