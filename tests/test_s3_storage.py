from pathlib import Path

import pytest

from src.cloud import s3_storage


def test_upload_file_success(monkeypatch, tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("sample data")

    uploads = []

    class FakeS3Client:
        def upload_file(self, filename, bucket, key):
            uploads.append(
                (filename, bucket, key)
            )

    monkeypatch.setattr(
        s3_storage,
        "get_s3_client",
        lambda: FakeS3Client(),
    )

    result = s3_storage.upload_file(
        file_path,
        "test/sample.txt",
    )

    assert result == (
        f"s3://{s3_storage.BUCKET_NAME}"
        "/test/sample.txt"
    )

    assert uploads == [
        (
            str(file_path),
            s3_storage.BUCKET_NAME,
            "test/sample.txt",
        )
    ]


def test_upload_file_missing_file(tmp_path):
    missing_file = (
        tmp_path / "missing.txt"
    )

    with pytest.raises(
        FileNotFoundError,
        match="File not found",
    ):
        s3_storage.upload_file(
            missing_file,
            "test/missing.txt",
        )


def test_upload_directory_success(
    monkeypatch,
    tmp_path,
):
    directory = tmp_path / "data"
    directory.mkdir()

    file_one = directory / "one.txt"
    file_two = directory / "nested" / "two.txt"

    file_two.parent.mkdir()

    file_one.write_text("one")
    file_two.write_text("two")

    uploads = []

    def fake_upload_file(
        local_path,
        s3_key,
    ):
        uploads.append(
            (
                Path(local_path),
                s3_key,
            )
        )

        return (
            f"s3://{s3_storage.BUCKET_NAME}"
            f"/{s3_key}"
        )

    monkeypatch.setattr(
        s3_storage,
        "upload_file",
        fake_upload_file,
    )

    result = s3_storage.upload_directory(
        directory,
        "raw",
    )

    assert len(result) == 2

    assert (
        directory / "one.txt",
        "raw/one.txt",
    ) in uploads

    assert (
        directory / "nested/two.txt",
        "raw/nested/two.txt",
    ) in uploads


def test_upload_directory_missing_directory(
    tmp_path,
):
    missing_directory = (
        tmp_path / "missing"
    )

    with pytest.raises(
        FileNotFoundError,
        match="Directory not found",
    ):
        s3_storage.upload_directory(
            missing_directory,
            "raw",
        )
