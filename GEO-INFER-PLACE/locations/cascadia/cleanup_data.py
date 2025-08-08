#!/usr/bin/env python3
"""
Data Cleanup Script for Cascadia Framework

This script reorganizes the data structure to:
- Move module-specific data to appropriate module directories
- Clean up old run data from output directory
- Maintain run-specific summaries in output directory
- Create standardized data structure for each module
"""

import logging
import sys
from pathlib import Path

# Add the utils directory to the path
sys.path.append(str(Path(__file__).parent / "utils"))

from data_cleanup import create_data_cleanup_manager

def setup_logging():
    """Set up logging for the cleanup script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('data_cleanup.log')
        ]
    )

def main():
    """Main cleanup function."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting Cascadia data cleanup and reorganization...")
    
    # Get the base directory (current directory)
    base_dir = Path(__file__).parent
    
    # Create cleanup manager
    cleanup_manager = create_data_cleanup_manager(base_dir)
    
    try:
        # Run full cleanup and reorganization
        cleanup_manager.run_full_cleanup(keep_recent_runs=3)
        
        logger.info("✅ Data cleanup and reorganization completed successfully!")
        logger.info("📁 New data structure:")
        logger.info("   - Module data moved to module/data/ directories")
        logger.info("   - Old run files cleaned up (kept 3 most recent)")
        logger.info("   - Run-specific summaries remain in output/")
        logger.info("   - Standardized data structure created for each module")
        
    except Exception as e:
        logger.error(f"❌ Data cleanup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
