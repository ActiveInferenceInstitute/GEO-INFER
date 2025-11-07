import pytest
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import csv

from geo_infer_pep.models.crm_models import Customer, Address, InteractionLog
from geo_infer_pep.crm.importer import CSVCRMImporter
from geo_infer_pep.crm.transformer import clean_customer_data, enrich_customer_data, convert_customers_to_dataframe
from geo_infer_pep.reporting.crm_reports import generate_customer_segmentation_report, generate_lead_conversion_report
from geo_infer_pep.visualizations.crm_visuals import plot_customer_distribution_by_status, plot_customer_distribution_by_source

# Fixtures
@pytest.fixture
def sample_customer_data_list():
    """Provides a list of Customer Pydantic models for testing."""
    return [
        Customer(
            customer_id="cust1",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="5551234567",
            company="TestCorp",
            address=Address(street="123 Main St", city="Anytown", state="CA", postal_code="90210", country="USA"),
            tags=["test", "important"],
            status="active",
            source="website"
        ),
        Customer(
            customer_id="cust2",
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            status="lead",
            source="referral",
            tags=["new"]
        ),
        Customer(
            customer_id="cust3",
            first_name="Alpha",
            last_name="Beta",
            email="alpha.beta@example.com",
            status="active_customer", # For conversion report
            source="website",
            tags=["vip_customer"] # For enrichment and segmentation
        )
    ]

@pytest.fixture
def dummy_csv_file(tmp_path):
    """Creates a dummy CSV file for importer testing and returns its path."""
    csv_path = tmp_path / "dummy_crm.csv"
    headers = ['id', 'first_name', 'last_name', 'email', 'phone', 'company_name', 'title', 
               'address_street', 'address_city', 'address_state', 'address_postal_code', 'address_country',
               'created_at', 'updated_at', 'lead_source', 'status', 'tags', 'notes', 'notes_detail']
    row1 = ['cust1', 'John', 'Doe', 'john.doe@example.com', '555-1234', 'Acme Corp', 'Developer',
            '123 Main St', 'Anytown', 'CA', '90210', 'USA',
            datetime.now().isoformat(), datetime.now().isoformat(), 'Website', 'active', 'vip,developer', 'Initial contact', 'Met at conference']
    row2 = ['cust2', 'Jane', 'Smith', 'jane.smith@example.com', '555-5678', 'Beta Inc', 'Manager',
            '456 Oak Ave', 'Otherville', 'NY', '10001', 'USA',
            datetime(2023,1,15).isoformat(), datetime.now().isoformat(), 'Referral', 'lead', 'manager', 'Followed up', 'Interested']
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow(row1)
        writer.writerow(row2)
    return csv_path

# Model Tests
def test_customer_model():
    addr = Address(street="123 Test St", city="Testville", country="Testland")
    interaction = InteractionLog(channel="email", summary="Test email")
    cust = Customer(
        customer_id="test001",
        last_name="Testington",
        email="test@example.com",
        address=addr,
        interaction_history=[interaction]
    )
    assert cust.customer_id == "test001"
    assert cust.address.city == "Testville"
    assert cust.interaction_history[0].summary == "Test email"

# Importer Tests
def test_csv_crm_importer(dummy_csv_file):
    importer = CSVCRMImporter(file_path=str(dummy_csv_file))
    customers = importer.import_customers()
    assert len(customers) == 2
    assert customers[0].first_name == "John"
    assert customers[1].email == "jane.smith@example.com"

# Transformer Tests
def test_clean_customer_data(sample_customer_data_list):
    cleaned = clean_customer_data(sample_customer_data_list)
    assert len(cleaned) == 3
    assert cleaned[0].email == "john.doe@example.com" # Already lowercase
    # Add more specific assertions for cleaning if rules are complex

def test_enrich_customer_data(sample_customer_data_list):
    enriched = enrich_customer_data(sample_customer_data_list)
    assert len(enriched) == 3
    # Example: Check if VIP_CUSTOMER tag was added if not present
    assert "VIP_CUSTOMER" in enriched[2].tags

def test_convert_customers_to_dataframe(sample_customer_data_list):
    df = convert_customers_to_dataframe(sample_customer_data_list)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert 'email' in df.columns

# Reporting Tests
def test_generate_customer_segmentation_report(sample_customer_data_list):
    report = generate_customer_segmentation_report(sample_customer_data_list)
    assert 'customers_by_status' in report
    assert report['customers_by_status'].get('active') == 1
    assert report['customers_by_status'].get('lead') == 1
    assert report.get('vip_customer_count', 0) >= 1 # Based on sample_customer_data_list and enricher

def test_generate_lead_conversion_report(sample_customer_data_list):
    report = generate_lead_conversion_report(sample_customer_data_list)
    assert 'total_identified_leads' in report
    assert report['total_identified_leads'] == 1
    assert report['total_converted_customers'] == 1 # cust3 is active_customer
    assert report['lead_to_customer_conversion_rate'] == 100.0

# Visualization Tests
def test_plot_customer_distribution_by_status(sample_customer_data_list, tmp_path):
    output_dir = tmp_path / "crm_visuals"
    output_dir.mkdir()
    plot_path = plot_customer_distribution_by_status(sample_customer_data_list, output_dir=output_dir)
    assert plot_path is not None
    assert os.path.exists(plot_path)
    assert Path(plot_path).name == "customer_status_distribution.png"

def test_plot_customer_distribution_by_source(sample_customer_data_list, tmp_path):
    output_dir = tmp_path / "crm_visuals"
    output_dir.mkdir() # Ensure it's created if not by the previous test in parallel runs
    plot_path = plot_customer_distribution_by_source(sample_customer_data_list, output_dir=output_dir)
    assert plot_path is not None
    assert os.path.exists(plot_path)
    assert Path(plot_path).name == "customer_source_distribution.png"

# Test with empty data
def test_crm_reports_empty_data():
    empty_list = []
    seg_report = generate_customer_segmentation_report(empty_list)
    assert "No customer data" in seg_report.get("message", "")
    
    conv_report = generate_lead_conversion_report(empty_list)
    assert "No customer data" in conv_report.get("message", "")

def test_crm_visuals_empty_data(tmp_path):
    empty_list = []
    output_dir = tmp_path / "crm_visuals_empty"
    output_dir.mkdir()
    status_plot = plot_customer_distribution_by_status(empty_list, output_dir=output_dir)
    assert status_plot is None
    source_plot = plot_customer_distribution_by_source(empty_list, output_dir=output_dir)
    assert source_plot is None

# Test importer with non-existent file
def test_csv_crm_importer_file_not_found():
    importer = CSVCRMImporter(file_path="non_existent_file.csv")
    with pytest.raises(FileNotFoundError):
        importer.connect()
    # Further test: import_customers should also fail or handle this
    with pytest.raises(FileNotFoundError): # Assuming connect is called within import_customers
         importer.import_customers() 