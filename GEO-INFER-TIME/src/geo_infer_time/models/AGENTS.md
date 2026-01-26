

# Agent
: models 

## Scope
 This directory contains models components for the module. It provides 1 classes and 0 functions. 

## Classes
 and Functions 

### TimeSerie
s
 TimeSeries data model for temporal geospatial data. **Methods**: - `timestamps() -> pd.DatetimeIndex`: Get timestamps. - `start_time() -> datetime`: Get start time. - `end_time() -> datetime`: Get end time. - `duration() -> timedelta`: Get time series duration. - `frequency() -> Optional[str]`: Get inferred frequency. - `resample(frequency: str, method: str) -> 'TimeSeries'`: Resample the time series to a different frequency. - `interpolate(method: str) -> 'TimeSeries'`: Interpolate missing values. - `get_statistics() -> Dict[str, Any]`: Get statistical summary of the time series. - `to_dataframe() -> pd.DataFrame`: Convert to pandas DataFrame. - `slice(start: datetime, end: datetime) -> 'TimeSeries'`: Slice the time series to a time range. 

## Capabilities
 
- **1 classes** for core functionality 

## Integration
 
- **Location**: `GEO-INFER-TIME/src/geo_infer_time/models` 
- **Type**: Directory Node 