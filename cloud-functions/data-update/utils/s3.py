import datetime as dt
import os
import pathlib

import boto3
from botocore.exceptions import NoCredentialsError, ClientError


class BucketObjectConn:
    def __init__(self, object_name):
        self.conn = boto3.client(
            "s3",
            aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )
        self.bucket_name = os.environ["S3_BUCKET_NAME"]
        self.object_name = object_name
        self.object = boto3.resource(
            "s3",
            aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        ).Object(self.bucket_name, self.object_name,)

    def exists(self):
        try:
            self.conn.head_object(Bucket=self.bucket_name, Key=self.object_name)
            return True
        except ClientError:
            print("S3 asset not found")
            return False

    def upload(self, file_path, last_data_date: dt.datetime = None):
        print(
            f"Uploading {file_path.name} to S3://{self.bucket_name}/{self.object_name}...",
            end=" ",
        )
        try:
            if last_data_date:
                date_str = last_data_date.strftime("%Y-%m-%d")
                extra_args = dict(Metadata={"last-data-date": date_str})
            else:
                extra_args = None
            self.conn.upload_file(
                str(file_path), self.bucket_name, self.object_name, extra_args
            )
            print("Complete.")
            return True
        except FileNotFoundError:
            print("Local file not found")
            return False
        except NoCredentialsError as e:
            print("AWS credentials error:", e)
            return False

    def download(self, destination_path: pathlib.Path):
        print(
            f"Downloading S3://{self.bucket_name}/{self.object_name} to {destination_path}...",
            end=" ",
        )
        try:
            destination_path.parent.absolute().mkdir(parents=True, exist_ok=True)
            self.conn.download_file(
                self.bucket_name, self.object_name, str(destination_path)
            )
            print("Complete.")
            return True
        except ClientError:
            print("S3 asset not found")
            return False
        except NoCredentialsError as e:
            print("AWS credentials error:", e)
            return False

    def last_data_date(self):
        date = self.object.metadata.get("last-data-date", None)
        return dt.datetime.strptime(date, "%Y-%m-%d").date()
