# app/utils/file_loader.py

import os
from io import BytesIO, StringIO
from typing import TextIO
from urllib.parse import urlparse

import boto3


class FileLoader:
    """
    Unified file loader for local and S3 paths.
    Returns a file-like object so existing code using `with open(...)` still works.
    """

    def __init__(self, app_env: str | None = None):
        self.app_env = app_env or os.getenv("APP_ENV", "local")
        self.s3 = boto3.client("s3")

    def open_file(self, path: str, mode: str = "r", encoding: str = "utf-8",
                  newline=None) -> TextIO | StringIO | BytesIO:
        """
        Opens a file from local FS or S3.
        Returns a file-like object.
        """
        if path.startswith("s3://"):
            return self._open_s3(path, mode, encoding)
        if newline is not None:
            return open(path, mode, newline=newline, encoding=encoding)
        if "b" in mode:
            return open(path, mode)
        return open(path, mode, encoding=encoding)

    def _open_s3(self, path: str, mode: str, encoding: str):
        parsed = urlparse(path)
        bucket = parsed.netloc
        key = parsed.path.lstrip("/")

        obj = self.s3.get_object(Bucket=bucket, Key=key)
        body = obj["Body"].read()

        # Binary mode
        if "b" in mode:
            return BytesIO(body)

        # Text mode
        return StringIO(body.decode(encoding))
