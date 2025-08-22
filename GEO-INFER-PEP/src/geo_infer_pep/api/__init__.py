# API endpoints for GEO-INFER-PEP
from fastapi import APIRouter
from typing import Dict, Any

from .crm_endpoints import router as crm_router
from .hr_endpoints import router as hr_router
from .talent_endpoints import router as talent_router

# Create the main API router
api_router = APIRouter(prefix="/pep")

# Include module-specific routers
api_router.include_router(crm_router)
api_router.include_router(hr_router)
api_router.include_router(talent_router)

# Health and system endpoints
@api_router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """System health check endpoint."""
    from ..core.pep_engine import PEPEngine
    engine = PEPEngine()
    health_status = engine.run_health_check()
    return health_status

@api_router.get("/status", response_model=Dict[str, Any])
async def system_status():
    """Get comprehensive system status."""
    from ..core.pep_engine import PEPEngine
    engine = PEPEngine()
    return engine.get_system_status()

@api_router.get("/dashboard", response_model=Dict[str, Any])
async def system_dashboard():
    """Get comprehensive system dashboard."""
    from ..core.pep_engine import PEPEngine
    engine = PEPEngine()
    return engine.generate_all_dashboards()

# Onboarding workflow endpoints
@api_router.post("/workflows/onboarding/{candidate_id}", response_model=Dict[str, Any])
async def create_onboarding_workflow(candidate_id: str):
    """Create an onboarding workflow for a candidate."""
    from ..core.orchestrator import PEPOrchestrator
    orchestrator = PEPOrchestrator()
    workflow_id = orchestrator.create_employee_onboarding_workflow(candidate_id)
    return {"workflow_id": workflow_id, "status": "created"}

@api_router.get("/workflows/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow_status(workflow_id: str):
    """Get workflow status."""
    from ..core.orchestrator import PEPOrchestrator
    orchestrator = PEPOrchestrator()
    return orchestrator.get_workflow_status(workflow_id)

@api_router.post("/workflows/{workflow_id}/execute", response_model=Dict[str, Any])
async def execute_workflow(workflow_id: str):
    """Execute a workflow."""
    from ..core.orchestrator import PEPOrchestrator
    orchestrator = PEPOrchestrator()
    return orchestrator.execute_workflow(workflow_id)

# Performance management endpoints
@api_router.post("/performance/reviews", response_model=Dict[str, Any])
async def create_performance_review(review_data: Dict[str, Any]):
    """Create a performance review."""
    # This would integrate with performance management system
    return {"message": "Performance review created", "data": review_data}

@api_router.get("/performance/reviews/{employee_id}", response_model=Dict[str, Any])
async def get_performance_reviews(employee_id: str):
    """Get performance reviews for an employee."""
    # This would fetch from performance management system
    return {"employee_id": employee_id, "reviews": []}

# Learning & Development endpoints
@api_router.post("/learning/courses", response_model=Dict[str, Any])
async def create_learning_course(course_data: Dict[str, Any]):
    """Create a learning course."""
    return {"message": "Learning course created", "data": course_data}

@api_router.get("/learning/courses", response_model=Dict[str, Any])
async def get_learning_courses():
    """Get all learning courses."""
    return {"courses": []}

@api_router.post("/learning/enrollments", response_model=Dict[str, Any])
async def enroll_employee(enrollment_data: Dict[str, Any]):
    """Enroll employee in a learning course."""
    return {"message": "Employee enrolled", "data": enrollment_data}

# Conflict resolution endpoints
@api_router.post("/conflicts/cases", response_model=Dict[str, Any])
async def create_conflict_case(case_data: Dict[str, Any]):
    """Create a conflict resolution case."""
    return {"message": "Conflict case created", "data": case_data}

@api_router.get("/conflicts/cases", response_model=Dict[str, Any])
async def get_conflict_cases():
    """Get all conflict resolution cases."""
    return {"cases": []}

@api_router.put("/conflicts/cases/{case_id}", response_model=Dict[str, Any])
async def update_conflict_case(case_id: str, update_data: Dict[str, Any]):
    """Update a conflict resolution case."""
    return {"message": f"Conflict case {case_id} updated", "data": update_data}

# Survey endpoints
@api_router.post("/surveys", response_model=Dict[str, Any])
async def create_survey(survey_data: Dict[str, Any]):
    """Create a survey."""
    return {"message": "Survey created", "data": survey_data}

@api_router.get("/surveys/{survey_id}/responses", response_model=Dict[str, Any])
async def get_survey_responses(survey_id: str):
    """Get responses for a survey."""
    return {"survey_id": survey_id, "responses": []}

@api_router.post("/surveys/{survey_id}/responses", response_model=Dict[str, Any])
async def submit_survey_response(survey_id: str, response_data: Dict[str, Any]):
    """Submit a survey response."""
    return {"message": f"Response submitted for survey {survey_id}", "data": response_data}

# Data validation endpoints
@api_router.post("/validate/employee", response_model=Dict[str, Any])
async def validate_employee_data(employee_data: Dict[str, Any]):
    """Validate employee data."""
    from ..core.validator import PEPValidator
    from ..models.hr_models import Employee

    try:
        employee = Employee(**employee_data)
        validator = PEPValidator()
        result = validator.validate_employee(employee)
        return result.to_dict()
    except Exception as e:
        return {"is_valid": False, "errors": [str(e)], "error_count": 1}

@api_router.post("/validate/customer", response_model=Dict[str, Any])
async def validate_customer_data(customer_data: Dict[str, Any]):
    """Validate customer data."""
    from ..core.validator import PEPValidator
    from ..models.crm_models import Customer

    try:
        customer = Customer(**customer_data)
        validator = PEPValidator()
        result = validator.validate_customer(customer)
        return result.to_dict()
    except Exception as e:
        return {"is_valid": False, "errors": [str(e)], "error_count": 1}

@api_router.post("/validate/candidate", response_model=Dict[str, Any])
async def validate_candidate_data(candidate_data: Dict[str, Any]):
    """Validate candidate data."""
    from ..core.validator import PEPValidator
    from ..models.talent_models import Candidate

    try:
        candidate = Candidate(**candidate_data)
        validator = PEPValidator()
        result = validator.validate_candidate(candidate)
        return result.to_dict()
    except Exception as e:
        return {"is_valid": False, "errors": [str(e)], "error_count": 1}

__all__ = ["api_router"]

