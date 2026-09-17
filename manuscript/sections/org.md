## GEO-INFER-ORG — Organizational Structures and Governance

GEO-INFER-ORG models organizational structures, governance frameworks, and community processes for geospatial initiatives (per its `README.md`). Its package `geo_infer_org` is deliberately minimal — a single `core/` subpackage plus `__init__.py`, at approximately 1,494 lines of Python — concentrating the module on data structures and decision algorithms rather than service plumbing.

The public interface, verified from `__init__.py`, exports twenty-one symbols across three clusters. Structure: `OrganizationModel`, `OrgUnit`, `Role`, `Resource`, `OrgStructureType`, `RoleLevel`, and `OrgMetrics` for representing hierarchies and their measured properties. Decision-making: `VotingEngine`, `ConsensusModel`, `VotingMethod`, `DecisionStatus`, `Vote`, `Proposal`, and `VotingResult` for executing and recording collective choices. Collaboration: `CollaborationNetwork`, `TeamFormation`, `CollaborationEdge`, `CollaborationType`, `TeamMember`, `NetworkMetrics`, and `TeamFormationResult` for analyzing and composing teams as graphs.

The test census counts 7 test files with 17 test classes and 97 test functions, matching the module's three clusters — structural model tests, voting and consensus path tests, and collaboration-network tests.

In the root README's Module Themes, ORG belongs to Governance, Risk & Domain alongside METAGOV, NORMS, PEP, REQ, SEC, and RISK. Its role is the organizational layer beneath the governance theme: METAGOV designs governance regimes and NORMS encodes rules, while ORG supplies the concrete organizational objects — units, roles, votes, teams — that such regimes operate on, sized small enough that its entire decision logic can be reviewed in one sitting.
