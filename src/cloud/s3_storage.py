import os
from pathlib import Path

import boto3


BUCKET_NAME = os.getenv(
    "S3_BUCKET_NAME",
    "moksha19034-cloud-data-engineering-pipeline-20260818",
)

AWS_REGION = os.getenv(
    "AWS_REGION",
    "eu-north-1",
)


def get_s3_client():
    """Create an S3 client using the AWS CLI/session credentials."""
    return boto3.client(
        "s3",
        region_name=AWS_REGION,
    )


def upload_file(
    local_path,
    s3_key,
):
    """
    Upload a local file to the configured S3 bucket.

    Args:
        local_path: Local file path.
        s3_key: Destination object key in S3.

    Returns:
        S3 object URI.
    """

    path = Path(local_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    client = get_s3_client()

    client.upload_file(
        str(path),
        BUCKET_NAME,
        s3_key,
    )

    return (
        f"s3://{BUCKET_NAME}/{s3_key}"
    )


def upload_directory(
    directory,
    prefix,
):
    """
    Upload all files from a local directory
    to an S3 prefix.

    Returns:
        List of uploaded S3 object URIs.
    """

    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(
            f"Directory not found: {directory}"
        )

    uploaded = []

    for file_path in directory.rglob("*"):

        if not file_path.is_file():
            continue

        relative_path = (
            file_path.relative_to(directory)
        )

        s3_key = (
            f"{prefix.rstrip('/')}/"
            f"{relative_path}"
        )

        uploaded.append(
            upload_file(
                file_path,
                s3_key,
            )
        )

    return uploaded
