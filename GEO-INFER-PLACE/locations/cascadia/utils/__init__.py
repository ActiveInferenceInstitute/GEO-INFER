# This file makes the utils directory a Python package

from .setup_manager import (
    setup_logging,
    check_dependencies,
    setup_spatial_processor,
    setup_data_integrator,
    load_analysis_config,
    setup_visualization_engine,
)

from .analysis_engine import (
    perform_enhanced_spatial_analysis,
    run_comprehensive_analysis,
)

from .reporting_engine import (
    generate_spatial_analysis_report,
    generate_enhanced_dashboard,
    generate_analysis_report,
    export_data_provenance,
)

from .data_processor import (
    initialize_modules,
    create_shared_backend,
    export_results,
    validate_data_acquisition,
)

__all__ = [
    # Setup functions
    "setup_logging",
    "check_dependencies",
    "setup_spatial_processor",
    "setup_data_integrator",
    "load_analysis_config",
    "setup_visualization_engine",
    # Analysis functions
    "perform_enhanced_spatial_analysis",
    "run_comprehensive_analysis",
    # Reporting functions
    "generate_spatial_analysis_report",
    "generate_enhanced_dashboard",
    "generate_analysis_report",
    "export_data_provenance",
    # Data processing functions
    "initialize_modules",
    "create_shared_backend",
    "export_results",
    "validate_data_acquisition",
] 