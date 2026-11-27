# Telegram channels aggregator

Collection and semantic search for Telegram channels. The pipeline saves posts in MongoDB and local JSON files and indexes cleaned text in Qdrant.

## features

- telegram channel scraping with Telethon
- text cleaning and normalization
- batch embedding with Sentence Transformers and similarity search in Qdrant
- raw and processed data in MongoDB and local json
- docker Compose support
- json configuration (channels, pipeline, preprocessing rules)

## installation

```bash
git clone https://github.com/0xJakuzya/sentiment-analysis-tg-news.git
cd sentiment-analysis-tg-news
python -m pip install -r requirements.txt
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

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=news_messages
```

## running

### locally

```bash
docker compose up -d mongodb qdrant
python main.py
```

## project structure

```
sentiment-analysis-tg-news
├── config/
│   ├── channels.json      # channels to scrape
│   ├── pipeline.json      # message limit
│   └── preprocessing.json # text preprocessing rules
├── src/
│   ├── inference.py       # scrape, clean, and save
│   ├── telegram_scraper.py # Telegram client
│   ├── preprocessing.py   # text cleaning
│   ├── mongodb.py         # MongoDB and JSON storage
│   ├── embedder.py        # batch embedding and indexing
│   ├── qdrantdb.py        # vector collection and queries
│   ├── semantic_search.py # post lookup and similarity results
│   └── utils.py           # configuration loading
├── notebooks/
│   └── train.ipynb        # legacy sentiment experiment
├── data/
│   ├── raw/               # raw data (JSON)
│   └── processed/         # processed data (JSON)
├── sessions/              # saved Telethon sessions
├── main.py                # entry point
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```
