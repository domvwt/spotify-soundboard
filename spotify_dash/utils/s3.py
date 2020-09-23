import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError


class BucketObjectConn:
    def __init__(self, object_name):
        self.conn = boto3.client(
            "s3",
            aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
        )
        self.bucket = os.environ["S3_BUCKET_NAME"]
        self.object = object_name

    def exists(self):
        try:
            self.conn.head_object(Bucket=self.bucket, Key=self.object)
            return True
        except ClientError:
            print("S3 asset not found")
            return False

    def upload(self, file_path):
        print(f"Uploading {file_path.name} to S3://{self.bucket}/{self.object}...", end=" ")
        try:
            self.conn.upload_file(str(file_path), self.bucket, self.object)
            print("Complete.")
            return True
        except FileNotFoundError:
            print("Local file not found")
            return False
        except NoCredentialsError as e:
            print("AWS credentials error:", e)
            return False

    def download(self, destination_path):
        print(f"Downloading S3://{self.bucket}/{self.object} to {destination_path}...", end=" ")
        try:
            self.conn.download_file(self.bucket, self.object, destination_path)
            print("Complete.")
            return True
        except ClientError:
            print("S3 asset not found")
            return False
        except NoCredentialsError as e:
            print("AWS credentials error:", e)
            return False

    def last_update(self):
        try:
            return self.conn.head_object(Bucket=self.bucket, Key=self.object)["LastModified"]
        except ClientError:
            print("S3 asset not found")
            return False
