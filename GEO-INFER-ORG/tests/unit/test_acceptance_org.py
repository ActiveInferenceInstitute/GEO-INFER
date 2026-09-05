"""
DOMAIN-02 Acceptance tests for GEO-INFER-ORG documented features.

These tests exercise real implemented behavior for documented features that
previously lacked focused acceptance tests:

1. OrganizationModel — hierarchy depth, descendant/ancestor traversal,
   structural metrics, reporting chains, budget allocation strategies.
2. CollaborationNetwork — network density/clustering, knowledge flow
   source/sink identification, betweenness centrality.
3. TeamFormation — greedy skill-coverage team formation, skill-gap analysis.
4. VotingEngine — simple majority, supermajority, unanimous, and weighted
   voting tally semantics.
5. ConsensusModel — rating-based consensus scoring and convergence checking.

No mocks, stubs, or placeholders: every assertion exercises actual code paths.
"""

import pytest

from geo_infer_org.core.organization import (
    OrganizationModel,
    OrgUnit,
    Role,
    RoleLevel,
    OrgStructureType,
)
from geo_infer_org.core.collaboration import (
    CollaborationNetwork,
    CollaborationEdge,
    CollaborationType,
    TeamFormation,
    TeamMember,
)
from geo_infer_org.core.governance import (
    VotingEngine,
    ConsensusModel,
    Vote,
    Proposal,
    VotingMethod,
)


# ---------------------------------------------------------------------------
# OrganizationModel
# ---------------------------------------------------------------------------

class TestOrganizationModelAcceptance:
    """Acceptance: hierarchical structure and budget allocation."""

    @pytest.fixture
    def model(self) -> OrganizationModel:
        m = OrganizationModel(OrgStructureType.HIERARCHICAL)
        m.add_unit(OrgUnit("root", "HQ", member_count=50, budget=100_000))
        m.add_unit(OrgUnit("eng", "Engineering", parent_id="root", member_count=30, budget=60_000))
        m.add_unit(OrgUnit("sales", "Sales", parent_id="root", member_count=20, budget=40_000))
        m.add_unit(OrgUnit("be", "Backend", parent_id="eng", member_count=15, budget=30_000))
        m.add_role(Role("ceo", "CEO", RoleLevel.EXECUTIVE, "root"))
        m.add_role(Role("vp", "VP Eng", RoleLevel.DIRECTOR, "eng", reports_to="ceo"))
        m.add_role(Role("ic", "Engineer", RoleLevel.INDIVIDUAL, "be", reports_to="vp"))
        return m

    def test_depth_and_descendants(self, model):
        """Root depth is 0; grandchildren are depth 2 and reachable as descendants."""
        assert model.compute_depth("root") == 0
        assert model.compute_depth("be") == 2
        descendants = model.get_descendants("root")
        descendant_ids = {u.unit_id for u in descendants}
        assert {"eng", "sales", "be"} <= descendant_ids
        assert "root" not in descendant_ids

    def test_ancestors_chain_rootward(self, model):
        """Ancestors of a leaf go parent → root."""
        ancestors = model.get_ancestors("be")
        assert [a.unit_id for a in ancestors] == ["eng", "root"]

    def test_metrics_report_structure(self, model):
        """Metrics reflect total units, max depth, and span of control."""
        metrics = model.compute_metrics()
        assert metrics.total_units == 4
        assert metrics.total_roles == 3
        assert metrics.max_depth == 2
        assert metrics.avg_span_of_control > 0.0  # root has 2 children, eng has 1

    def test_reporting_chain_to_top(self, model):
        """The reporting chain ascends from IC to the executive."""
        chain = model.find_reporting_chain("ic")
        assert [r.role_id for r in chain] == ["vp", "ceo"]

    def test_budget_proportional_allocation(self, model):
        """Proportional allocation splits budget by member count."""
        allocation = model.allocate_budget(100_000, strategy="proportional")
        assert pytest.approx(sum(allocation.values()), abs=1e-6) == 100_000
        # 'eng' (30) gets more than 'sales' (20).
        assert allocation["eng"] > allocation["sales"]

    def test_budget_equal_allocation(self, model):
        """Equal allocation divides budget evenly across all units."""
        allocation = model.allocate_budget(80, strategy="equal")
        assert len(allocation) == 4
        assert all(v == 20.0 for v in allocation.values())

    def test_unknown_budget_strategy_raises(self, model):
        """An unsupported allocation strategy raises ValueError."""
        with pytest.raises(ValueError, match="Unknown allocation strategy"):
            model.allocate_budget(100, strategy="lottery")

    def test_to_dict_serializes_structure(self, model):
        """to_dict produces a serializable view of units and roles."""
        d = model.to_dict()
        assert d["structure_type"] == "hierarchical"
        assert "root" in d["units"]
        assert d["roles"]["ceo"]["level"] == "EXECUTIVE"


