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

class TestRankedChoiceIRV:
    def _rc_proposal(self, engine: VotingEngine, pid: str, options=None) -> None:
        engine.create_proposal(Proposal(
            pid, "RC", "Ranked choice", "proposer",
            options=options or ["A", "B", "C"],
            voting_method=VotingMethod.RANKED_CHOICE,
        ))

    def test_single_elimination_recovers_blocked_winner(self, engine):
        """Multi-elimination would wipe B, C, and D together and crown A;
        standard single-elimination IRV transfers D's votes to B, who wins."""
        self._rc_proposal(engine, "rc1", options=["A", "B", "C", "D"])
        ballots = (
            [["A", "C", "B"]] * 4
            + [["B", "C", "A"]] * 2
            + [["C", "B", "A"]] * 2
            + [["D", "B", "A"]]
        )
        for i, rank in enumerate(ballots):
            engine.cast_vote("rc1", Vote(f"v{i}", rank[0], rank=rank))
        result = engine.tally("rc1")
        assert result.winner == "B"
        assert result.rounds == [
            {"A": 4.0, "B": 2.0, "C": 2.0, "D": 1.0},
            {"A": 4.0, "B": 3.0, "C": 2.0},
            {"A": 4.0, "B": 5.0},
        ]

    def test_tie_break_is_deterministic(self, engine):
        """Candidates tied at the minimum eliminate the lexicographically
        first id, so repeated tallies agree."""
        self._rc_proposal(engine, "rc2")
        for i, rank in enumerate([
            ["B", "A", "C"],
            ["B", "A", "C"],
            ["A", "C", "B"],
            ["C", "A", "B"],
        ]):
            engine.cast_vote("rc2", Vote(f"v{i}", rank[0], rank=rank))
        r1 = engine.tally("rc2")
        r2 = engine.tally("rc2")
        assert r1.winner == r2.winner
        # A and C tie at the minimum in round 1; 'A' is eliminated first.
        assert r1.rounds is not None and r1.rounds[0] == {"A": 1.0, "B": 2.0, "C": 1.0}
        assert "A" not in r1.rounds[1]

    def test_eliminated_votes_transfer_to_survivor(self, engine):
        """A candidate eliminated mid-run transfers its ballots, letting a
        trailing candidate overtake the round-1 leader."""
        self._rc_proposal(engine, "rc3")
        ballots = (
            [["A", "C", "B"]] * 2
            + [["B", "A", "C"]] * 2
            + [["C", "B", "A"]]
        )
        for i, rank in enumerate(ballots):
            engine.cast_vote("rc3", Vote(f"v{i}", rank[0], rank=rank))
        result = engine.tally("rc3")
        # C is eliminated in round 1; its ballot transfers to B, who then
        # reaches a majority (3 of 5) over A.
        assert result.winner == "B"
        assert result.rounds is not None and len(result.rounds) == 2


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
