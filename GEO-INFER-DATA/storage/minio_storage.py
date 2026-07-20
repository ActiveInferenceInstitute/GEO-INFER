"""
MinIO/S3 storage implementation for GEO-INFER-DATA.

This module provides comprehensive MinIO and S3-compatible storage
for geospatial data with automatic optimization and metadata management.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any


logger = logging.getLogger(__name__)


class MinIOStorage:
    """
    MinIO/S3-compatible object storage implementation.

    This class provides comprehensive MinIO and S3-compatible storage for
    geospatial data with support for large files, versioning, and lifecycle management.

    Args:
        config: MinIO/S3 configuration

    Examples:
        >>> storage = MinIOStorage({
        ...     'endpoint': 'localhost:9000',
        ...     'access_key': 'minioadmin',
        ...     'secret_key': 'minioadmin',
        ...     'bucket': 'geo-infer-data'
        ... })
        >>>
        >>> await storage.upload_file('local_data.geojson', 'processed/data.geojson')
        >>> files = await storage.list_files('processed/')
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.endpoint = config.get("endpoint")
        self.access_key = config.get("access_key")
        self.secret_key = config.get("secret_key")
        self.bucket = config.get("bucket")
        if not all((self.endpoint, self.access_key, self.secret_key, self.bucket)):
            raise ValueError(
                "MinIOStorage requires endpoint, access_key, secret_key, and bucket"
            )

        from minio import Minio

        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=bool(config.get("secure", False)),
        )

        logger.info(f"Initialized MinIOStorage for bucket: {self.bucket}")

    async def upload_file(self, local_path: str, remote_path: str) -> str:
        """
        Upload file to MinIO/S3.

        Args:
            local_path: Local file path
            remote_path: Remote object key

        Returns:
            Remote object key
        """
        local = Path(local_path)
        if not local.is_file():
            raise FileNotFoundError(local)
        await asyncio.to_thread(
            self.client.fput_object, self.bucket, remote_path, str(local)
        )
        logger.info(f"Uploaded {local_path} to {self.bucket}/{remote_path}")
        return remote_path

    async def download_file(self, remote_path: str, local_path: str) -> str:
        """
        Download file from MinIO/S3.

        Args:
            remote_path: Remote object key
            local_path: Local file path

        Returns:
            Local file path
        """
        destination = Path(local_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(
            self.client.fget_object, self.bucket, remote_path, str(destination)
        )
        logger.info(f"Downloaded {self.bucket}/{remote_path} to {local_path}")
        return local_path

    async def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in MinIO/S3 bucket.

        Args:
            prefix: Object key prefix

        Returns:
            List of object keys
        """
        objects = await asyncio.to_thread(
            lambda: list(
                self.client.list_objects(self.bucket, prefix=prefix, recursive=True)
            )
        )
        return [obj.object_name for obj in objects]

    async def delete_file(self, remote_path: str) -> bool:
        """
        Delete file from MinIO/S3.

        Args:
            remote_path: Remote object key

        Returns:
            True if deletion successful
        """
        await asyncio.to_thread(self.client.remove_object, self.bucket, remote_path)
        logger.info(f"Deleted {self.bucket}/{remote_path}")
        return True
