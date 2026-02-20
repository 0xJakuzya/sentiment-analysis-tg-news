# sentiment analysis for telegram news

A project for sentiment analysis of news from Telegram channels using machine learning.

## Features

- Scraping messages from Telegram channels (Telethon)
- Text preprocessing (raw data cleaning, normalization, emoji/URL removal, etc.)
- Sentiment classification (positive / negative / neutral) using BERT-based models
- Storing raw and processed data in MongoDB and local JSON
- Docker support for easy deployment
- JSON configuration (channels, pipeline, preprocessing rules)

## Installation

```bash
git clone <repo>
cd Sentiment-Analysis-Telegram-news
pip install -r requirements.txt
```

## Setup

### 1. Environment variables (.env)

Create a `.env` file in the project root:

```env
# Telegram API (get credentials at my.telegram.org)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# Session
SESSION_NAME=session
SESSION_DIR=sessions

# MongoDB
MONGO_ADDRESS=mongodb://localhost:27017
MONGO_DATABASE_NAME=telegram_sentiment
MONGO_COLLECTION_NAME=messages
```

### 2. Configuration files (config/)

| File | Description |
|------|-------------|
| `channels.json` | Array of channel usernames, e.g. `["ruble30", "channel2"]` |
| `pipeline.json` | `messages_per_channel` — message limit per channel |
| `preprocessing.json` | Text cleaning rules (what to remove, skip, filter) |

## Running

**Start MongoDB before running:**

```bash
docker-compose up -d mongodb
```

### Locally

```bash
python main.py
```

On first run, enter your phone number and Telegram verification code for authorization.

### Docker Compose

```bash
docker-compose up --build
```

## Project structure

```
sentiment-analysis-telegram-news
├── config/
│   ├── channels.json      # Channels to scrape
│   ├── pipeline.json      # Pipeline limits and settings
│   └── preprocessing.json # Text preprocessing rules
├── src/
│   ├── pipeline.py        # Pipeline: scrape → clean → classify → save
│   ├── telegram_scraper.py # Scraping via Telethon
│   ├── preprocessing.py   # Text cleaning
│   ├── mongo.py           # MongoDB integration
│   ├── utils.py           # Config loading
│   ├── embedding.py       # (stub) Embeddings
│   └── classification.py # (stub) Sentiment classification
├── data/
│   ├── raw/               # Raw messages (JSON)
│   └── processed/         # Processed messages (JSON)
├── sessions/              # Telethon sessions (created automatically)
├── main.py                # Entry point
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```
