import os
import logging

import boto3

LOG_PATH = os.getenv("LOG_PATH", "/var/log/nginx/access.log")
STATE_PATH = os.getenv("STATE_PATH", "/var/log/nginx/.shipper_state.json")

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_PREFIX = os.getenv("S3_PREFIX")

MAX_BUFFER_BYTES = 5 * 1024 * 1024
READ_CHUNK_BYTES = 256 * 1024

logging.basicConfig(
    level="INFO", 
    format="%(asctime)sZ | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
    )
logger = logging.getLogger()

