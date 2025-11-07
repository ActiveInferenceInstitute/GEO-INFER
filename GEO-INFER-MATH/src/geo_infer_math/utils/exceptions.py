"""
Custom Exceptions for GEO-INFER-MATH

This module provides custom exception classes for better error handling.
"""


class MathError(Exception):
    """Base exception for mathematical operations."""
    pass


class NumericalError(MathError):
    """Exception for numerical computation errors."""
    pass


class ConvergenceError(NumericalError):
    """Exception for convergence failures in iterative methods."""
    pass


class SingularMatrixError(NumericalError):
    """Exception for singular matrix operations."""
    pass


class TheoremProvingError(MathError):
    """Exception for theorem proving errors."""
    pass


class ProofVerificationError(TheoremProvingError):
    """Exception for proof verification errors."""
    pass


class InformationTheoryError(MathError):
    """Exception for information theory errors."""
    pass


class InvalidDistributionError(InformationTheoryError):
    """Exception for invalid probability distributions."""
    pass


class SpatialError(MathError):
    """Exception for spatial operation errors."""
    pass


class CoordinateError(SpatialError):
    """Exception for coordinate transformation errors."""
    pass


class GeometryError(SpatialError):
    """Exception for geometric operation errors."""
    pass


