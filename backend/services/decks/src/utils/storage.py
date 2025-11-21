import os
from functools import lru_cache

from src.utils.minio import MinioClient

MINIO_ENDPOINT = os.getenv("MINIO_HOST", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "miniouser")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "miniopassword")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

BUCKET_CARDS = os.getenv("MINIO_BUCKET_CARDS", "cards")


@lru_cache(maxsize=1)
def get_storage_client() -> MinioClient:
    return MinioClient(
        MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, secure=MINIO_SECURE
    )
