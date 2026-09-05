"""Basic governance example using GEO-INFER-ORG.

Demonstrates the real public API:
- Building an organizational structure with OrganizationModel / OrgUnit
- Running a ranked-choice (IRV) vote with VotingEngine
- Scoring consensus ratings with ConsensusModel
"""

from geo_infer_org import (
    OrganizationModel,
    OrgUnit,
    VotingEngine,
    ConsensusModel,
    VotingMethod,
    Proposal,
    Vote,
)


def build_organization() -> OrganizationModel:
    """Create a small two-level org structure."""
    model = OrganizationModel()
    model.add_unit(OrgUnit(unit_id="hq", name="Regional Authority"))
    model.add_unit(OrgUnit(unit_id="planning", name="Planning", parent_id="hq"))
    model.add_unit(OrgUnit(unit_id="emergency", name="Emergency Response", parent_id="hq"))
    return model


def run_ranked_choice_vote() -> None:
    """Run an IRV vote among three options and print the outcome."""
    engine = VotingEngine()
    engine.create_proposal(Proposal(
        proposal_id="site-plan",
        title="Site plan",
        description="Choose the expansion site",
        proposer_id="hq",
        options=["site_a", "site_b", "site_c"],
        voting_method=VotingMethod.RANKED_CHOICE,
    ))
    ballots = {
        "voter-1": ["site_a", "site_b", "site_c"],
        "voter-2": ["site_b", "site_a", "site_c"],
        "voter-3": ["site_a", "site_c", "site_b"],
        "voter-4": ["site_c", "site_b", "site_a"],
    }
    for voter_id, rank in ballots.items():
        engine.cast_vote("site-plan", Vote(voter_id, rank[0], rank=rank))

    result = engine.tally("site-plan")
    for i, round_counts in enumerate(result.rounds or [], start=1):
        print(f"Round {i}: {round_counts}")
    print(f"IRV winner: {result.winner}")


def run_consensus_rounds() -> None:
    """Drive two consensus rounds and check convergence."""
    consensus = ConsensusModel(convergence_threshold=0.5)
    consensus.set_options(["option_alpha", "option_beta"])

    round1 = {
        "p1": {"option_alpha": 7.0, "option_beta": 5.0},
        "p2": {"option_alpha": 6.5, "option_beta": 5.5},
    }
    for participant, ratings in round1.items():
        consensus.submit_rating(participant, ratings)
    previous = consensus.compute_consensus()["option_scores"]
    print(f"Round 1 scores: {previous}")

    round2 = {
        "p1": {"option_alpha": 7.2, "option_beta": 5.1},
        "p2": {"option_alpha": 6.7, "option_beta": 5.4},
    }
    for participant, ratings in round2.items():
        consensus.submit_rating(participant, ratings)
    current = consensus.compute_consensus()
    print(f"Round 2 scores: {current['option_scores']}")
    print(f"Consensus level: {current['consensus_level']}")
    print(f"Converged: {consensus.check_convergence(previous)}")


def main() -> None:
    """Run the basic governance example."""
    print("GEO-INFER-ORG: Basic Governance Example")
    print("-" * 40)

    model = build_organization()
    print(f"Units: {sorted(model.to_dict()['units'].keys())}")

    run_ranked_choice_vote()
    run_consensus_rounds()


if __name__ == "__main__":
    main()
