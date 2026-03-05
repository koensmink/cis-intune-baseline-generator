FROM python:3.11-slim@sha256:4057d02a202f69bfbfe10f65300519f612eb00fc595b8499f77d3cfe5b1b9fd4

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=60

RUN useradd --create-home --home-dir /home/appuser --shell /usr/sbin/nologin appuser

RUN python -m pip install --no-cache-dir --upgrade pip wheel setuptools

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY pyproject.toml .

ENV PYTHONPATH=/app/src

USER appuser

ENTRYPOINT ["python", "-m", "cis_pdf2csv"]
