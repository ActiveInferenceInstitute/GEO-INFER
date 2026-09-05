"""Shared in-memory data store for GEO-INFER-PEP.

This module owns the canonical in-memory data lists for HR, CRM, and Talent
data. Both the high-level ``geo_infer_pep.methods`` layer and the FastAPI
``geo_infer_pep.api`` layer operate on the same ``pep_data_manager`` singleton,
so the two layers always observe identical data. ``PEPDataManager`` instances
created directly remain instance-scoped for isolated use (e.g. tests).
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from ..models.hr_models import Employee
from ..models.crm_models import Customer
from ..models.talent_models import Candidate, JobRequisition

logger = logging.getLogger(__name__)


def _validate_filter_keys(
    model: Any, filters: Dict[str, Any], alias_keys: Optional[set] = None
) -> None:
    """Raise ``ValueError`` for filter keys that do not exist on the model.

    ``alias_keys`` are alternate names accepted by specific getters (e.g.
    ``"status"`` mapping to an enum field under a different attribute name).
    """
    allowed = set(model.model_fields.keys()) | (alias_keys or set())
    unknown = set(filters.keys()) - allowed
    if unknown:
        raise ValueError(
            f"Unknown filter key(s) {sorted(unknown)} for {model.__name__}; "
            f"allowed keys: {sorted(allowed)}"
        )


class PEPDataManager:
    """
    Manages the storage and retrieval of PEP data (employees, customers,
    candidates, requisitions).

    Provides basic in-memory storage, retrieval, and simple filtering for
    each data type. Instantiate the class for an isolated store, or use the
    module-level ``pep_data_manager`` singleton to share data across the
    methods and API layers.
    """

    def __init__(self) -> None:
        self._employees: List[Employee] = []
        self._customers: List[Customer] = []
        self._candidates: List[Candidate] = []
        self._requisitions: List[JobRequisition] = []
        self._last_updated = datetime.now()

    @property
    def employees(self) -> List[Employee]:
        """Live employee list (shared with any code holding this manager)."""
        return self._employees

    @property
    def customers(self) -> List[Customer]:
        """Live customer list (shared with any code holding this manager)."""
        return self._customers

    @property
    def candidates(self) -> List[Candidate]:
        """Live candidate list (shared with any code holding this manager)."""
        return self._candidates

    @property
    def requisitions(self) -> List[JobRequisition]:
        """Live requisition list (shared with any code holding this manager)."""
        return self._requisitions

    def add_employees(self, employees: List[Employee]) -> int:
        """Add employees to the data store."""
        self._employees.extend(employees)
        self._last_updated = datetime.now()
        return len(employees)

    def add_customers(self, customers: List[Customer]) -> int:
        """Add customers to the data store."""
        self._customers.extend(customers)
        self._last_updated = datetime.now()
        return len(customers)

    def add_candidates(self, candidates: List[Candidate]) -> int:
        """Add candidates to the data store."""
        self._candidates.extend(candidates)
        self._last_updated = datetime.now()
        return len(candidates)

    def add_requisitions(self, requisitions: List[JobRequisition]) -> int:
        """Add job requisitions to the data store."""
        self._requisitions.extend(requisitions)
        self._last_updated = datetime.now()
        return len(requisitions)

    def get_employees(self, filters: Optional[Dict[str, Any]] = None) -> List[Employee]:
        """Get employees with optional filtering.

        Supported filter keys are the ``Employee`` model fields plus the
        aliases ``"department"`` (same field), ``"status"`` (compared against
        ``employment_status`` value), and ``"gender"`` (compared against the
        gender enum value). Unknown keys raise ``ValueError``.
        """
        employees = self._employees.copy()

        if filters:
            _validate_filter_keys(Employee, filters, alias_keys={"status"})
            for key, value in filters.items():
                if key == "department":
                    employees = [
                        emp for emp in employees if emp.department == value
                    ]
                elif key == "status":
                    employees = [
                        emp
                        for emp in employees
                        if emp.employment_status.value == value
                    ]
                elif key == "gender":
                    employees = [
                        emp
                        for emp in employees
                        if emp.gender and emp.gender.value == value
                    ]
                else:
                    employees = [
                        emp for emp in employees if getattr(emp, key) == value
                    ]

        return employees

    def get_customers(self, filters: Optional[Dict[str, Any]] = None) -> List[Customer]:
        """Get customers with optional filtering."""
        customers = self._customers.copy()

        if filters:
            _validate_filter_keys(Customer, filters)
            for key, value in filters.items():
                customers = [
                    cust for cust in customers if getattr(cust, key) == value
                ]

        return customers

    def get_candidates(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> List[Candidate]:
        """Get candidates with optional filtering.

        The ``"status"`` alias compares against ``CandidateStatus`` values.
        """
        candidates = self._candidates.copy()

        if filters:
            _validate_filter_keys(Candidate, filters)
            for key, value in filters.items():
                if key == "status":
                    candidates = [
                        cand for cand in candidates if cand.status.value == value
                    ]
                else:
                    candidates = [
                        cand for cand in candidates if getattr(cand, key) == value
                    ]

        return candidates

    def get_requisitions(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> List[JobRequisition]:
        """Get requisitions with optional filtering.

        The ``"status"`` key compares against ``JobRequisitionStatus`` values.
        """
        requisitions = self._requisitions.copy()

        if filters:
            _validate_filter_keys(JobRequisition, filters)
            for key, value in filters.items():
                if key == "status":
                    requisitions = [
                        req for req in requisitions if req.status.value == value
                    ]
                else:
                    requisitions = [
                        req for req in requisitions if getattr(req, key) == value
                    ]

        return requisitions

    def get_data_summary(self) -> Dict[str, Any]:
        """Get a summary of all data in the store."""
        return {
            "employees": {
                "total": len(self._employees),
                "active": len(
                    [
                        emp
                        for emp in self._employees
                        if emp.employment_status.value == "active"
                    ]
                ),
                "departments": len({emp.department for emp in self._employees}),
            },
            "customers": {
                "total": len(self._customers),
                "active": len(
                    [cust for cust in self._customers if cust.status == "active"]
                ),
            },
            "candidates": {
                "total": len(self._candidates),
                "in_pipeline": len(
                    [
                        cand
                        for cand in self._candidates
                        if cand.status.value
                        not in ("hired", "rejected", "withdrawn")
                    ]
                ),
            },
            "requisitions": {
                "total": len(self._requisitions),
                "open": len(
                    [req for req in self._requisitions if req.status.value == "open"]
                ),
            },
            "last_updated": self._last_updated.isoformat(),
        }

    def clear_all_data(self) -> bool:
        """Clear all data from the store.

        Destructive: removes every employee, customer, candidate, and
        requisition record held by this manager.
        """
        logger.warning(
            "PEPDataManager.clear_all_data() called; deleting all in-memory records"
        )
        self._employees.clear()
        self._customers.clear()
        self._candidates.clear()
        self._requisitions.clear()
        self._last_updated = datetime.now()
        return True


#: Process-wide shared store used by ``geo_infer_pep.methods`` and the
#: FastAPI layer in ``geo_infer_pep.api`` so both surfaces see the same data.
pep_data_manager = PEPDataManager()
