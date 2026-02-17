"""Tests for governance: voting engine and consensus model."""

import pytest
from geo_infer_org.core.governance import (
    VotingEngine,
    ConsensusModel,
    VotingMethod,
    Vote,
    Proposal,
    DecisionStatus,
)


@pytest.fixture
def engine():
    return VotingEngine()


@pytest.fixture
def consensus():
    return ConsensusModel()


def make_proposal(pid: str = "p1", method: VotingMethod = VotingMethod.SIMPLE_MAJORITY, eligible: int = 10):
    return Proposal(
        proposal_id=pid,
        title="Test Proposal",
        description="A test",
        proposer_id="admin",
        options=["yes", "no"],
        voting_method=method,
        eligible_voters=eligible,
    )


class TestVotingEngine:
    def test_create_proposal(self, engine):
        engine.create_proposal(make_proposal())
        with pytest.raises(ValueError, match="already exists"):
            engine.create_proposal(make_proposal())

    def test_proposal_needs_options(self, engine):
        bad = Proposal("p", "T", "D", "a", options=["only_one"])
        with pytest.raises(ValueError, match="at least 2"):
            engine.create_proposal(bad)

    def test_simple_majority(self, engine):
        engine.create_proposal(make_proposal(eligible=10))
        for i in range(6):
            engine.cast_vote("p1", Vote(voter_id=f"v{i}", choice="yes"))
        for i in range(4):
            engine.cast_vote("p1", Vote(voter_id=f"n{i}", choice="no"))
        result = engine.tally("p1")
        assert result.winner == "yes"
        assert result.quorum_met

    def test_no_quorum(self, engine):
        engine.create_proposal(make_proposal(eligible=100))
        engine.cast_vote("p1", Vote(voter_id="v1", choice="yes"))
        result = engine.tally("p1")
        assert not result.quorum_met

    def test_duplicate_voter_raises(self, engine):
        engine.create_proposal(make_proposal())
        engine.cast_vote("p1", Vote(voter_id="v1", choice="yes"))
        with pytest.raises(ValueError, match="already voted"):
            engine.cast_vote("p1", Vote(voter_id="v1", choice="no"))

    def test_invalid_choice_raises(self, engine):
        engine.create_proposal(make_proposal())
        with pytest.raises(ValueError, match="Invalid choice"):
            engine.cast_vote("p1", Vote(voter_id="v1", choice="maybe"))

    def test_supermajority_pass(self, engine):
        engine.create_proposal(make_proposal(method=VotingMethod.SUPERMAJORITY, eligible=9))
        for i in range(7):
            engine.cast_vote("p1", Vote(voter_id=f"v{i}", choice="yes"))
        for i in range(2):
            engine.cast_vote("p1", Vote(voter_id=f"n{i}", choice="no"))
        result = engine.tally("p1")
        assert result.winner == "yes"

    def test_supermajority_fail(self, engine):
        engine.create_proposal(make_proposal(method=VotingMethod.SUPERMAJORITY, eligible=10))
        for i in range(6):
            engine.cast_vote("p1", Vote(voter_id=f"v{i}", choice="yes"))
        for i in range(4):
            engine.cast_vote("p1", Vote(voter_id=f"n{i}", choice="no"))
        result = engine.tally("p1")
        assert result.winner is None  # 60% < 66.7%

    def test_unanimous(self, engine):
        engine.create_proposal(make_proposal(method=VotingMethod.UNANIMOUS, eligible=5))
        for i in range(5):
            engine.cast_vote("p1", Vote(voter_id=f"v{i}", choice="yes"))
        result = engine.tally("p1")
        assert result.winner == "yes"

    def test_unanimous_fails_with_dissent(self, engine):
        engine.create_proposal(make_proposal(method=VotingMethod.UNANIMOUS, eligible=5))
        for i in range(4):
            engine.cast_vote("p1", Vote(voter_id=f"v{i}", choice="yes"))
        engine.cast_vote("p1", Vote(voter_id="dissent", choice="no"))
        result = engine.tally("p1")
        assert result.winner is None

    def test_weighted_voting(self, engine):
        prop = make_proposal(method=VotingMethod.WEIGHTED, eligible=3)
        engine.create_proposal(prop)
        engine.cast_vote("p1", Vote(voter_id="v1", choice="yes", weight=10.0))
        engine.cast_vote("p1", Vote(voter_id="v2", choice="no", weight=1.0))
        engine.cast_vote("p1", Vote(voter_id="v3", choice="no", weight=1.0))
        result = engine.tally("p1")
        assert result.winner == "yes"  # Weight 10 vs 2

    def test_ranked_choice(self, engine):
        prop = Proposal("rc", "Ranked", "D", "a",
                        options=["A", "B", "C"],
                        voting_method=VotingMethod.RANKED_CHOICE,
                        eligible_voters=5)
        engine.create_proposal(prop)
        engine.cast_vote("rc", Vote(voter_id="v1", choice="A", rank=["A", "B", "C"]))
        engine.cast_vote("rc", Vote(voter_id="v2", choice="A", rank=["A", "B", "C"]))
        engine.cast_vote("rc", Vote(voter_id="v3", choice="B", rank=["B", "C", "A"]))
        engine.cast_vote("rc", Vote(voter_id="v4", choice="C", rank=["C", "B", "A"]))
        engine.cast_vote("rc", Vote(voter_id="v5", choice="C", rank=["C", "B", "A"]))
        result = engine.tally("rc")
        assert result.rounds is not None
        assert result.winner is not None

    def test_approval_voting(self, engine):
        prop = Proposal("ap", "Approval", "D", "a",
                        options=["A", "B", "C"],
                        voting_method=VotingMethod.APPROVAL,
                        eligible_voters=3)
        engine.create_proposal(prop)
        engine.cast_vote("ap", Vote(voter_id="v1", choice="A", approvals=["A", "B"]))
        engine.cast_vote("ap", Vote(voter_id="v2", choice="B", approvals=["B", "C"]))
        engine.cast_vote("ap", Vote(voter_id="v3", choice="B", approvals=["A", "B"]))
        result = engine.tally("ap")
        assert result.winner == "B"  # B has 3 approvals


