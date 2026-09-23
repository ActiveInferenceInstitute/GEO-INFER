"""Unit tests for PEPOrchestrator workflow create/get/execute (GS19-18)."""

from datetime import datetime, timedelta

import pytest

from geo_infer_pep.core.data_store import PEPDataManager
from geo_infer_pep.core.orchestrator import PEPOrchestrator, WorkflowStatus
from geo_infer_pep.core.pep_engine import PEPEngine
from geo_infer_pep.models.talent_models import Candidate, CandidateStatus, Offer


def _accepted_candidate(candidate_id: str = "cand-42") -> Candidate:
    return Candidate(
        candidate_id=candidate_id,
        first_name="New",
        last_name="Hire",
        email="new.hire@example.com",
        applied_at=datetime.now() - timedelta(days=7),
        status=CandidateStatus.OFFER_ACCEPTED,
        offer=Offer(
            offer_id="offer-1",
            offered_at=(datetime.now() - timedelta(days=9)).date(),
            accepted_at=(datetime.now() - timedelta(days=1)).date(),
        ),
    )


@pytest.fixture
def orchestrator() -> PEPOrchestrator:
    """Orchestrator wired to an isolated PEPDataManager-backed engine."""
    engine = PEPEngine(data_manager=PEPDataManager())
    return PEPOrchestrator(pep_engine=engine)


def test_create_workflow_returns_id_and_pending_status(orchestrator):
    workflow_id = orchestrator.create_employee_onboarding_workflow("cand-42")

    assert workflow_id.startswith("onboarding_cand-42_")
    assert workflow_id in orchestrator.workflows
    workflow = orchestrator.workflows[workflow_id]
    assert workflow["status"] == WorkflowStatus.PENDING
    assert workflow["context"]["candidate_id"] == "cand-42"
    assert [step.name for step in workflow["steps"]][0] == "validate_candidate"


def test_get_workflow_status_reports_pending_steps(orchestrator):
    workflow_id = orchestrator.create_employee_onboarding_workflow("cand-42")

    status = orchestrator.get_workflow_status(workflow_id)

    assert status["success"] is True
    assert status["workflow_id"] == workflow_id
    assert status["status"] == "pending"
    assert status["steps"][0]["name"] == "validate_candidate"
    assert all(step["status"] == "pending" for step in status["steps"])


def test_get_workflow_status_unknown_id_reports_error(orchestrator):
    status = orchestrator.get_workflow_status("no-such-workflow")
    assert status == {
        "success": False,
        "error": "Workflow no-such-workflow not found",
    }


def test_execute_workflow_fails_when_candidate_missing(orchestrator):
    workflow_id = orchestrator.create_employee_onboarding_workflow("cand-ghost")

    result = orchestrator.execute_workflow(workflow_id)

    assert result["success"] is False
    assert result["failed_step"] == "validate_candidate"
    assert "candidate cand-ghost not found" in result["error"]
    assert orchestrator.workflows[workflow_id]["status"] == WorkflowStatus.FAILED
    assert orchestrator.workflows[workflow_id]["failed_step"] == "validate_candidate"


def test_execute_workflow_completes_all_steps(orchestrator, monkeypatch):
    candidate = _accepted_candidate("cand-42")
    orchestrator.engine.data_manager.add_candidates([candidate])

    def _record_employee(employee_data):
        assert employee_data["candidate_id"] == "cand-42"
        return True

    monkeypatch.setattr(
        "geo_infer_pep.methods.process_employee_onboarding_workflow",
        _record_employee,
    )

    workflow_id = orchestrator.create_employee_onboarding_workflow("cand-42")
    result = orchestrator.execute_workflow(workflow_id)

    assert result["success"] is True
    assert result["workflow_id"] == workflow_id
    assert result["steps_executed"] == result["total_steps"] == 8
    status = orchestrator.get_workflow_status(workflow_id)
    assert status["status"] == "completed"
    assert status["completed_at"] is not None
    assert all(step["status"] == "completed" for step in status["steps"])


def test_execute_unknown_workflow_returns_error(orchestrator):
    result = orchestrator.execute_workflow("ghost-workflow")
    assert result == {
        "success": False,
        "error": "Workflow ghost-workflow not found",
        "workflow_id": "ghost-workflow",
    }
