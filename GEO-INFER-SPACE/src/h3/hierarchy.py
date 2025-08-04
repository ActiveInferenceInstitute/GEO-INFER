#!/usr/bin/env python3
"""
H3 Hierarchy Module

Provides H3 hierarchical operations using H3 v4.3.0.
Functions for parent-child relationships and hierarchical navigation.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import h3
import numpy as np
from typing import Union, List, Tuple, Optional, Dict, Any
from constants import (
    MAX_H3_RES, MIN_H3_RES, ERROR_MESSAGES
)


def cell_to_children(cell: str, resolution: int) -> List[str]:
    """
    Get all children of an H3 cell at a given resolution.
    
    Args:
        cell: H3 cell index as string
        resolution: Target resolution (must be > cell resolution)
        
    Returns:
        List of child cell indices
        
    Raises:
        ValueError: If cell is invalid or resolution is not greater than cell resolution
        
    Example:
        >>> cell_to_children('89283082e73ffff', 10)
        ['8a283082e73ffff', '8a283082e77ffff', ...]
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    cell_res = h3.get_resolution(cell)
    if resolution <= cell_res:
        raise ValueError(f"Target resolution must be greater than cell resolution ({cell_res})")
    
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    return list(h3.cell_to_children(cell, resolution))


def cell_to_parent(cell: str, resolution: int) -> str:
    """
    Get the parent of an H3 cell at a given resolution.
    
    Args:
        cell: H3 cell index as string
        resolution: Target resolution (must be < cell resolution)
        
    Returns:
        Parent cell index
        
    Raises:
        ValueError: If cell is invalid or resolution is not less than cell resolution
        
    Example:
        >>> cell_to_parent('89283082e73ffff', 8)
        '88283082e73ffff'
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    cell_res = h3.get_resolution(cell)
    if resolution >= cell_res:
        raise ValueError(f"Target resolution must be less than cell resolution ({cell_res})")
    
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    return h3.cell_to_parent(cell, resolution)


def cell_to_center_child(cell: str, resolution: int) -> str:
    """
    Get the center child of an H3 cell at a given resolution.
    
    Args:
        cell: H3 cell index as string
        resolution: Target resolution (must be > cell resolution)
        
    Returns:
        Center child cell index
        
    Raises:
        ValueError: If cell is invalid or resolution is not greater than cell resolution
        
    Example:
        >>> cell_to_center_child('89283082e73ffff', 10)
        '8a283082e73ffff'
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    cell_res = h3.get_resolution(cell)
    if resolution <= cell_res:
        raise ValueError(f"Target resolution must be greater than cell resolution ({cell_res})")
    
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    return h3.cell_to_center_child(cell, resolution)


def get_hierarchy_path(cell: str, target_resolution: int) -> List[str]:
    """
    Get the hierarchical path from a cell to a target resolution.
    
    Args:
        cell: H3 cell index as string
        target_resolution: Target resolution for the path
        
    Returns:
        List of cells forming the hierarchical path
        
    Raises:
        ValueError: If cell is invalid or target resolution is invalid
        
    Example:
        >>> get_hierarchy_path('89283082e73ffff', 6)
        ['86283082e73ffff', '87283082e73ffff', '88283082e73ffff', '89283082e73ffff']
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    if not MIN_H3_RES <= target_resolution <= MAX_H3_RES:
        raise ValueError(f"Target resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    cell_res = h3.get_resolution(cell)
    path = [cell]
    
    if target_resolution < cell_res:
        # Go up the hierarchy
        current_cell = cell
        for res in range(cell_res - 1, target_resolution - 1, -1):
            current_cell = h3.cell_to_parent(current_cell, res)
            path.insert(0, current_cell)
    elif target_resolution > cell_res:
        # Go down the hierarchy
        current_cell = cell
        for res in range(cell_res + 1, target_resolution + 1):
            current_cell = h3.cell_to_center_child(current_cell, res)
            path.append(current_cell)
    
    return path


def get_ancestors(cell: str, max_ancestors: int = None) -> List[str]:
    """
    Get all ancestors of an H3 cell up to a maximum number or resolution 0.
    
    Args:
        cell: H3 cell index as string
        max_ancestors: Maximum number of ancestors to return (None for all)
        
    Returns:
        List of ancestor cell indices (from closest to farthest)
        
    Raises:
        ValueError: If cell is invalid
        
    Example:
        >>> get_ancestors('89283082e73ffff', 3)
        ['88283082e73ffff', '87283082e73ffff', '86283082e73ffff']
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    cell_res = h3.get_resolution(cell)
    ancestors = []
    current_cell = cell
    
    for res in range(cell_res - 1, -1, -1):
        if max_ancestors is not None and len(ancestors) >= max_ancestors:
            break
        
        current_cell = h3.cell_to_parent(current_cell, res)
        ancestors.append(current_cell)
    
    return ancestors


def get_descendants(cell: str, max_descendants: int = None) -> List[str]:
    """
    Get all descendants of an H3 cell up to a maximum number or resolution 15.
    
    Args:
        cell: H3 cell index as string
        max_descendants: Maximum number of descendants to return (None for all)
        
    Returns:
        List of descendant cell indices (from closest to farthest)
        
    Raises:
        ValueError: If cell is invalid
        
    Example:
        >>> get_descendants('88283082e73ffff', 10)
        ['89283082e73ffff', '8a283082e73ffff', ...]
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    cell_res = h3.get_resolution(cell)
    descendants = []
    current_cells = [cell]
    
    for res in range(cell_res + 1, MAX_H3_RES + 1):
        if max_descendants is not None and len(descendants) >= max_descendants:
            break
        
        new_cells = []
        for current_cell in current_cells:
            children = h3.cell_to_children(current_cell, res)
            new_cells.extend(children)
            descendants.extend(children)
        
        current_cells = new_cells
    
    return descendants[:max_descendants] if max_descendants else descendants


# Export all functions
__all__ = [
    'cell_to_children',
    'cell_to_parent',
    'cell_to_center_child',
    'get_hierarchy_path',
    'get_ancestors',
    'get_descendants'
] 