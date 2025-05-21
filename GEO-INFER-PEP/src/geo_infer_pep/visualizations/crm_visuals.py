"""CRM Data Visualization functions."""
from typing import List, Dict, Any, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from ..models.crm_models import Customer
from ..crm.transformer import convert_customers_to_dataframe
from ..reporting.crm_reports import generate_customer_segmentation_report # For data

# Ensure output directory exists
DEFAULT_OUTPUT_DIR = Path("visualizations_output")
DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def plot_customer_distribution_by_status(customers: List[Customer], output_dir: Path = DEFAULT_OUTPUT_DIR) -> Optional[str]:
    """
    Generates a bar chart of customer distribution by status.
    Saves the plot to a file and returns the file path.
    """
    if not customers:
        print("No customer data to plot distribution by status.")
        return None

    df = convert_customers_to_dataframe(customers)
    if df.empty or 'status' not in df.columns:
        print("Customer data is empty or 'status' column missing for plotting.")
        return None

    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='status', order=df['status'].value_counts().index)
    plt.title('Customer Distribution by Status')
    plt.xlabel('Status')
    plt.ylabel('Number of Customers')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    file_path = output_dir / "customer_status_distribution.png"
    try:
        plt.savefig(file_path)
        print(f"Saved customer status distribution plot to: {file_path}")
        plt.close() # Close the plot to free memory
        return str(file_path)
    except Exception as e:
        print(f"Error saving plot: {e}")
        plt.close()
        return None

def plot_customer_distribution_by_source(customers: List[Customer], output_dir: Path = DEFAULT_OUTPUT_DIR) -> Optional[str]:
    """
    Generates a bar chart of customer distribution by source.
    Saves the plot to a file and returns the file path.
    """
    if not customers:
        print("No customer data to plot distribution by source.")
        return None
    
    df = convert_customers_to_dataframe(customers)
    if df.empty or 'source' not in df.columns:
        print("Customer data is empty or 'source' column missing for plotting.")
        return None

    plt.figure(figsize=(12, 7))
    sns.countplot(data=df, y='source', order=df['source'].value_counts().index, palette="viridis")
    plt.title('Customer Distribution by Source')
    plt.xlabel('Number of Customers')
    plt.ylabel('Source')
    plt.tight_layout()

    file_path = output_dir / "customer_source_distribution.png"
    try:
        plt.savefig(file_path)
        print(f"Saved customer source distribution plot to: {file_path}")
        plt.close()
        return str(file_path)
    except Exception as e:
        print(f"Error saving plot: {e}")
        plt.close()
        return None

# Add more CRM visualization functions here, e.g.:
# - Sales pipeline funnel chart
# - Customer acquisition cost over time
# - Lead conversion rates by channel (pie chart or bar chart)

# Example conceptual usage
# if __name__ == '__main__':
#     from ..crm.importer import CSVCRMImporter
#     from ..crm.transformer import clean_customer_data, enrich_customer_data

#     # Assume dummy_crm_data.csv exists
#     importer = CSVCRMImporter(file_path='dummy_crm_data.csv')
#     raw_customers = importer.import_customers()
#     cleaned = clean_customer_data(raw_customers)
#     enriched = enrich_customer_data(cleaned)

#     if enriched:
#         status_plot_path = plot_customer_distribution_by_status(enriched)
#         if status_plot_path:
#             print(f"Status plot created at: {status_plot_path}")
        
#         source_plot_path = plot_customer_distribution_by_source(enriched)
#         if source_plot_path:
#             print(f"Source plot created at: {source_plot_path}")
#     else:
#         print("No data to generate visualizations.") 