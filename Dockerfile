FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY pyproject.toml .

ENV PYTHONPATH=/app/src
ENTRYPOINT ["python", "-m", "cis_pdf2csv"]
