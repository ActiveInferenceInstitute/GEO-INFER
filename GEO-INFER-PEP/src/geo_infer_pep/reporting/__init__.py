# Reporting functionalities for GEO-INFER-PEP

from .crm_reports import generate_customer_segmentation_report, generate_lead_conversion_report, get_quarterly_metrics as get_crm_quarterly_metrics
from .hr_reports import generate_headcount_report, generate_diversity_report, get_quarterly_metrics as get_hr_quarterly_metrics
from .talent_reports import generate_candidate_pipeline_report, calculate_time_to_hire, get_quarterly_metrics as get_talent_quarterly_metrics
from .generic_report_generator import create_quarterly_overview

__all__ = [
    # CRM Reports
    "generate_customer_segmentation_report",
    "generate_lead_conversion_report",
    "get_crm_quarterly_metrics",
    # HR Reports
    "generate_headcount_report",
    "generate_diversity_report",
    "get_hr_quarterly_metrics",
    # Talent Reports
    "generate_candidate_pipeline_report",
    "calculate_time_to_hire",
    "get_talent_quarterly_metrics",
    # Generic Reports
    "create_quarterly_overview"
] 