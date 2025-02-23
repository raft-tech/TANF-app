"""Custom logging handler that sends logs to an S3 bucket."""

import logging.handlers
import boto3
import logging
from botocore.exceptions import ClientError
from django.conf import settings

# SET TO GET THESE FROM ENV VARS IN SETTINGS
AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
AWS_REGION = settings.AWS_REGION
AWS_S3_BUCKET_NAME = settings.AWS_S3_BUCKET_NAME
AWS_S3_LOGS_PREFIX = settings.AWS_S3_LOGS_PREFIX

def change_log_filename(logger, new_filename):
    """Change the filename of the log file handler."""
    handlers = getattr(logger, 'handlers', [])
    for handler in handlers:
        if isinstance(handler, S3FileHandler):
            handler.close()
            handler.filename = new_filename
            handler.stream = open(new_filename, 'a')


class S3FileHandler(logging.FileHandler):
    """Custom logging handler that sends logs to an S3 bucket."""

    def __init__(self, filename, mode='a', encoding=None, delay=False, errors=None):
        self.filename = filename
        try:
            with open(filename, "x") as file: # noqa
                pass  # No content is written, so it's an empty file
            print("File created successfully.")
        except FileExistsError:
            print("File already exists.")
        super().__init__(
            filename, mode='a', encoding=None, delay=False, errors=None
        )
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )
        self.bucket_name = AWS_S3_BUCKET_NAME
        self.logs_prefix = AWS_S3_LOGS_PREFIX
        if not self.logs_prefix.endswith("/"):
            self.logs_prefix += "/"

    def doRollover(self):
        """Rollover happens before closing the file."""
        try:
            key = f"{AWS_S3_LOGS_PREFIX}/{self.filename}"
            self.s3_client.upload_file(
                Filename=self.filename,
                Bucket=AWS_S3_BUCKET_NAME,
                Key=key)
        except ClientError as e:
            print(f"Error sending log to S3: {e}")
        self.close()
