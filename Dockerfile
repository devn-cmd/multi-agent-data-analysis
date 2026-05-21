FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for headless browsers on Linux
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Force Playwright to download its headless chromium driver inside the container
RUN python -m playwright install --with-deps chromium || true

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]