#!/usr/bin/env python3
"""
H3 Indexing Operations Module

Provides H3 cell indexing operations using H3 v4.3.0.
Functions for cell conversion, string/int operations, and position indexing.

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


def cell_to_string(cell: Union[str, int]) -> str:
    """
    Convert H3 cell to string representation.
    
    Args:
        cell: H3 cell index (string or integer)
        
    Returns:
        H3 cell index as string
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> cell_to_string(0x89283082e73ffff)
        '89283082e73ffff'
    """
    if isinstance(cell, str):
        if not h3.is_valid_cell(cell):
            raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
        return cell
    elif isinstance(cell, int):
        return h3.int_to_cell(cell)
    else:
        raise ValueError("Cell must be string or integer")


def string_to_cell(cell: str) -> int:
    """
    Convert H3 cell string to integer representation.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        H3 cell index as integer
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> string_to_cell('89283082e73ffff')
        617283082e73ffff
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    return h3.cell_to_int(cell)


def int_to_cell(cell: int) -> str:
    """
    Convert H3 cell integer to string representation.
    
    Args:
        cell: H3 cell index as integer
        
    Returns:
        H3 cell index as string
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> int_to_cell(0x89283082e73ffff)
        '89283082e73ffff'
    """
    return h3.int_to_cell(cell)


def cell_to_int(cell: str) -> int:
    """
    Convert H3 cell string to integer representation.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        H3 cell index as integer
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> cell_to_int('89283082e73ffff')
        617283082e73ffff
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    return h3.cell_to_int(cell)


# Re-export core functions for convenience
# Removed to avoid circular import


# Export all functions
__all__ = [
    'cell_to_center_child',
    'cell_to_children',
    'cell_to_parent',
    'cell_to_string',
    'string_to_cell',
    'int_to_cell',
    'cell_to_int'
] 