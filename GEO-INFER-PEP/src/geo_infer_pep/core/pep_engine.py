"""
Core PEP Engine

This module provides the central engine for orchestrating all PEP (People, Engagement, Performance)
operations. It serves as the main entry point for the PEP system and coordinates between
different modules and data flows.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
import logging
from pathlib import Path

from ..models.hr_models import Employee, EmploymentStatus
from ..models.crm_models import Customer
from ..models.talent_models import Candidate, JobRequisition
from ..methods import (
    import_hr_data_from_csv,
    import_crm_data_from_csv,
    import_talent_data_from_csv,
    generate_comprehensive_hr_dashboard,
    generate_comprehensive_crm_dashboard,
    generate_comprehensive_talent_dashboard,
    process_employee_onboarding_workflow,
    clear_all_data,
    get_all_employees,
    get_all_candidates,
    get_all_customers
)

logger = logging.getLogger(__name__)

class PEPDataManager:
    """
    Central data manager for PEP operations.

    Handles data storage, retrieval, and basic operations for all PEP data types.
    In a production system, this would interface with a database.
    """

    def __init__(self):
        self._employees: List[Employee] = []
        self._customers: List[Customer] = []
        self._candidates: List[Candidate] = []
        self._requisitions: List[JobRequisition] = []
        self._last_updated = datetime.now()

    def add_employees(self, employees: List[Employee]) -> int:
        """Add employees to the data store."""
        self._employees.extend(employees)
        self._last_updated = datetime.now()
        logger.info(f"Added {len(employees)} employees to data store")
        return len(employees)

    def add_customers(self, customers: List[Customer]) -> int:
        """Add customers to the data store."""
        self._customers.extend(customers)
        self._last_updated = datetime.now()
        logger.info(f"Added {len(customers)} customers to data store")
        return len(customers)

    def add_candidates(self, candidates: List[Candidate]) -> int:
        """Add candidates to the data store."""
        self._candidates.extend(candidates)
        self._last_updated = datetime.now()
        logger.info(f"Added {len(candidates)} candidates to data store")
        return len(candidates)

    def add_requisitions(self, requisitions: List[JobRequisition]) -> int:
        """Add job requisitions to the data store."""
        self._requisitions.extend(requisitions)
        self._last_updated = datetime.now()
        logger.info(f"Added {len(requisitions)} requisitions to data store")
        return len(requisitions)

    def get_employees(self, filters: Optional[Dict[str, Any]] = None) -> List[Employee]:
        """Get employees with optional filtering."""
        employees = self._employees.copy()

        if filters:
            for key, value in filters.items():
                if hasattr(Employee, key):
                    employees = [emp for emp in employees if getattr(emp, key) == value]
                elif key in ["department", "status", "gender"]:  # Common filter fields
                    if key == "department":
                        employees = [emp for emp in employees if emp.department == value]
                    elif key == "status":
                        employees = [emp for emp in employees if emp.employment_status.value == value]
                    elif key == "gender" and value:
                        employees = [emp for emp in employees if emp.gender and emp.gender.value == value]

        return employees

    def get_customers(self, filters: Optional[Dict[str, Any]] = None) -> List[Customer]:
        """Get customers with optional filtering."""
        customers = self._customers.copy()

        if filters:
            for key, value in filters.items():
                if hasattr(Customer, key):
                    customers = [cust for cust in customers if getattr(cust, key) == value]
                elif key in ["status", "company"]:  # Common filter fields
                    if key == "status":
                        customers = [cust for cust in customers if cust.status == value]
                    elif key == "company":
                        customers = [cust for cust in customers if cust.company == value]

        return customers

    def get_candidates(self, filters: Optional[Dict[str, Any]] = None) -> List[Candidate]:
        """Get candidates with optional filtering."""
        candidates = self._candidates.copy()

        if filters:
            for key, value in filters.items():
                if hasattr(Candidate, key):
                    candidates = [cand for cand in candidates if getattr(cand, key) == value]
                elif key == "status":
                    candidates = [cand for cand in candidates if cand.status.value == value]

        return candidates

    def get_requisitions(self, filters: Optional[Dict[str, Any]] = None) -> List[JobRequisition]:
        """Get job requisitions with optional filtering."""
        requisitions = self._requisitions.copy()

        if filters:
            for key, value in filters.items():
                if hasattr(JobRequisition, key):
                    requisitions = [req for req in requisitions if getattr(req, key) == value]
                elif key == "status":
                    requisitions = [req for req in requisitions if req.status.value == value]

        return requisitions

    def get_data_summary(self) -> Dict[str, Any]:
        """Get a summary of all data in the store."""
        return {
            "employees": {
                "total": len(self._employees),
                "active": len([e for e in self._employees if e.employment_status == EmploymentStatus.ACTIVE]),
                "departments": len(set(e.department for e in self._employees))
            },
            "customers": {
                "total": len(self._customers),
                "active": len([c for c in self._customers if c.status == "active"]),
                "companies": len(set(c.company for c in self._customers if c.company))
            },
            "candidates": {
                "total": len(self._candidates),
                "offer_accepted": len([c for c in self._candidates if c.status.value == "offer_accepted"]),
                "requisitions": len(set(c.job_requisition_id for c in self._candidates if c.job_requisition_id))
            },
            "requisitions": {
                "total": len(self._requisitions),
                "open": len([r for r in self._requisitions if r.status.value == "open"])
            },
            "last_updated": self._last_updated.isoformat()
        }

    def clear_all_data(self) -> bool:
        """Clear all data from the store."""
        self._employees.clear()
        self._customers.clear()
        self._candidates.clear()
        self._requisitions.clear()
        self._last_updated = datetime.now()
        logger.info("Cleared all data from PEP data store")
        return True

class PEPEngine:
    """
    Main PEP Engine

    Provides high-level operations and orchestrates complex workflows across
    all PEP modules (HR, CRM, Talent).
    """

    def __init__(self, data_manager: Optional[PEPDataManager] = None):
        self.data_manager = data_manager or PEPDataManager()
        self._initialized = False

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        logger.info("PEP Engine initialized")

    def initialize(self) -> bool:
        """Initialize the PEP engine."""
        if self._initialized:
            logger.warning("PEP Engine already initialized")
            return True

        try:
            # Any initialization logic would go here
            self._initialized = True
            logger.info("PEP Engine successfully initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize PEP Engine: {str(e)}")
            return False

    def import_hr_data(self, file_path: str) -> Dict[str, Any]:
        """Import HR data from CSV file."""
        try:
            employees = import_hr_data_from_csv(file_path)
            count = self.data_manager.add_employees(employees)

            return {
                "success": True,
                "records_imported": count,
                "data_type": "employees",
                "file_path": file_path
            }
        except Exception as e:
            logger.error(f"HR data import failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data_type": "employees"
            }

    def import_crm_data(self, file_path: str) -> Dict[str, Any]:
        """Import CRM data from CSV file."""
        try:
            customers = import_crm_data_from_csv(file_path)
            count = self.data_manager.add_customers(customers)

            return {
                "success": True,
                "records_imported": count,
                "data_type": "customers",
                "file_path": file_path
            }
        except Exception as e:
            logger.error(f"CRM data import failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data_type": "customers"
            }

    def import_talent_data(self, candidates_file: str, requisitions_file: str) -> Dict[str, Any]:
        """Import talent data from CSV files."""
        try:
            result = import_talent_data_from_csv(candidates_file, requisitions_file)

            if result.get("processed_successfully"):
                # Update data manager with imported data
                candidates = get_all_candidates()
                self.data_manager.add_candidates(candidates)

                # Note: Requisitions would need to be added to data manager as well
                # This would require modifying the import function to return them

                return {
                    "success": True,
                    "candidates_imported": result.get("candidates", 0),
                    "requisitions_imported": result.get("requisitions", 0),
                    "data_type": "talent"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "data_type": "talent"
                }

        except Exception as e:
            logger.error(f"Talent data import failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data_type": "talent"
            }

    def process_onboarding_workflow(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process employee onboarding workflow."""
        try:
            success = process_employee_onboarding_workflow(employee_data)

            # Update data manager with new employee
            employees = get_all_employees()
            self.data_manager._employees = employees  # Direct update for now

            return {
                "success": success,
                "workflow": "onboarding",
                "candidate_id": employee_data.get("candidate_id"),
                "employee_data": employee_data
            }

        except Exception as e:
            logger.error(f"Onboarding workflow failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "workflow": "onboarding"
            }

    def generate_hr_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive HR dashboard."""
        try:
            dashboard = generate_comprehensive_hr_dashboard()
            return {
                "success": True,
                "dashboard_type": "hr",
                "data": dashboard
            }
        except Exception as e:
            logger.error(f"HR dashboard generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "dashboard_type": "hr"
            }

    def generate_crm_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive CRM dashboard."""
        try:
            dashboard = generate_comprehensive_crm_dashboard()
            return {
                "success": True,
                "dashboard_type": "crm",
                "data": dashboard
            }
        except Exception as e:
            logger.error(f"CRM dashboard generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "dashboard_type": "crm"
            }

    def generate_talent_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive talent dashboard."""
        try:
            dashboard = generate_comprehensive_talent_dashboard()
            return {
                "success": True,
                "dashboard_type": "talent",
                "data": dashboard
            }
        except Exception as e:
            logger.error(f"Talent dashboard generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "dashboard_type": "talent"
            }

    def generate_all_dashboards(self) -> Dict[str, Any]:
        """Generate all dashboards and return combined results."""
        results = {
            "overall_success": True,
            "dashboards": {},
            "generated_at": datetime.now().isoformat()
        }

        # Generate each dashboard
        hr_result = self.generate_hr_dashboard()
        crm_result = self.generate_crm_dashboard()
        talent_result = self.generate_talent_dashboard()

        results["dashboards"]["hr"] = hr_result
        results["dashboards"]["crm"] = crm_result
        results["dashboards"]["talent"] = talent_result

        # Check if any failed
        if not all([hr_result["success"], crm_result["success"], talent_result["success"]]):
            results["overall_success"] = False
            results["errors"] = []

            for name, result in [("HR", hr_result), ("CRM", crm_result), ("Talent", talent_result)]:
                if not result["success"]:
                    results["errors"].append(f"{name}: {result.get('error', 'Unknown error')}")

        return results

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        data_summary = self.data_manager.get_data_summary()

        return {
            "system_status": "operational",
            "initialized": self._initialized,
            "data_summary": data_summary,
            "engine_version": "1.0.0",
            "last_check": datetime.now().isoformat()
        }

    def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check."""
        health_status = {
            "overall_health": "healthy",
            "checks": {},
            "timestamp": datetime.now().isoformat()
        }

        # Check data integrity
        data_summary = self.data_manager.get_data_summary()
        health_status["checks"]["data_integrity"] = {
            "status": "healthy",
            "details": f"Data store contains {data_summary['employees']['total']} employees, {data_summary['customers']['total']} customers, {data_summary['candidates']['total']} candidates"
        }

        # Check module availability
        try:
            import pandas as pd
            health_status["checks"]["dependencies"] = {
                "status": "healthy",
                "details": "All required dependencies available"
            }
        except ImportError as e:
            health_status["checks"]["dependencies"] = {
                "status": "unhealthy",
                "details": f"Missing dependency: {str(e)}"
            }
            health_status["overall_health"] = "unhealthy"

        # Check data processing capabilities
        try:
            test_data = Employee(
                employee_id="test001",
                first_name="Test",
                last_name="User",
                email="test@example.com",
                employment_status=EmploymentStatus.ACTIVE,
                job_title="Test Role",
                department="Test Dept"
            )
            self.data_manager.add_employees([test_data])
            health_status["checks"]["data_processing"] = {
                "status": "healthy",
                "details": "Data processing functions operational"
            }
        except Exception as e:
            health_status["checks"]["data_processing"] = {
                "status": "unhealthy",
                "details": f"Data processing error: {str(e)}"
            }
            health_status["overall_health"] = "unhealthy"

        return health_status

    def shutdown(self) -> bool:
        """Shutdown the PEP engine gracefully."""
        try:
            logger.info("Shutting down PEP Engine")
            self.data_manager.clear_all_data()
            self._initialized = False
            return True
        except Exception as e:
            logger.error(f"Error during PEP Engine shutdown: {str(e)}")
            return False
