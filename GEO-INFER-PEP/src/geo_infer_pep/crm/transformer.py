"""CRM Data Transformers."""
from typing import List
import pandas as pd
from ..models.crm_models import Customer

def clean_customer_data(customers: List[Customer]) -> List[Customer]:
    """
    Performs basic cleaning operations on a list of Customer objects.
    - Standardizes phone numbers (example).
    - Normalizes email addresses to lowercase.
    - Fills missing essential fields with defaults if appropriate.
    """
    cleaned_customers = []
    for customer in customers:
        # Example: Normalize email to lowercase
        if customer.email:
            customer.email = customer.email.lower()

        # Example: Basic phone number standardization (very simplified)
        if customer.phone_number:
            customer.phone_number = "".join(filter(str.isdigit, customer.phone_number))
            if len(customer.phone_number) == 10 and not customer.phone_number.startswith('1'):
                 customer.phone_number = "1" + customer.phone_number # Add country code if US like
        
        # Add more cleaning rules here
        # e.g., capitalizing names, standardizing addresses, etc.

        cleaned_customers.append(customer)
    print(f"Performed cleaning on {len(cleaned_customers)} customer records.")
    return cleaned_customers

def enrich_customer_data(customers: List[Customer], external_data_sources: dict = None) -> List[Customer]:
    """
    Enriches customer data using internal logic or external data sources.
    - Example: Deriving a 'customer_segment' based on company size or industry (if available).
    - Example: Flagging VIP customers based on interaction history or tags.
    """
    enriched_customers = []
    for customer in customers:
        # Example: VIP flagging (simplified)
        if "vip" in customer.tags or "high-priority" in customer.tags:
            if "VIP_CUSTOMER" not in customer.tags:
                 customer.tags.append("VIP_CUSTOMER")
        
        # Example: Inferring segment (very basic)
        # if customer.company and "Enterprise" in customer.company:
        #    customer.segment = "Enterprise"
        # elif customer.company and ("SMB" in customer.company or "Startup" in customer.company):
        #    customer.segment = "SMB"

        # Add more enrichment rules here
        # e.g., using external APIs for company info, social media data, etc.
        enriched_customers.append(customer)
    print(f"Performed enrichment on {len(enriched_customers)} customer records.")
    return enriched_customers

def convert_customers_to_dataframe(customers: List[Customer]) -> pd.DataFrame:
    """
    Converts a list of Customer Pydantic models to a Pandas DataFrame
    for easier analysis and bulk operations.
    """
    if not customers:
        return pd.DataFrame()
    
    # model_dump() is used for Pydantic v2 models
    customer_dicts = [customer.model_dump() for customer in customers]
    df = pd.DataFrame(customer_dicts)
    
    # Potentially flatten nested structures like 'address' or 'interaction_history' if needed
    # For example, to flatten address:
    # if 'address' in df.columns:
    #     address_df = pd.json_normalize(df['address'])
    #     address_df = address_df.add_prefix('address.')
    #     df = pd.concat([df.drop(columns=['address']), address_df], axis=1)
        
    print(f"Converted {len(df)} customer records to DataFrame.")
    return df

# Example usage (conceptual)
# if __name__ == '__main__':
#     from .importer import CSVCRMImporter
#     # Assume dummy_crm_data.csv exists from importer.py example
#     importer = CSVCRMImporter(file_path='dummy_crm_data.csv')
#     raw_customers = importer.import_customers()
#     
#     cleaned = clean_customer_data(raw_customers)
#     enriched = enrich_customer_data(cleaned)
#     
#     customer_df = convert_customers_to_dataframe(enriched)
#     if not customer_df.empty:
#         print("\nCustomer DataFrame head:")
#         print(customer_df.head())
#         print("\nCustomer DataFrame info:")
#         customer_df.info() 