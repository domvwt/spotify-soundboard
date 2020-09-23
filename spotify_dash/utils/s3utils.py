import boto3
from botocore.exceptions import NoCredentialsError, DataNotFoundError, ClientError


class BucketObjectConn:
    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket_name, object_name):
        print(f"Connecting to S3 object: {bucket_name}/{object_name}...", end=" ")
        self.conn = boto3.client("s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        print("Complete.")
        self.bucket = bucket_name
        self.object = object_name

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
        return self.conn.head_object(Bucket=self.bucket, Key=self.object)["LastModified"]
