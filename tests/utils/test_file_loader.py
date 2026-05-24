import boto3
from moto import mock_aws as mock_s3

from app.utils.file_loader import FileLoader


class TestFileLoader:

    def test_open_local_file(self, tmp_path):
        # Arrange
        file_path = tmp_path / "sample.txt"
        file_path.write_text("hello world", encoding="utf-8")

        loader = FileLoader(app_env="local")

        # Act
        with loader.open_file(str(file_path), "r") as f:
            content = f.read()

        # Assert
        assert content == "hello world"

    @mock_s3
    def test_open_s3_file(self):
        # Arrange
        bucket = "company-api-bucket"
        key = "folder/sample.txt"
        content = "hello from s3"

        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=bucket)
        s3.put_object(Bucket=bucket, Key=key, Body=content.encode("utf-8"))

        loader = FileLoader(app_env="uat")
        s3_path = f"{key}"

        # Act
        with loader.open_file(s3_path, "r") as f:
            result = f.read()

        # Assert
        assert result == content

    @mock_s3
    def test_open_s3_binary(self):
        # Arrange
        bucket = "company-api-bucket"
        key = "folder/data.bin"
        data = b"\x00\x01\x02"

        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=bucket)
        s3.put_object(Bucket=bucket, Key=key, Body=data)

        loader = FileLoader(app_env="uat")
        s3_path = f"{key}"

        # Act
        with loader.open_file(s3_path, "rb") as f:
            result = f.read()

        # Assert
        assert result == data
