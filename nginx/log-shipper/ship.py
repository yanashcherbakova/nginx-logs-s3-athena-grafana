import os
import logging
import json
import gzip
import uuid
import datetime
import time

import boto3

LOG_PATH = os.getenv("LOG_PATH", "/var/log/nginx_files/access.jsonl")
STATE_PATH = os.getenv("STATE_PATH", "/var/log/nginx_files/.shipper_state.json")

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_PREFIX = os.getenv("S3_PREFIX")

MAX_BUFFER_BYTES = 5 * 1024 * 1024
READ_CHUNK_BYTES = 256 * 1024

upload_every_sec = 60
poll_every_sec = 2 

if not S3_BUCKET:
    raise SystemExit("S3_Bucket is required")

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
    
def save_offset(offset):
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"offset": offset}, f)
    os.replace(tmp, STATE_PATH)

def gzip_jsonl(lines):
    cleaned_lines = []

    for l in lines:
        if not l.strip():
            continue
        cleaned_l = l.rstrip(b"\n")
        cleaned_lines.append(cleaned_l)

    body = b"\n".join(cleaned_lines)
    body += b"\n"

    compressed_body = gzip.compress(body)
    return compressed_body


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)

def s3_key(now):
    return (
        f"{S3_PREFIX}/year={now:%Y}/month={now:%m}/day={now:%d}/hour={now:%H}/"
        f"access_{now:%Y%m%dT%H%M%SZ}_{uuid.uuid4().hex}.jsonl.gz"
    )

def main():
    s3 = build_s3()
    offset = load_offset()

    buf_lines = []
    buf_bytes = 0
    flush_started_at = time.time()

    logger.info("start with offset=%d", offset)
    logger.info("target s3 bucket=%s", S3_BUCKET)
    logger.info("upload_every=%ds poll_every=%ds max_buffer=%dB", upload_every_sec, poll_every_sec, MAX_BUFFER_BYTES)

    while True:
        try:
            size=os.path.getsize(LOG_PATH)
            if offset > size:
                logger.warning("log truncated or rotated: offset=%d size=%d", offset, size)
                offset = 0

            with open(LOG_PATH, "rb") as f:
                f.seek(offset)
                chunk = f.read(READ_CHUNK_BYTES)
                offset = f.tell()

            if chunk:
                lines = chunk.splitlines()
                buf_lines.extend(lines)
                buf_bytes += len(chunk)

        except FileNotFoundError:
            pass
        except Exception:
            logger.exception("tail error")

        time_due = (time.time() - flush_started_at) >= upload_every_sec
        size_due = buf_bytes >= MAX_BUFFER_BYTES

        if buf_lines and (time_due or size_due):
            key = s3_key(utcnow())
            try:
                body = gzip_jsonl(buf_lines)
                s3.put_object(Bucket=S3_BUCKET, Key= key, Body = body)
                save_offset(offset)

                logger.info("uploaded s3://%s/%s lines=%d bytes_gz=%d offset=%d",
                            S3_BUCKET, key, len(buf_lines), len(body), offset)
                
                buf_lines.clear()
                buf_bytes = 0
                flush_started_at = time.time()
                
            except Exception:
                logger.exception("upload error")

        time.sleep(poll_every_sec)

if __name__ == "__main__":
    main()