FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data/raw data/processed data/labeled sessions && \
    chmod 700 sessions && \
    chown -R root:root sessions
ENV MONGODB_URI=mongodb://mongodb:27017
ENV MONGODB_DB=telegram_sentiment
ENV MONGODB_COLLECTION=messages
ENV SESSION_DIR=/app/sessions
CMD ["python", "telegram_scraper.py"]

