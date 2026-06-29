from minio import Minio
from app.core.config import settings

class MinioService:
    def __init__(self):
        # Strip protocol prefix if present (e.g. 'http://' or 'https://')
        endpoint = settings.minio_endpoint.replace("http://", "").replace("https://", "")
        self.client = Minio(
            endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )

    def get_object_bytes(self, bucket_name: str, object_name: str) -> bytes:
        response = self.client.get_object(bucket_name, object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

minio_service = MinioService()