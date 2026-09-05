"""
Temporal Analytics Module for GEO-INFER-SPACE.

This module provides methods for analyzing temporal patterns, trends,
and time-series data associated with spatial cells. It is backend-agnostic
and operates on standard data structures.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

import numpy as np


class TemporalAnalyzer:
    """
    Analyzer for temporal patterns in spatial data.
    
    Provides methods for analyzing temporal patterns, trends,
    and time-series data.
    """
    
    def __init__(self) -> None:
        """Initialize the TemporalAnalyzer."""
        self.analysis_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def analyze_temporal_patterns(self, data: List[Dict[str, Any]], 
                                timestamp_column: str, 
                                value_column: str,
                                temporal_resolution: str = 'hour') -> Dict[str, Any]:
        """
        Analyze temporal patterns in data.
        
        Args:
            data: List of dictionaries containing data records
            timestamp_column: Key containing timestamps
            value_column: Key containing values to analyze
            temporal_resolution: Resolution ('hour', 'day', 'week', 'month')
            
        Returns:
            Dictionary containing temporal pattern analysis
        """
        if not data:
            return {'error': 'No data provided'}
        
        # Extract and parse temporal data
        temporal_data = []
        for record in data:
            if timestamp_column in record and value_column in record:
                ts_val = record[timestamp_column]
                val = record[value_column]
                
                if ts_val is not None and val is not None:
                    timestamp = self._parse_timestamp(ts_val)
                    if timestamp:
                        temporal_data.append({
                            'timestamp': timestamp,
                            'value': float(val),
                            'original_record': record
                        })
        
        if not temporal_data:
            return {'error': 'No valid temporal data found'}

        # Aggregate by temporal resolution
        aggregated_data = self._aggregate_by_temporal_resolution(temporal_data, temporal_resolution)
        
        # Analyze patterns
        patterns = self._analyze_patterns(aggregated_data, temporal_resolution)
        
        # Calculate statistics
        stats = self._calculate_temporal_stats(aggregated_data)
        
        return {
            'temporal_patterns': patterns,
            'aggregated_data': aggregated_data,
            'statistics': stats,
            'temporal_resolution': temporal_resolution,
            'data_points': len(temporal_data),
            'method': 'Temporal Pattern Analysis'
        }

    def _parse_timestamp(self, ts: Any) -> Optional[datetime]:
        """Parse timestamp from various formats."""
        if isinstance(ts, datetime):
            return ts
        
        timestamp_str = str(ts)
        try:
            # Try common formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d',
                '%m/%d/%Y %H:%M:%S'
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue
            
            # ISO format fallback
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.debug(f"Failed to parse timestamp '{timestamp_str}': {e}")
            return None

    def _aggregate_by_temporal_resolution(
        self, temporal_data: List[Dict], resolution: str
    ) -> Dict[int, Dict[str, float]]:
        """Aggregate data by temporal resolution."""
        aggregated: Dict[int, List[float]] = {}
        
        for item in temporal_data:
            ts = item['timestamp']
            val = item['value']
            
            if resolution == 'hour':
                key = ts.hour
            elif resolution == 'day':
                key = ts.weekday()
            elif resolution == 'week':
                key = ts.isocalendar()[1]
            elif resolution == 'month':
                key = ts.month
            else:
                key = ts.hour
            
            if key not in aggregated:
                aggregated[key] = []
            aggregated[key].append(val)
            
        # Calculate stats for each bucket
        result: Dict[int, Dict[str, float]] = {}
        for key, values in aggregated.items():
            stats = {
                'mean': float(np.mean(values)),
                'sum': float(np.sum(values)),
                'count': len(values),
                'std': float(np.std(values))
            }
            result[key] = stats
            
        return result

    def _analyze_patterns(self, aggregated_data: Dict, resolution: str) -> Dict[str, Any]:
        """Analyze temporal patterns in aggregated data."""
        if not aggregated_data:
            return {}
            
        # Find peak periods
        sorted_periods = sorted(aggregated_data.items(), 
                              key=lambda x: x[1]['mean'], reverse=True)
                              
        peak_periods = []
        for period, stats in sorted_periods[:5]:
            peak_periods.append({
                'period': period,
                'mean_value': stats['mean'],
                'count': stats['count']
            })
            
        return {
            'peak_periods': peak_periods,
            'total_periods': len(aggregated_data)
        }

    def _calculate_temporal_stats(self, aggregated_data: Dict) -> Dict[str, Any]:
        """Calculate overall statistics."""
        if not aggregated_data:
            return {}
            
        all_means = [d['mean'] for d in aggregated_data.values()]
        
        return {
            'overall_mean': float(np.mean(all_means)),
            'overall_std': float(np.std(all_means)),
            'min_mean': float(np.min(all_means)),
            'max_mean': float(np.max(all_means))
        }
