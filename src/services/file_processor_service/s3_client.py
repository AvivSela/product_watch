"""
Simple S3 Client Utility for Local Development

This module provides a basic S3-compatible client that works with local MinIO instance.

For local development, start MinIO using:
docker run -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"
"""

# Standard library imports
import logging
from io import BytesIO
from os import getenv
from typing import Optional, Union
from urllib.parse import urlparse

# Third-party imports
from minio import Minio

logger = logging.getLogger(__name__)


class S3ClientError(Exception):
    """Custom exception for S3 client errors."""

    pass


class S3Client:
    """
    Simple S3-compatible client for local MinIO development.

    Supports local MinIO instance for development and testing.
    """

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        default_bucket_name: str = "default",
        auto_create_bucket: bool = True,
    ):
        """
        Initialize S3 client.

        Args:
            endpoint_url: MinIO endpoint URL (default: "http://localhost:9000")
            access_key: Access key for authentication (default: "minioadmin")
            secret_key: Secret key for authentication (default: "minioadmin")
            bucket_name: Default bucket to use
            auto_create_bucket: Whether to create bucket if it doesn't exist
        """
        # Use environment variables if not provided
        self.endpoint_url = endpoint_url or getenv(
            "MINIO_ENDPOINT", "http://localhost:9000"
        )
        self.access_key = access_key or getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = secret_key or getenv("MINIO_SECRET_KEY", "minioadmin")
        self.default_bucket_name = default_bucket_name
        self.auto_create_bucket = auto_create_bucket

        # Initialize MinIO client
        self._minio_client = None
        self._initialize_client()

        # Create bucket if needed
        if self.auto_create_bucket:
            self._ensure_bucket_exists()

    def _initialize_client(self):
        """Initialize MinIO client."""

        try:
            # Determine if connection should be secure
            secure = getenv("MINIO_SECURE", "false").lower() == "true"

            self._minio_client = Minio(
                endpoint=self.endpoint_url.replace("http://", "").replace(
                    "https://", ""
                ),
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=secure,
            )
            logger.info(f"Initialized MinIO client for {self.endpoint_url}")
        except Exception as e:
            raise S3ClientError(f"Failed to initialize MinIO client: {e}")

    def _ensure_bucket_exists(self):
        """Ensure the default bucket exists."""
        try:
            if not self._minio_client.bucket_exists(self.default_bucket_name):
                self._minio_client.make_bucket(self.default_bucket_name)
                logger.info(f"Created MinIO bucket: {self.default_bucket_name}")
        except Exception as e:
            logger.warning(f"Failed to ensure bucket exists: {e}")

    def upload_data(
        self,
        data: Union[str, bytes],
        object_key: str,
        bucket_name: Optional[str] = None,
    ) -> str:
        """
        Upload data (string or bytes) to S3.

        Args:
            data: Data to upload
            object_key: S3 object key
            bucket_name: Bucket name (if None, uses default)

        Returns:
            S3 object key of uploaded data
        """
        bucket_name = bucket_name or self.default_bucket_name

        try:
            if isinstance(data, str):
                data = data.encode("utf-8")

            # Wrap bytes data in BytesIO to make it file-like
            data_stream = BytesIO(data)

            self._minio_client.put_object(
                bucket_name, object_key, data_stream, length=len(data)
            )

            logger.info(
                f"Successfully uploaded data to s3://{bucket_name}/{object_key}"
            )
            return urlparse(f"s3://{bucket_name}/{object_key}").geturl()

        except Exception as e:
            raise S3ClientError(f"Failed to upload data: {e}")

    def get_object(self, url: str) -> bytes:
        """
        Get object data from S3.

        Args:
            object_key: S3 object key
            bucket_name: Bucket name (if None, uses default)

        Returns:
            Object data as bytes
        """
        # If it's a full URL, parse it
        if url.startswith(("http://", "https://", "s3://")):
            bucket_name, object_key = self.__url_into_bucket_and_object_key(url)
        else:
            # If it's just a path, use the default bucket
            bucket_name = self.default_bucket_name
            object_key = url

        try:
            response = self._minio_client.get_object(bucket_name, object_key)
            data = response.read()
            response.close()
            response.release_conn()

            logger.info(f"Successfully retrieved s3://{bucket_name}/{object_key}")
            return data

        except Exception as e:
            raise S3ClientError(f"Failed to get object: {e}")

    def url_exists(self, url: str) -> bool:
        """
        Check if a file exists in S3.

        Args:
            url: Either a full S3 URL or just the object key/path

        Returns:
            True if the file exists
        """
        # If it's a full URL, parse it
        if url.startswith(("http://", "https://", "s3://")):
            bucket_name, object_key = self.__url_into_bucket_and_object_key(url)
        else:
            # If it's just a path, use the default bucket
            bucket_name = self.default_bucket_name
            object_key = url

        return self.object_exists(bucket_name, object_key)

    def object_exists(self, bucket_name, object_key) -> bool:
        """
        Check if an object exists in S3.

        Args:
            object_key: S3 object key
            bucket_name: Bucket name (if None, uses default)

        Returns:
            True if object exists
        """

        try:
            self._minio_client.stat_object(bucket_name, object_key)
            return True
        except Exception:
            return False

    def __url_into_bucket_and_object_key(self, url: str) -> tuple[str, str]:
        """
        Convert a URL into a bucket name and object key.
        """
        parsed = urlparse(url)
        bucket_name = parsed.netloc
        object_key = parsed.path.lstrip("/")
        return bucket_name, object_key


# Convenience function for local development
def create_local_s3_client(
    default_bucket_name: str = "default", port: int = 9000
) -> S3Client:
    """
    Create an S3 client for local MinIO development.

    Args:
        default_bucket_name: Default bucket name
        port: MinIO port

    Returns:
        Configured S3Client instance
    """
    endpoint_url = f"http://localhost:{port}"

    return S3Client(endpoint_url=endpoint_url, default_bucket_name=default_bucket_name)


# Example usage and testing
if __name__ == "__main__":
    client = create_local_s3_client()
    print(client.get_object("s3://default/test/file.txt"))
    print(client.object_exists("s3://default/test/file.txt"))
    print(client.upload_data("Hello, S3!", "test/file.txt"))
    print(client.get_object("s3://default/test/file.txt"))
    print(client.object_exists("s3://default/test/file.txt"))
    print(client.upload_data("Hello, S3!", "test/file.txt"))
    print(client.get_object("s3://default/test/file.txt"))
    print(client.object_exists("s3://default/test/file.txt"))
