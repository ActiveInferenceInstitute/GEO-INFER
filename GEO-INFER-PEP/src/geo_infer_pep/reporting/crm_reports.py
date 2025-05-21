"""CRM Reporting functions."""
from typing import List, Dict, Any
import pandas as pd
from ..models.crm_models import Customer
from ..crm.transformer import convert_customers_to_dataframe # Assuming this function exists

def generate_customer_segmentation_report(customers: List[Customer]) -> Dict[str, Any]:
    """
    Generates a report on customer segmentation.
    Example: Counts customers by status, source, or custom tags.
    """
    if not customers:
        return {"message": "No customer data to report."}

    df = convert_customers_to_dataframe(customers)
    if df.empty:
        return {"message": "Customer data is empty after conversion to DataFrame."}

    report = {}

    if 'status' in df.columns:
        report['customers_by_status'] = df['status'].value_counts().to_dict()
    
    if 'source' in df.columns:
        report['customers_by_source'] = df['source'].value_counts().to_dict()
    
    # Example: Segmentation by a common tag like 'VIP_CUSTOMER' (created during enrichment)
    if 'tags' in df.columns:
        # Explode tags if they are lists, then count
        # This assumes 'tags' column contains lists of strings
        try:
            all_tags = df['tags'].explode()
            report['customers_by_tag'] = all_tags.value_counts().to_dict()
            if 'VIP_CUSTOMER' in all_tags.values:
                report['vip_customer_count'] = int(all_tags[all_tags == 'VIP_CUSTOMER'].count())
            else:
                report['vip_customer_count'] = 0
        except Exception as e:
            print(f"Could not process tags for reporting: {e}")
            report['tags_processing_error'] = str(e)

    report['total_customers'] = len(df)
    print("Generated customer segmentation report.")
    return report

def generate_lead_conversion_report(customers: List[Customer]) -> Dict[str, Any]:
    """
    Generates a report on lead conversion rates.
    Requires 'status' and potentially 'created_at' or 'updated_at' fields.
    (This is a simplified example)
    """
    if not customers:
        return {"message": "No customer data for lead conversion report."}

    df = convert_customers_to_dataframe(customers)
    if df.empty:
        return {"message": "Customer data is empty after conversion to DataFrame."}

    report = {}
    if 'status' not in df.columns:
        return {"message": "'status' column missing, cannot generate lead conversion report."}

    total_leads = df[df['status'] == 'lead'].shape[0]
    converted_customers = df[df['status'] == 'active_customer'].shape[0] # Simplified definition of "converted"
    
    report['total_identified_leads'] = total_leads
    report['total_converted_customers'] = converted_customers
    
    if total_leads > 0:
        report['lead_to_customer_conversion_rate'] = (converted_customers / total_leads) * 100
    else:
        report['lead_to_customer_conversion_rate'] = 0.0
        
    print("Generated lead conversion report.")
    return report

def get_quarterly_metrics(quarter: str, year: int) -> Dict[str, Any]:
    """Simulates fetching CRM quarterly metrics."""
    print(f"Fetching CRM quarterly metrics for Q{quarter} {year} (simulated).")
    return {
        "quarter": quarter,
        "year": year,
        "new_leads_acquired": 150, # Simulated
        "customers_converted": 30, # Simulated
        "avg_customer_satisfaction_score": 4.2, # Simulated
        "churn_rate_percent": 1.5 # Simulated
    }

# Add more CRM-specific reporting functions here, e.g.:
# - Sales pipeline analysis
# - Customer activity summary
# - Churn rate analysis

# Example conceptual usage
# if __name__ == '__main__':
#     from ..crm.importer import CSVCRMImporter
#     from ..crm.transformer import clean_customer_data, enrich_customer_data

#     # Assume dummy_crm_data.csv exists
#     importer = CSVCRMImporter(file_path='dummy_crm_data.csv')
#     raw_customers = importer.import_customers()
#     cleaned = clean_customer_data(raw_customers)
#     enriched = enrich_customer_data(cleaned)

#     segment_report = generate_customer_segmentation_report(enriched)
#     print("\nSegmentation Report:")
#     import json
#     print(json.dumps(segment_report, indent=2))

#     conversion_report = generate_lead_conversion_report(enriched)
#     print("\nConversion Report:")
#     print(json.dumps(conversion_report, indent=2)) 