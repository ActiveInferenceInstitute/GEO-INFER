"""
File system storage implementation for GEO-INFER-DATA.

This module provides local file system storage for development,
testing, and small-scale geospatial data management.
"""

import json
import logging
from typing import Dict, List, Any
from pathlib import Path


logger = logging.getLogger(__name__)


class FileSystemStorage:
    """
    Local file system storage implementation.

    This class provides local file system storage for development,
    testing, and small-scale geospatial data management.

    Args:
        config: File system configuration

    Examples:
        >>> storage = FileSystemStorage({
        ...     'base_path': '/data/geo_infer',
        ...     'create_dirs': True
        ... })
        >>>
        >>> await storage.store_file(data, 'datasets/sensors.geojson')
        >>> files = await storage.list_files('datasets/')
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_path = Path(config.get("base_path", "/tmp/geo_infer_data"))
        self.create_dirs = config.get("create_dirs", True)

        # Create base directory if needed
        if self.create_dirs:
            self.base_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized FileSystemStorage for {self.base_path}")

    async def store_file(self, data: Any, file_path: str) -> str:
        """
        Store data to file system.

        Args:
            data: Data to store
            file_path: Relative file path

        Returns:
            Absolute file path
        """
        full_path = self._resolve_path(file_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Storing data to {full_path}")
        if isinstance(data, (bytes, bytearray, memoryview)):
            full_path.write_bytes(bytes(data))
        elif isinstance(data, str):
            full_path.write_text(data, encoding="utf-8")
        else:
            full_path.write_text(
                json.dumps(data, indent=2, default=str), encoding="utf-8"
            )
        return str(full_path)

    async def retrieve_file(self, file_path: str) -> Any:
        """
        Retrieve data from file system.

        Args:
            file_path: Relative file path

        Returns:
            Retrieved data
        """
        full_path = self._resolve_path(file_path)
        if not full_path.is_file():
            raise FileNotFoundError(full_path)

        logger.info(f"Retrieving data from {full_path}")
        if full_path.suffix.lower() in {".json", ".geojson"}:
            return json.loads(full_path.read_text(encoding="utf-8"))
        return full_path.read_bytes()

    async def list_files(self, pattern: str = "*") -> List[str]:
        """
        List files in storage.

        Args:
            pattern: File pattern

        Returns:
            List of file paths
        """
        logger.info(f"Listing files with pattern: {pattern}")
        return [
            str(path.relative_to(self.base_path))
            for path in self.base_path.glob(pattern)
            if path.is_file()
        ]

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage.

        Args:
            file_path: Relative file path

        Returns:
            True if successful
        """
        full_path = self._resolve_path(file_path)
        logger.info(f"Deleting file: {full_path}")
        if not full_path.is_file():
            return False
        full_path.unlink()
        return True

    def _resolve_path(self, file_path: str) -> Path:
        """Resolve a storage-relative path without allowing path traversal."""
        candidate = (self.base_path / file_path).resolve()
        base = self.base_path.resolve()
        if candidate != base and base not in candidate.parents:
            raise ValueError(f"file_path escapes storage base path: {file_path}")
        return candidate
