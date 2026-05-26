# app/utils/file_loader.py

from io import BytesIO, StringIO
from typing import TextIO

import boto3


class FileLoader:
    """
    Unified file loader for local and S3 paths.
    Returns a file-like object so existing code using `with open(...)` still works.
    """

    def __init__(self, app_env: str | None = None):
        from app.utils.env_vars import APP_ENV
        self.app_env = app_env if app_env else APP_ENV
        self.s3 = boto3.client("s3")

    def open_file(
            self,
            path: str,
            mode: str = "r",
            encoding: str = "utf-8",
            newline=None
    ) -> TextIO | StringIO | BytesIO:
        """
        Opens a file from local FS or S3.
        Returns a file-like object.
        """

        # --- S3 HANDLING ---
        if self.app_env not in ["local", "test"]:
            return self._open_s3(path, mode, encoding)

        # --- LOCAL FILE HANDLING ---
        if newline is not None:
            return open(path, mode, newline=newline, encoding=encoding)

        if "b" in mode:
            return open(path, mode)

        return open(path, mode, encoding=encoding)

    def _open_s3(self, path: str, mode: str, encoding: str):
        from app.utils.env_vars import S3_BUCKET
        bucket = S3_BUCKET

        # WRITE MODE
        if "w" in mode:
            return S3WriteBuffer(self.s3, bucket, path, encoding)

        # APPEND MODE
        if "a" in mode:
            try:
                obj = self.s3.get_object(Bucket=bucket, Key=path, mode="a+")
                existing = obj["Body"].read().decode(encoding)
            except self.s3.exceptions.NoSuchKey:
                existing = ""
            return S3WriteBuffer(self.s3, bucket, path, encoding, initial=existing)

        # READ MODE
        obj = self.s3.get_object(Bucket=bucket, Key=path)
        body = obj["Body"].read()

        if "b" in mode:
            return BytesIO(body)

        return StringIO(body.decode(encoding))


class S3WriteBuffer:
    def __init__(self, s3, bucket, key, encoding="utf-8", initial=""):
        from io import StringIO
        self.s3 = s3
        self.bucket = bucket
        self.key = key
        self.encoding = encoding
        self.buffer = StringIO(initial)

    def write(self, data):
        return self.buffer.write(data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.buffer.seek(0)
        self.s3.put_object(
            Bucket=self.bucket,
            Key=self.key,
            Body=self.buffer.getvalue().encode(self.encoding)
        )
        self.buffer.close()
