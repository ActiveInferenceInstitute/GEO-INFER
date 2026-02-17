"""Tests for GEO-INFER-ORG module initialization and imports."""

import pytest


class TestOrgImports:
    def test_import_module(self):
        import geo_infer_org
        assert geo_infer_org.__version__ == "0.1.0"

    def test_import_organization(self):
        from geo_infer_org import OrganizationModel, OrgUnit, Role, OrgStructureType, RoleLevel
        assert OrganizationModel is not None
        model = OrganizationModel()
        assert model is not None

    def test_import_governance(self):
        from geo_infer_org import VotingEngine, ConsensusModel, VotingMethod, Vote, Proposal
        assert VotingEngine is not None
        assert ConsensusModel is not None

    def test_import_collaboration(self):
        from geo_infer_org import CollaborationNetwork, TeamFormation, TeamMember, CollaborationEdge
        assert CollaborationNetwork is not None
        assert TeamFormation is not None

    def test_core_imports(self):
        from geo_infer_org.core import OrganizationModel, VotingEngine, CollaborationNetwork
        assert OrganizationModel is not None
        assert VotingEngine is not None
        assert CollaborationNetwork is not None