# ---------------------------------------------------------------------------
# CollaborationNetwork
# ---------------------------------------------------------------------------

class TestCollaborationNetworkAcceptance:
    """Acceptance: collaboration graph metrics and knowledge flow."""

    def test_density_and_components(self):
        """A triangle plus an isolated node yields the expected component count."""
        net = CollaborationNetwork()
        for src, tgt in [("a", "b"), ("b", "c"), ("a", "c")]:
            net.add_edge(CollaborationEdge(
                src, tgt, CollaborationType.TASK_COORDINATION, strength=1.0,
            ))
        net.add_node("loner")
        metrics = net.compute_metrics()
        assert metrics.node_count == 4
        assert metrics.edge_count == 3
        assert metrics.connected_components == 2
        assert 0.0 < metrics.density <= 1.0
        assert metrics.most_central_nodes  # non-empty

    def test_knowledge_flow_sources_and_sinks(self):
        """KNOWLEDGE_SHARE edges populate sources (outbound) and sinks (inbound)."""
        net = CollaborationNetwork()
        net.add_edge(CollaborationEdge("mentor", "novice1", CollaborationType.KNOWLEDGE_SHARE, strength=0.8))
        net.add_edge(CollaborationEdge("mentor", "novice2", CollaborationType.KNOWLEDGE_SHARE, strength=0.6))
        net.add_edge(CollaborationEdge("novice1", "novice2", CollaborationType.TASK_COORDINATION, strength=0.4))
        flow = net.get_knowledge_flow()
        assert "mentor" in flow["sources"]
        assert flow["sources"]["mentor"] == round(0.8 + 0.6, 4)
        # task_coordination edge should not appear in knowledge flow.
        assert "novice1" not in flow["sources"]


# ---------------------------------------------------------------------------
# TeamFormation
# ---------------------------------------------------------------------------

class TestTeamFormationAcceptance:
    """Acceptance: skill-coverage team formation and gap analysis."""

    def test_form_team_covers_required_skills(self):
        """The greedy algorithm selects members covering all required skills."""
        tf = TeamFormation()
        tf.add_members([
            TeamMember("m1", "Alice", ["python", "sql"], unit_id="eng"),
            TeamMember("m2", "Bob", ["python", "docker"], unit_id="ops"),
            TeamMember("m3", "Cara", ["frontend"], unit_id="design"),
        ])
        result = tf.form_team(required_skills=["python", "sql", "docker"], max_size=3)
        assert result.skill_coverage == 1.0
        assert "m1" in result.team_members  # covers python+sql
        assert "m2" in result.team_members  # covers docker
        assert result.overall_score > 0.0

    def test_skill_gap_reports_missing(self):
        """compute_skill_gap lists missing skills and their coverage ratio."""
        tf = TeamFormation()
        tf.add_member(TeamMember("m1", "Alice", ["python"]))
        gap = tf.compute_skill_gap(["python", "rust", "go"])
        assert "rust" in gap["missing"]
        assert "go" in gap["missing"]
        assert "python" in gap["covered"]
        assert gap["coverage_ratio"] == round(1 / 3, 4)

    def test_form_team_empty_pool_raises(self):
        """Forming a team with no available members raises."""
        tf = TeamFormation()
        with pytest.raises(ValueError, match="No members available"):
            tf.form_team(required_skills=["python"])


# ---------------------------------------------------------------------------
# VotingEngine
# ---------------------------------------------------------------------------

