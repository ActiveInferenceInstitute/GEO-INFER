"""
Base model class for agricultural analysis and prediction.
"""

from typing import Dict, List, Optional, Union, Any
import abc


class AgricultureModel(abc.ABC):
    """
    Abstract base class for agricultural models.
    
    This class defines the interface for all agricultural models in the GEO-INFER-AG
    module. Subclasses should implement the core predictive functionality.
    
    Attributes:
        name: Name of the model
        version: Version string
        metadata: Dictionary of model metadata
        required_inputs: List of required input data sources
    """
    
    def __init__(
        self, 
        name: str,
        version: str = "0.1.0",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the agricultural model.
        
        Args:
            name: Unique name for the model
            version: Version string 
            config: Optional configuration parameters
        """
        self.name = name
        self.version = version
        self.config = config or {}
        self.metadata = {
            "name": name,
            "version": version,
            "type": self.__class__.__name__
        }
        self.required_inputs = []
        
    @abc.abstractmethod
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate predictions using the model.
        
        Args:
            data: Dictionary of input data
            
        Returns:
            Dictionary containing prediction results
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement predict()")
    
    def validate_inputs(self, data: Dict[str, Any]) -> bool:
        """
        Validate that all required inputs are present.
        
        Args:
            data: Dictionary of input data
            
        Returns:
            True if all required inputs are present
            
        Raises:
            ValueError: If required inputs are missing
        """
        for input_name in self.required_inputs:
            if input_name not in data:
                raise ValueError(f"Required input '{input_name}' is missing")
        return True
    
    @property
    def info(self) -> Dict[str, Any]:
        """
        Get information about the model.
        
        Returns:
            Dictionary of model information
        """
        return {
            "name": self.name,
            "version": self.version,
            "type": self.__class__.__name__,
            "required_inputs": self.required_inputs,
            "config": self.config
        }
    
    def save(self, path: str) -> None:
        """
        Save the model to disk.
        
        Args:
            path: Path to save the model
            
        Raises:
            NotImplementedError: Default implementation
        """
        raise NotImplementedError("Model saving not implemented")
    
    @classmethod
    def load(cls, path: str) -> "AgricultureModel":
        """
        Load a model from disk.
        
        Args:
            path: Path to load the model from
            
        Returns:
            Loaded model instance
            
        Raises:
            NotImplementedError: Default implementation
        """
        raise NotImplementedError("Model loading not implemented") 