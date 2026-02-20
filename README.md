# sentiment analysis for telegram news

Sentiment analysis tool for Telegram news: scraping with Telethon, text preprocessing, ML classification (BERT), storage in MongoDB and JSON

## features

- scraping messages from Telegram channels (telethon)
- text preprocessing (raw data cleaning, normalization, emoji/URL removal, etc.)
- sentiment classification (positive / negative / neutral) using BERT-based models
- storing raw and processed data in MongoDB and local JSON
- docker support for easy deployment
- JSON configuration (channels, pipeline, preprocessing rules)

## installation

```bash
git clone <repo>
cd Sentiment-Analysis-Telegram-news
pip install -r requirements.txt
```

## setup

### 1. environment variables (.env)

create a `.env` file in the project root:

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

### 2. configuration files (config/)

| File | Description |
|------|-------------|
| `channels.json` | Array of channel usernames, e.g. `["ruble30", "channel2"]` |
| `pipeline.json` | `messages_per_channel` — message limit per channel |
| `preprocessing.json` | Text cleaning rules (what to remove, skip, filter) |

## running

**start MongoDB before running:**

```bash
docker-compose up -d mongodb
```

### locally

```bash
python main.py
```

on first run, enter your phone number and Telegram verification code for authorization.

### docker compose

```bash
docker-compose up --build
```

## project structure

```
sentiment-analysis-telegram-news
├── config/
│   ├── channels.json      # channels to scrape
│   ├── pipeline.json      # pipeline limits and settings
│   └── preprocessing.json # text preprocessing rules
├── src/
│   ├── pipeline.py        # pipeline: scrape → clean → classify → save
│   ├── telegram_scraper.py # scraping telethon
│   ├── preprocessing.py   # text cleaning
│   ├── mongo.py           # mongoDB integration
│   ├── utils.py           # config loading
│   ├── embedding.py       # (stub) embeddings
│   └── classification.py # (stub) sentiment classification
├── data/
│   ├── raw/               # raw data (JSON)
│   └── processed/         # processed data (JSON)
├── sessions/              # telethon sessions (created automatically)
├── main.py                # entry point
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```