class TestVotingEngineAcceptance:
    """Acceptance: governance voting semantics across methods."""

    @pytest.fixture
    def engine(self) -> VotingEngine:
        return VotingEngine()

    def test_simple_majority_plurality_wins(self, engine):
        """The option with the most votes wins under simple majority."""
        engine.create_proposal(Proposal(
            "p1", "Budget", "Approve budget", "proposer", options=["yes", "no"],
            voting_method=VotingMethod.SIMPLE_MAJORITY,
        ))
        for vid in ("v1", "v2", "v3"):
            engine.cast_vote("p1", Vote(vid, "yes"))
        engine.cast_vote("p1", Vote("v4", "no"))
        result = engine.tally("p1")
        assert result.winner == "yes"
        assert result.vote_counts["yes"] == 3
        assert result.total_votes == 4

    def test_supermajority_requires_two_thirds(self, engine):
        """A bare majority (2/4) is insufficient under supermajority."""
        engine.create_proposal(Proposal(
            "p2", "Amend", "Amend bylaws", "proposer", options=["pass", "fail"],
            voting_method=VotingMethod.SUPERMAJORITY,
        ))
        engine.cast_vote("p2", Vote("a", "pass"))
        engine.cast_vote("p2", Vote("b", "pass"))
        engine.cast_vote("p2", Vote("c", "fail"))
        engine.cast_vote("p2", Vote("d", "fail"))
        result = engine.tally("p2")
        # 2/4 = 0.5 < 2/3 threshold → no winner.
        assert result.winner is None

    def test_unanimous_requires_consensus(self, engine):
        """Unanimous voting only passes when every vote agrees."""
        engine.create_proposal(Proposal(
            "p3", "Merger", "Unanimous merger", "proposer", options=["approve", "reject"],
            voting_method=VotingMethod.UNANIMOUS,
        ))
        for vid in ("a", "b", "c"):
            engine.cast_vote("p3", Vote(vid, "approve"))
        result = engine.tally("p3")
        assert result.winner == "approve"
        assert result.method == VotingMethod.UNANIMOUS

    def test_weighted_tally_uses_weights(self, engine):
        """Weighted tally sums vote weights; a heavy minority can win."""
        engine.create_proposal(Proposal(
            "p4", "Weighted", "Weighted vote", "proposer", options=["x", "y"],
            voting_method=VotingMethod.WEIGHTED,
        ))
        engine.cast_vote("p4", Vote("a", "x", weight=1.0))
        engine.cast_vote("p4", Vote("b", "x", weight=1.0))
        engine.cast_vote("p4", Vote("c", "y", weight=5.0))
        result = engine.tally("p4")
        assert result.winner == "y"
        assert result.vote_counts["y"] == 5.0

    def test_duplicate_voter_rejected(self, engine):
        """A voter casting twice on the same proposal raises."""
        engine.create_proposal(Proposal(
            "p5", "One", "Single vote", "proposer", options=["a", "b"],
        ))
        engine.cast_vote("p5", Vote("v1", "a"))
        with pytest.raises(ValueError, match="already voted"):
            engine.cast_vote("p5", Vote("v1", "b"))


# ---------------------------------------------------------------------------
# ConsensusModel
# ---------------------------------------------------------------------------

class TestConsensusModelAcceptance:
    """Acceptance: rating-based consensus scoring."""

    def test_unanimous_ratings_yield_full_consensus(self):
        """Identical ratings across participants produce consensus_level 1.0."""
        cm = ConsensusModel()
        cm.set_options(["alpha", "beta"])
        cm.submit_rating("p1", {"alpha": 8.0, "beta": 6.0})
        cm.submit_rating("p2", {"alpha": 8.0, "beta": 6.0})
        result = cm.compute_consensus()
        assert result["consensus_level"] == 1.0
        assert result["recommendation"] == "alpha"
        assert result["participant_count"] == 2

    def test_resubmitted_ratings_overwrite_and_converge(self):
        """Resubmitting ratings for an existing participant overwrites
        their previous round (documented overwrite semantics); the small
        score change stays below the convergence threshold."""
        cm = ConsensusModel(convergence_threshold=0.5)
        cm.set_options(["alpha", "beta"])
        cm.submit_rating("p1", {"alpha": 7.0, "beta": 5.0})
        cm.submit_rating("p2", {"alpha": 7.0, "beta": 5.0})
        current = cm.compute_consensus()["option_scores"]
        # p1 resubmits: values are replaced, not accumulated as a new round.
        cm.submit_rating("p1", {"alpha": 7.2, "beta": 5.1})
        assert cm.compute_consensus()["participant_count"] == 2
        assert cm.check_convergence(current) is True

    def test_no_ratings_raises(self):
        """Computing consensus with no ratings raises."""
        cm = ConsensusModel()
        cm.set_options(["x", "y"])
        with pytest.raises(ValueError, match="No ratings submitted"):
            cm.compute_consensus()
