# Cascadia Framework Data Structure

## Overview

The Cascadia Agricultural Analysis Framework has been reorganized to provide a cleaner, more efficient data structure that separates module-specific data from run-specific outputs.

## New Data Organization

### Module-Specific Data (`module/data/`)

Each module now has its own data directory with standardized subdirectories:

```
module_name/
├── data/
│   ├── empirical/          # Real acquired data
│   ├── synthetic/          # Generated test data
│   ├── cache/             # H3-processed cached data
│   ├── processed/         # Final processed outputs
│   ├── raw/              # Unprocessed source data
│   └── metadata.json     # Module metadata and structure info
```

**Example:**
```
zoning/
├── data/
│   ├── empirical/
│   │   └── empirical_zoning_data.geojson
│   ├── synthetic/
│   │   └── synthetic_zoning_data.geojson
│   ├── cache/
│   │   └── zoning_h3_res8.json
│   ├── processed/
│   │   └── processed_zoning_data.geojson
│   ├── raw/
│   │   └── raw_zoning_data.geojson
│   └── metadata.json
```

### Run-Specific Outputs (`output/`)

The output directory now contains only run-specific summaries and reports:

```
output/
├── cascadia_analysis_report_YYYYMMDD_HHMMSS.md
├── cascadia_redevelopment_scores_YYYYMMDD_HHMMSS.json
├── cascadia_summary_YYYYMMDD_HHMMSS.json
├── cascadia_unified_data_YYYYMMDD_HHMMSS.geojson
├── cascadia_visualization_data.json
├── cascadia_summary_statistics.json
├── real_data/              # Real data acquisition outputs
├── visualizations/         # Interactive visualization files
└── cascadia_analysis.log   # Analysis log file
```

## Benefits of New Structure

### 1. **Cleaner Output Directory**
- Only run-specific summaries and reports
- No large data files cluttering the output
- Easy to identify recent runs and their results

### 2. **Module-Specific Data Organization**
- Each module manages its own data
- Clear separation between empirical, synthetic, and processed data
- Standardized structure across all modules
- Easy to locate and manage module-specific files

### 3. **Improved Caching**
- H3-processed data cached in module directories
- No need to re-process data if already available
- Clear distinction between raw and processed data

### 4. **Better Performance**
- Reduced output directory size
- Faster file operations
- Easier backup and version control

## Data Flow

### 1. **Data Acquisition**
```
Real Data Sources → module/data/empirical/
Synthetic Generation → module/data/synthetic/
Raw Downloads → module/data/raw/
```

### 2. **Data Processing**
```
Raw Data → H3 Processing → module/data/cache/
Processed Data → module/data/processed/
```

### 3. **Analysis Outputs**
```
Module Data → Fusion → output/ (run-specific files)
```

## Module Data Structure Details

### Empirical Data (`empirical/`)
- Real data acquired from external sources
- County/city websites, government APIs, etc.
- Validated and quality-checked data

### Synthetic Data (`synthetic/`)
- Generated test data for development and testing
- Used when real data is unavailable
- Clearly marked as synthetic for transparency

### Cache Data (`cache/`)
- H3-processed data for fast access
- Prevents re-processing of large datasets
- Module-specific H3 resolution files

### Processed Data (`processed/`)
- Final processed outputs ready for analysis
- Cleaned and standardized data formats
- Ready for fusion and analysis

### Raw Data (`raw/`)
- Unprocessed source data
- Original downloads and acquisitions
- Backup for reprocessing if needed

## Configuration

The data structure is configured in:
- `config/data_cleanup_config.json` - Data manager configuration
- `utils/data_cleanup.py` - Cleanup and reorganization utilities
- `utils/enhanced_data_manager.py` - Updated data manager with module-specific paths

## Maintenance

### Automatic Cleanup
- Old run files automatically cleaned (keeps 3 most recent)
- Module data organized automatically
- Standardized structure maintained

### Manual Cleanup
```bash
python3 cleanup_data.py
```

### Data Validation
- Each module has metadata.json with structure information
- Quality reports generated for data validation
- Clear logging of data sources and processing steps

## Migration Notes

### From Old Structure
- Module data moved from `output/data/` to `module/data/`
- H3 cache files moved to module-specific cache directories
- Empirical data moved to module-specific empirical directories
- Old run files cleaned up (kept 3 most recent)

### To New Structure
- All new data follows the standardized module structure
- Enhanced logging provides clear data source information
- Real data acquisition prioritized over synthetic data
- Interactive visualizations stored in `output/visualizations/`

## Best Practices

1. **Always check module data directories first** for existing data
2. **Use enhanced logging** to track data sources and quality
3. **Run cleanup script** periodically to maintain organization
4. **Keep run-specific outputs** in output directory only
5. **Use module-specific paths** for all data operations

## Future Enhancements

- Automated data quality monitoring
- Real-time data source validation
- Enhanced visualization capabilities
- Integration with external data APIs
- Advanced caching strategies
