CREATE DATABASE IF NOT EXISTS nginx_logs;

CREATE EXTERNAL TABLE IF NOT EXISTS nginx_logs.access_logs (
  ts string,
  remote_addr string,
  method string,
  path string,
  request_uri string,
  status int,
  referer string,
  request_id string,
  bytes_sent bigint,
  user_id string,
  request_time double,
  user_agent string,
  session_id string
)
PARTITIONED BY (
  year string,
  month string,
  day string,
  hour string
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES (
  'ignore.malformed.json' = 'true'
)
LOCATION 's3://nginx-logs-grafana11/nginx_access_logs/'
TBLPROPERTIES ('has_encrypted_data'='false');

MSCK REPAIR TABLE nginx_logs.access_logs;