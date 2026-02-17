"""Tests for collaboration networks and team formation."""

import pytest
from geo_infer_org.core.collaboration import (
    CollaborationNetwork,
    TeamFormation,
    CollaborationEdge,
    CollaborationType,
    TeamMember,
)


@pytest.fixture
def network():
    net = CollaborationNetwork()
    # Create a small network: A-B, B-C, A-C, C-D
    net.add_edge(CollaborationEdge("A", "B", CollaborationType.TASK_COORDINATION, strength=1.0))
    net.add_edge(CollaborationEdge("B", "C", CollaborationType.KNOWLEDGE_SHARE, strength=2.0))
    net.add_edge(CollaborationEdge("A", "C", CollaborationType.JOINT_PROJECT, strength=1.5))
    net.add_edge(CollaborationEdge("C", "D", CollaborationType.KNOWLEDGE_SHARE, strength=1.0))
    return net


@pytest.fixture
def team_formation():
    tf = TeamFormation()
    tf.add_members([
        TeamMember("m1", "Alice", skills=["python", "ml", "stats"], unit_id="data"),
        TeamMember("m2", "Bob", skills=["python", "devops", "docker"], unit_id="infra"),
        TeamMember("m3", "Carol", skills=["javascript", "react", "css"], unit_id="frontend"),
        TeamMember("m4", "Dave", skills=["python", "sql", "analytics"], unit_id="data"),
        TeamMember("m5", "Eve", skills=["java", "spring", "sql"], unit_id="backend"),
    ])
    return tf


class TestCollaborationNetwork:
    def test_metrics(self, network):
        metrics = network.compute_metrics()
        assert metrics.node_count == 4
        assert metrics.edge_count == 4
        assert metrics.density > 0
        assert metrics.avg_degree > 0
        assert metrics.connected_components == 1

    def test_empty_network(self):
        net = CollaborationNetwork()
        metrics = net.compute_metrics()
        assert metrics.node_count == 0

    def test_add_node_explicit(self):
        net = CollaborationNetwork()
        net.add_node("X")
        metrics = net.compute_metrics()
        assert metrics.node_count == 1
        assert metrics.connected_components == 1

    def test_clustering(self, network):
        # A-B, A-C, B-C form a triangle so clustering should be > 0
        metrics = network.compute_metrics()
        assert metrics.clustering_coefficient > 0

    def test_betweenness_centrality(self, network):
        centrality = network.compute_betweenness_centrality()
        assert len(centrality) == 4
        # C should have high centrality (bridges to D)
        assert centrality["C"] >= centrality["D"]

    def test_knowledge_flow(self, network):
        flow = network.get_knowledge_flow()
        assert "sources" in flow
        assert "sinks" in flow
        # B and C are sources of knowledge_share edges
        assert "B" in flow["sources"]
        # C is a sink (B->C)
        assert "C" in flow["sinks"]

    def test_most_central_nodes(self, network):
        metrics = network.compute_metrics()
        assert len(metrics.most_central_nodes) > 0


class TestTeamFormation:
    def test_form_team_full_coverage(self, team_formation):
        result = team_formation.form_team(
            required_skills=["python", "javascript", "sql"],
            max_size=5,
        )
        assert result.skill_coverage == 1.0
        assert len(result.team_members) >= 2

    def test_form_team_partial_coverage(self, team_formation):
        result = team_formation.form_team(
            required_skills=["python", "rust", "haskell"],
        )
        assert result.skill_coverage < 1.0

    def test_team_diversity(self, team_formation):
        result = team_formation.form_team(
            required_skills=["python", "javascript", "java"],
            prefer_diverse_units=True,
        )
        assert result.team_diversity > 0.0

    def test_no_members_raises(self):
        tf = TeamFormation()
        with pytest.raises(ValueError, match="No members"):
            tf.form_team(["python"])

    def test_max_size_respected(self, team_formation):
        result = team_formation.form_team(
            required_skills=["python", "javascript", "java", "sql", "docker", "react"],
            max_size=2,
        )
        assert len(result.team_members) <= 2

    def test_skill_gap_analysis(self, team_formation):
        gap = team_formation.compute_skill_gap(["python", "rust", "sql"])
        assert "python" in gap["covered"]
        assert "rust" in gap["missing"]
        assert gap["coverage_ratio"] < 1.0
        assert gap["skill_frequency"]["python"] >= 2  # Multiple python users

    def test_overall_score_range(self, team_formation):
        result = team_formation.form_team(["python", "sql"])
        assert 0.0 <= result.overall_score <= 1.0
        assert 0.0 <= result.coordination_cost <= 1.0
