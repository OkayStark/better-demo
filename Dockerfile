# Use slim Python base
FROM python:3.12-slim-bookworm

WORKDIR /app

# install runtime deps and clean up build tools after use
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y build-essential \
    && apt-get autoremove -y

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PORT=5000
EXPOSE 5000

# Use Gunicorn for a production-like process
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers", "2"]
