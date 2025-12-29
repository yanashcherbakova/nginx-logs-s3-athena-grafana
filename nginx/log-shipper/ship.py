import os
import logging
import json

import boto3

LOG_PATH = os.getenv("LOG_PATH", "/var/log/nginx/access.log")
STATE_PATH = os.getenv("STATE_PATH", "/var/log/nginx/.shipper_state.json")

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_PREFIX = os.getenv("S3_PREFIX")

MAX_BUFFER_BYTES = 5 * 1024 * 1024
READ_CHUNK_BYTES = 256 * 1024

upload_every_sec = 60
poll_every_sec = 2 

logging.basicConfig(
    level="INFO", 
    format="%(asctime)sZ | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
    )
logger = logging.getLogger()

def build_s3():
    session = boto3.Session(region_name=AWS_REGION)
    return session.client("s3")

def load_offset():
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return int(json.load(f).get("offset", 0))
    except Exception:
        return 0

def main():
    s3 = build_s3()
    offset = load_offset()

    buf_lines = []
    buf_bytes = 0

    logger.info("start with offset=%d", offset)
    logger.info("target s3 bucket=%s", S3_BUCKET)
    logger.info("upload_every=%ds poll_every=%ds max_buffer=%dB", upload_every_sec, poll_every_sec, MAX_BUFFER_BYTES)

    while True:
        try:
            with open(LOG_PATH, "rb") as f:
                f.seek(offset)
                chunk = f.read()
                offset = f.tell()

            if chunk:
                lines = chunk.splitlines()
                buf_lines.extend(lines)
                buf_bytes += len(chunk)

        except FileNotFoundError:
            pass
        except Exception:
            logger.exception("tail error")
