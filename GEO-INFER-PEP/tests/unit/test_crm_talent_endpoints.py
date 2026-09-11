"""Unit tests for CRM customer and talent requisition CRUD endpoints."""

import asyncio
from datetime import date

import pytest
from fastapi import HTTPException

from geo_infer_pep.api.crm_endpoints import (
    create_customer,
    delete_customer,
    get_all_customers,
    get_customer,
    update_customer,
)
from geo_infer_pep.api.talent_endpoints import (
    create_requisition,
    delete_requisition,
    get_all_requisitions,
    get_requisition,
    update_requisition,
)
from geo_infer_pep.core.data_store import pep_data_manager as store
from geo_infer_pep.models.crm_models import Customer
from geo_infer_pep.models.talent_models import JobRequisition


@pytest.fixture
def empty_store():
    """Clear the shared in-memory store around each test."""
    store.clear_all_data()
    yield store
    store.clear_all_data()


def _customer(customer_id: str = "cust-1") -> Customer:
    return Customer(customer_id=customer_id, last_name="Doe", status="lead")


def _requisition(requisition_id: str = "req-1") -> JobRequisition:
    return JobRequisition(
        requisition_id=requisition_id,
        job_title="Data Engineer",
        department="Platform",
        opened_at=date(2026, 1, 5),
    )


def test_create_and_get_customer_roundtrip(empty_store):
    created = asyncio.run(create_customer(_customer()))
    assert created.customer_id == "cust-1"
    assert empty_store.customers[0].customer_id == "cust-1"

    fetched = asyncio.run(get_customer("cust-1"))
    assert fetched.last_name == "Doe"


def test_create_customer_rejects_duplicate_id(empty_store):
    asyncio.run(create_customer(_customer()))
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(create_customer(_customer()))
    assert exc_info.value.status_code == 409


def test_get_missing_customer_returns_404(empty_store):
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_customer("nope"))
    assert exc_info.value.status_code == 404


def test_update_customer_preserves_created_at(empty_store):
    original = asyncio.run(create_customer(_customer()))
    updated = _customer()
    updated.last_name = "Smith"

    result = asyncio.run(update_customer("cust-1", updated))

    assert result.last_name == "Smith"
    assert result.created_at == original.created_at
    assert result.updated_at >= original.updated_at
    assert empty_store.customers == [result]


def test_update_missing_customer_returns_404(empty_store):
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(update_customer("nope", _customer()))
    assert exc_info.value.status_code == 404


def test_delete_customer_removes_record(empty_store):
    asyncio.run(create_customer(_customer()))
    asyncio.run(create_customer(_customer("cust-2")))

    result = asyncio.run(delete_customer("cust-1"))
    assert result == {"deleted": "cust-1"}
    assert [c.customer_id for c in empty_store.customers] == ["cust-2"]

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(delete_customer("cust-1"))
    assert exc_info.value.status_code == 404


def test_customer_list_respects_limit_and_offset(empty_store):
    for index in range(3):
        asyncio.run(create_customer(_customer(f"cust-{index}")))

    page = asyncio.run(get_all_customers(limit=2, offset=1))
    assert [c.customer_id for c in page] == ["cust-1", "cust-2"]


def test_requisition_crud_roundtrip(empty_store):
    created = asyncio.run(create_requisition(_requisition()))
    assert created.job_title == "Data Engineer"

    fetched = asyncio.run(get_requisition("req-1"))
    assert fetched.department == "Platform"

    updated = _requisition()
    updated.job_title = "Senior Data Engineer"
    result = asyncio.run(update_requisition("req-1", updated))
    assert result.job_title == "Senior Data Engineer"

    deleted = asyncio.run(delete_requisition("req-1"))
    assert deleted == {"deleted": "req-1"}
    assert empty_store.requisitions == []


def test_create_requisition_rejects_duplicate_id(empty_store):
    asyncio.run(create_requisition(_requisition()))
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(create_requisition(_requisition()))
    assert exc_info.value.status_code == 409


def test_requisition_list_respects_limit_and_offset(empty_store):
    for index in range(3):
        asyncio.run(create_requisition(_requisition(f"req-{index}")))

    page = asyncio.run(get_all_requisitions(limit=1, offset=2))
    assert [r.requisition_id for r in page] == ["req-2"]
