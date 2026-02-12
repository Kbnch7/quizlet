from datetime import timedelta
from urllib.parse import urlparse

from minio import Minio
from minio.commonconfig import CopySource
from minio.error import S3Error


class MinioClient:
    def __init__(self, endpoint, access_key, secret_key, secure=False):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def presigned_put_url(
        self, bucket_name: str, object_name: str, expires: int = 3600
    ) -> str:
        """
        Генерирует presigned URL для загрузки файла (HTTP PUT)
        :param bucket_name: имя бакета
        :param object_name: ключ объекта
        :param expires: время жизни ссылки в секундах (по умолчанию 1 час)
        :return: presigned URL строка
        """
        try:
            url = self.client.presigned_put_object(
                bucket_name, object_name, expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            raise RuntimeError(f"Error generating presigned PUT URL: {e}")

    def presigned_get_url(
        self, bucket_name: str, object_name: str, expires: int = 3600
    ) -> str:
        """
        Генерирует presigned URL для скачивания файла (HTTP GET)
        :param bucket_name: имя бакета
        :param object_name: ключ объекта
        :param expires: время жизни ссылки в секундах (по умолчанию 1 час)
        :return: presigned URL строка
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name, object_name, expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            raise RuntimeError(f"Error generating presigned GET URL: {e}")

    def ensure_bucket(self, bucket_name: str) -> None:
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
        except S3Error as e:
            raise RuntimeError(f"Error ensuring bucket: {e}")

    def copy_object(self, bucket_name: str, src_object: str, dst_object: str) -> None:
        try:
            self.client.copy_object(
                bucket_name, dst_object, CopySource(bucket_name, src_object)
            )
        except S3Error as e:
            raise RuntimeError(f"Error copying object: {e}")

    def remove_object(self, bucket_name: str, object_name: str) -> None:
        try:
            self.client.remove_object(bucket_name, object_name)
        except S3Error as e:
            raise RuntimeError(f"Error removing object: {e}")


def extract_object_key_from_url(url: str, bucket_name: str) -> str:
    """Extract object key from full presigned or static URL; if already a key, return as-is."""
    if not url:
        return url
    if "://" not in url:
        return url
    parsed = urlparse(url)
    # Common patterns: /bucket/key or just /key depending on gateway
    path = parsed.path.lstrip("/")
    if path.startswith(bucket_name + "/"):
        return path[len(bucket_name) + 1:]
    return path
