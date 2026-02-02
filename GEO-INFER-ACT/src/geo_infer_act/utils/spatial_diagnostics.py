#!/usr/bin/env python
"""
Spatial Diagnostics Utilities for GEO-INFER-ACT.

This module provides specialized diagnostic and analysis tools for spatial
active inference, including spatial coherence metrics, autocorrelation,
and free energy landscape analysis.

Features:
- H3 neighbor coherence metrics
- Spatial autocorrelation (Moran's I approximation)
- Free energy landscape analysis
- Structured JSON/CSV export
"""

import numpy as np
import logging
import json
import csv
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class SpatialDiagnostics:
    """
    Comprehensive spatial diagnostics for active inference agents.
    
    Provides metrics for analyzing spatial belief coherence,
    information flow, and agent performance in H3 grids.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize spatial diagnostics.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir) if output_dir else Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_history: List[Dict] = []
        self.analysis_cache: Dict[str, Any] = {}
    
    def compute_spatial_coherence(
        self,
        beliefs: np.ndarray,
        neighbor_matrix: np.ndarray
    ) -> Dict[str, float]:
        """
        Compute spatial coherence metrics.
        
        Measures how consistent beliefs are across neighboring cells.
        
        Args:
            beliefs: Array of shape (n_cells, state_dim)
            neighbor_matrix: Binary adjacency matrix (n_cells, n_cells)
            
        Returns:
            Dict with coherence metrics
        """
        n_cells = beliefs.shape[0]
        
        if neighbor_matrix.shape != (n_cells, n_cells):
            return {'error': 'dimension_mismatch'}
        
        # Local coherence: similarity to immediate neighbors
        local_coherences = []
        for i in range(n_cells):
            neighbors = np.where(neighbor_matrix[i] > 0)[0]
            if len(neighbors) > 0:
                neighbor_beliefs = beliefs[neighbors]
                mean_neighbor = np.mean(neighbor_beliefs, axis=0)
                coherence = 1 - np.mean(np.abs(beliefs[i] - mean_neighbor))
                local_coherences.append(coherence)
        
        # Global coherence: overall belief similarity
        belief_variance = np.var(beliefs)
        global_coherence = 1.0 / (1.0 + belief_variance)
        
        return {
            'local_mean': float(np.mean(local_coherences)) if local_coherences else 0.0,
            'local_std': float(np.std(local_coherences)) if local_coherences else 0.0,
            'local_min': float(np.min(local_coherences)) if local_coherences else 0.0,
            'local_max': float(np.max(local_coherences)) if local_coherences else 0.0,
            'global': float(global_coherence),
            'n_cells': n_cells
        }
    
    def compute_morans_i(
        self,
        values: np.ndarray,
        weights: np.ndarray
    ) -> Dict[str, float]:
        """
        Compute Moran's I spatial autocorrelation.
        
        Moran's I measures spatial autocorrelation - how similar
        nearby observations are to each other.
        
        Args:
            values: Array of values per cell (n_cells,)
            weights: Spatial weights matrix (n_cells, n_cells)
            
        Returns:
            Dict with Moran's I and related metrics
        """
        n = len(values)
        values = np.asarray(values).flatten()
        
        if n < 2:
            return {'morans_i': 0.0, 'interpretation': 'insufficient_data'}
        
        # Mean and deviation
        mean_val = np.mean(values)
        y = values - mean_val
        
        # Sum of weights
        W = np.sum(weights)
        if W == 0:
            return {'morans_i': 0.0, 'interpretation': 'no_neighbors'}
        
        # Numerator: spatial covariance
        numerator = np.sum(weights * np.outer(y, y))
        
        # Denominator: total variance
        denominator = np.sum(y ** 2)
        
        if denominator == 0:
            return {'morans_i': 0.0, 'interpretation': 'zero_variance'}
        
        # Moran's I
        I = (n / W) * (numerator / denominator)
        
        # Interpretation
        if I > 0.3:
            interpretation = 'positive_clustering'
        elif I < -0.3:
            interpretation = 'negative_dispersion'
        else:
            interpretation = 'random'
        
        return {
            'morans_i': float(I),
            'interpretation': interpretation,
            'n_cells': n,
            'mean_value': float(mean_val)
        }
    
    def analyze_free_energy_landscape(
        self,
        free_energy_history: List[float],
        belief_history: List[np.ndarray]
    ) -> Dict[str, Any]:
        """
        Analyze the free energy landscape over time.
        
        Args:
            free_energy_history: List of free energy values
            belief_history: List of belief arrays over time
            
        Returns:
            Dict with landscape analysis
        """
        if len(free_energy_history) < 3:
            return {'status': 'insufficient_data'}
        
        fe = np.array(free_energy_history)
        
        # Trend analysis
        x = np.arange(len(fe))
        slope, intercept = np.polyfit(x, fe, 1)
        
        # Volatility
        volatility = np.std(np.diff(fe))
        
        # Convergence detection
        recent = fe[-min(10, len(fe)):]
        is_converged = np.std(recent) < 0.01 * np.mean(np.abs(recent) + 1e-8)
        
        # Find minima
        local_minima = []
        for i in range(1, len(fe) - 1):
            if fe[i] < fe[i-1] and fe[i] < fe[i+1]:
                local_minima.append({'step': i, 'value': float(fe[i])})
        
        # Belief entropy evolution
        entropy_history = []
        for beliefs in belief_history:
            entropy = -np.sum(beliefs * np.log(beliefs + 1e-8), axis=-1)
            entropy_history.append(float(np.mean(entropy)))
        
        return {
            'trend': {
                'slope': float(slope),
                'direction': 'decreasing' if slope < -0.001 else ('increasing' if slope > 0.001 else 'stable')
            },
            'volatility': float(volatility),
            'is_converged': is_converged,
            'final_value': float(fe[-1]),
            'min_value': float(np.min(fe)),
            'max_value': float(np.max(fe)),
            'local_minima': local_minima[:5],  # Top 5
            'entropy_trend': {
                'initial': entropy_history[0] if entropy_history else None,
                'final': entropy_history[-1] if entropy_history else None
            }
        }
    
    def compute_belief_dynamics(
        self,
        belief_history: List[np.ndarray]
    ) -> Dict[str, Any]:
        """
        Analyze belief dynamics over time.
        
        Args:
            belief_history: List of belief arrays over time
            
        Returns:
            Dict with dynamics analysis
        """
        if len(belief_history) < 2:
            return {'status': 'insufficient_data'}
        
        # Belief changes between steps
        changes = []
        for i in range(1, len(belief_history)):
            diff = np.abs(belief_history[i] - belief_history[i-1])
            changes.append(float(np.mean(diff)))
        
        # Belief concentration (how peaked are beliefs)
        concentrations = []
        for beliefs in belief_history:
            max_prob = np.max(beliefs, axis=-1)
            concentrations.append(float(np.mean(max_prob)))
        
        return {
            'mean_change': float(np.mean(changes)),
            'change_trend': 'stabilizing' if changes[-1] < changes[0] else 'volatile',
            'final_concentration': concentrations[-1],
            'concentration_trend': concentrations[-5:] if len(concentrations) >= 5 else concentrations
        }
    
    def record_step(
        self,
        step: int,
        beliefs: np.ndarray,
        free_energy: float,
        action: Optional[Dict] = None,
        spatial_metrics: Optional[Dict] = None
    ) -> None:
        """Record a single step for analysis."""
        entry = {
            'step': step,
            'timestamp': datetime.now().isoformat(),
            'free_energy': float(free_energy),
            'belief_entropy': float(-np.sum(beliefs * np.log(beliefs + 1e-8))),
            'belief_max': float(np.max(beliefs)),
            'action': action,
            'spatial_metrics': spatial_metrics
        }
        self.metrics_history.append(entry)
    
    def export_to_json(self, filename: str = 'spatial_diagnostics.json') -> str:
        """Export diagnostics to JSON."""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump({
                'metrics_history': self.metrics_history,
                'analysis_cache': self.analysis_cache,
                'export_time': datetime.now().isoformat()
            }, f, indent=2, default=str)
        
        logger.info(f"Exported diagnostics to {filepath}")
        return str(filepath)
    
    def export_to_csv(self, filename: str = 'spatial_diagnostics.csv') -> str:
        """Export step-by-step metrics to CSV."""
        filepath = self.output_dir / filename
        
        if not self.metrics_history:
            logger.warning("No metrics to export")
            return str(filepath)
        
        # Flatten metrics for CSV
        fieldnames = ['step', 'timestamp', 'free_energy', 'belief_entropy', 'belief_max']
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for entry in self.metrics_history:
                writer.writerow(entry)
        
        logger.info(f"Exported CSV to {filepath}")
        return str(filepath)


def compute_spatial_kl_divergence(
    beliefs_a: np.ndarray,
    beliefs_b: np.ndarray
) -> float:
    """
    Compute KL divergence between two spatial belief distributions.
    
    Args:
        beliefs_a: First belief array (n_cells, state_dim)
        beliefs_b: Second belief array (n_cells, state_dim)
        
    Returns:
        Average KL divergence across cells
    """
    kl_values = []
    for a, b in zip(beliefs_a, beliefs_b):
        a = np.asarray(a) + 1e-8
        b = np.asarray(b) + 1e-8
        a = a / a.sum()
        b = b / b.sum()
        kl = np.sum(a * np.log(a / b))
        kl_values.append(kl)
    return float(np.mean(kl_values))


def compute_information_flow(
    belief_history: List[np.ndarray],
    neighbor_matrix: np.ndarray
) -> Dict[str, float]:
    """
    Compute information flow between neighboring cells.
    
    Args:
        belief_history: List of beliefs over time
        neighbor_matrix: Adjacency matrix
        
    Returns:
        Dict with information flow metrics
    """
    if len(belief_history) < 2:
        return {'flow': 0.0}
    
    n_cells = belief_history[0].shape[0]
    flow_values = []
    
    for t in range(1, len(belief_history)):
        prev_beliefs = belief_history[t-1]
        curr_beliefs = belief_history[t]
        
        for i in range(n_cells):
            neighbors = np.where(neighbor_matrix[i] > 0)[0]
            if len(neighbors) > 0:
                # Change at this cell
                cell_change = np.sum(np.abs(curr_beliefs[i] - prev_beliefs[i]))
                # Neighbor influence
                neighbor_prev = np.mean(prev_beliefs[neighbors], axis=0)
                influence = np.sum(curr_beliefs[i] * np.log((curr_beliefs[i] + 1e-8) / (neighbor_prev + 1e-8)))
                flow_values.append(influence)
    
    return {
        'mean_flow': float(np.mean(flow_values)) if flow_values else 0.0,
        'max_flow': float(np.max(flow_values)) if flow_values else 0.0
    }
