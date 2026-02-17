"""Tests for PEP CRM data models."""
import pytest
from datetime import datetime

from geo_infer_pep.models.crm_models import (
    Customer,
    Address,
    InteractionLog,
)


class TestCustomer:
    def test_create_customer(self):
        customer = Customer(
            customer_id="cust-001",
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
        )
        assert customer.customer_id == "cust-001"
        assert customer.first_name == "Jane"

    def test_customer_with_address(self):
        addr = Address(
            street="123 Main St",
            city="San Francisco",
            state="CA",
            postal_code="94102",
            country="USA",
        )
        customer = Customer(
            customer_id="cust-002",
            first_name="John",
            last_name="Smith",
            email="john@example.com",
            address=addr,
        )
        assert customer.address.city == "San Francisco"

    def test_customer_with_interactions(self):
        interaction = InteractionLog(
            summary="Initial meeting",
            channel="in_person",
        )
        customer = Customer(
            customer_id="cust-003",
            first_name="Alice",
            last_name="Johnson",
            email="alice@example.com",
            interaction_history=[interaction],
        )
        assert len(customer.interaction_history) == 1

    def test_customer_tags(self):
        customer = Customer(
            customer_id="cust-004",
            first_name="Bob",
            last_name="Wilson",
            email="bob@example.com",
            tags=["vip", "enterprise"],
        )
        assert "vip" in customer.tags


class TestAddress:
    def test_create_address(self):
        addr = Address(
            street="456 Oak Ave",
            city="New York",
            state="NY",
            postal_code="10001",
            country="USA",
        )
        assert addr.city == "New York"

    def test_partial_address(self):
        addr = Address(city="London", country="UK")
        assert addr.city == "London"
        assert addr.street is None


class TestInteractionLog:
    def test_create_log(self):
        log = InteractionLog(
            summary="Follow-up call",
            channel="phone",
        )
        assert log.summary == "Follow-up call"
        assert log.channel == "phone"
