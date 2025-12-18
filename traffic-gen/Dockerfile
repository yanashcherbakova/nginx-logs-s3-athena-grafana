FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir requests
COPY gen.py /app/gen.py
CMD ["python", "/app/gen.py"]