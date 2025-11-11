import os
import boto3
from django.conf import settings

def generate_presigned_url(file_key):
    """
    Return a presigned URL to access a file.
    """
    s3_client = get_s3_client()

    return s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": file_key,
            "ResponseContentDisposition": f'inline; filename="{os.path.basename(file_key)}"',
        },
        ExpiresIn=settings.PRESIGNED_URL_EXPIRES_IN,
    )


def generate_presigned_upload_url(file_field_name, content_type="application/octet-stream"):
    """
    Return a presigned URL to upload a file.
    """
    s3_client = get_s3_client()

    return s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": file_field_name,
            "ContentType": content_type,
        },
        ExpiresIn=settings.PRESIGNED_URL_EXPIRES_IN,
    )


def get_s3_client():
    """
    Return an S3 client to interact with the S3 backend.
    """
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
