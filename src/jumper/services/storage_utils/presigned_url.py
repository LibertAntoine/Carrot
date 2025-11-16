import os
from django.core import signing
from django.conf import settings
from django.utils import timezone
from django.core.files.storage import default_storage
from jumper.services.utils import get_full_domain_from_request
from datetime import timedelta
from urllib.parse import urlencode

LOCAL_TOKEN_EXPIRATION = 3600  # 1 hour


def generate_presigned_url(file_key, request):
    """
    Return a presigned URL to access a file.
    """
    if settings.STORAGE_BACKEND == "local":
        base_url = get_full_domain_from_request(request)
        url = default_storage.url(file_key)

        expires_at = (
            timezone.now() + timedelta(seconds=LOCAL_TOKEN_EXPIRATION)
        ).timestamp()
        token_data = {"file": file_key, "exp": expires_at, "user": request.user.id}
        token = signing.dumps(token_data, salt="local-file-token")
        url = f"{base_url}{url}?{urlencode({'token': token})}"
        return url
    if settings.STORAGE_BACKEND == "s3":
        return get_s3_client().generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": file_key,
                "ResponseContentDisposition": f'inline; filename="{os.path.basename(file_key)}"',
            },
            ExpiresIn=getattr(settings, "PRESIGNED_MINIO_URL_EXPIRES_IN", 7200),
        )
    elif settings.STORAGE_BACKEND == "swift":
        return default_storage.url(file_key)
    else:
        raise ValueError(f"Unknown storage backend: {settings.STORAGE_BACKEND}")


def generate_presigned_upload_url(
    key: str, content_type: str = "application/octet-stream"
):
    """
    Return a presigned URL to upload a file.
    """
    if settings.STORAGE_BACKEND == "s3":
        return get_s3_client().generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=getattr(settings, "PRESIGNED_MINIO_URL_EXPIRES_IN", 7200),
        )

    elif settings.STORAGE_BACKEND == "swift":
        import time
        import hashlib
        import hmac

        # Swift presigned PUT URL
        expires = int(time.time()) + getattr(settings, "SWIFT_TEMP_URL_DURATION", 3600)
        base_path = f"/v1/AUTH_{settings.SWIFT_TENANT_NAME}/{settings.SWIFT_CONTAINER_NAME}/{key}"
        key = settings.SWIFT_TEMP_URL_KEY.encode("utf-8")

        # Create the HMAC signature
        hmac_body = f"PUT\n{expires}\n{base_path}".encode("utf-8")
        sig = hmac.new(key, hmac_body, digestmod=hashlib.sha1).hexdigest()

        # Construct the full URL
        swift_base_url = settings.SWIFT_AUTH_URL.replace(
            "/identity/v3", "/v1/AUTH_" + settings.SWIFT_TENANT_NAME
        )
        upload_url = f"{swift_base_url}/{settings.SWIFT_CONTAINER_NAME}/{key}?temp_url_sig={sig}&temp_url_expires={expires}"
        return upload_url

    else:
        raise ValueError(f"Unknown storage backend: {settings.STORAGE_BACKEND}")


def get_s3_client():
    """
    Return an S3 client to interact with the S3 backend.
    """
    import boto3

    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_CUSTOM_DOMAIN,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
