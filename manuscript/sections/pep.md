## GEO-INFER-PEP — People Operations

GEO-INFER-PEP provides comprehensive people operations management including HR, CRM, talent acquisition, performance tracking, and community engagement (per its `README.md`). The package `geo_infer_pep` reflects that breadth in subpackages — `hr/`, `crm/`, `talent/`, `reporting/`, `visualizations/`, plus `api/`, `core/`, `models/`, and `utils/` with a `methods.py` entry module — totaling roughly 6,035 lines of Python, and it emits module-scoped `visualizations_output/`.

The public interface, verified from `__init__.py`, is the largest record-type surface in the M-Z range: domain entities `Employee`, `Candidate`, `Customer`, `Address`, `Compensation`, `JobRequisition`, `Interview`, `InterviewFeedback`, `Offer`, `PerformanceReview`, `InteractionLog`, and `JobHistoryEntry` with their status and category enums (`EmploymentStatus`, `CandidateStatus`, `InterviewType`, `JobRequisitionStatus`). Engines and orchestration come as `PEPEngine`, `PEPDataManager`, `PEPOrchestrator`, `PEPValidator`, plus functional helpers such as `process_employee_onboarding_workflow`, CSV importers for HR and CRM data, and dashboard/report generators (`generate_comprehensive_hr_dashboard`, `generate_quarterly_people_report`). Router objects `api_router`, `crm_router`, `hr_router`, and `talent_router` expose the HTTP surface.

The test census counts 16 test files with 15 test classes and 108 test functions covering workflows, validators, and reporting.

Under the root README's Module Themes, PEP belongs to Governance, Risk & Domain. Its role is the human layer of that theme: where ORG models structure and METAGOV designs governance, PEP tracks the people — employees, candidates, customers — whose records flow through those structures.