class TestConsensusModel:
    def test_no_ratings_raises(self, consensus):
        consensus.set_options(["A", "B"])
        with pytest.raises(ValueError, match="No ratings"):
            consensus.compute_consensus()

    def test_perfect_consensus(self, consensus):
        consensus.set_options(["A", "B"])
        consensus.submit_rating("p1", {"A": 8.0, "B": 3.0})
        consensus.submit_rating("p2", {"A": 8.0, "B": 3.0})
        result = consensus.compute_consensus()
        assert result["consensus_level"] == 1.0
        assert result["recommendation"] == "A"

    def test_split_opinion(self, consensus):
        consensus.set_options(["A", "B"])
        consensus.submit_rating("p1", {"A": 10.0, "B": 0.0})
        consensus.submit_rating("p2", {"A": 0.0, "B": 10.0})
        result = consensus.compute_consensus()
        assert result["consensus_level"] < 1.0
        assert result["spread"]["A"] > 0.0

    def test_convergence_check(self, consensus):
        consensus.set_options(["A", "B"])
        consensus.submit_rating("p1", {"A": 7.0, "B": 5.0})
        prev = {"A": 7.0, "B": 5.0}
        assert consensus.check_convergence(prev)

    def test_invalid_rating_range(self, consensus):
        consensus.set_options(["A"])
        with pytest.raises(ValueError, match="must be in"):
            consensus.submit_rating("p1", {"A": 15.0})

    def test_missing_option_rating(self, consensus):
        consensus.set_options(["A", "B"])
        with pytest.raises(ValueError, match="Missing rating"):
            consensus.submit_rating("p1", {"A": 5.0})
