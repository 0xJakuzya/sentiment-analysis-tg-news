# sentiment analysis for telegram news

sentiment analysis for russian-language telegram news using telethon, TF-IDF, and logistic regression. posts and predictions are saved to mongoDB and local json files.

## features

- telegram channel scraping with Telethon
- text cleaning and normalization
- binary sentiment classification with TF-IDF and logistic regression
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
```

## running

### locally

```bash
docker compose up -d mongodb
docker compose run --rm --build scraper
python main.py
```

## model and results

the classifier uses the original message as input. each processed record includes cleaned_text, the predicted sentiment (0 or 1), and confidence, the model's estimated probability for the predicted class.

| Evaluation set | Records | Accuracy | Macro-F1 |
|---|---:|---:|---:|
| `dev.csv` | 424 | 0.9269 | 0.9206 |

## project structure

```
sentiment-analysis-tg-news
├── config/
│   ├── channels.json      # channels to scrape
│   ├── pipeline.json      # message limit
│   └── preprocessing.json # text preprocessing rules
├── src/
│   ├── inference.py       # scrape, clean, classify, and save
│   ├── telegram_scraper.py # Telegram client
│   ├── preprocessing.py   # text cleaning
│   ├── mongodb.py         # MongoDB and JSON storage
│   └── utils.py           # configuration loading
├── models/
│   ├── tfidf.pkl          # fitted vectorizer
│   └── logreg.pkl         # trained classifier
├── data/
│   ├── raw/               # raw data (JSON)
│   └── processed/         # processed data (JSON)
├── sessions/              # saved Telethon sessions
├── main.py                # entry point
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```
