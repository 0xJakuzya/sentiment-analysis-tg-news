# Sentiment Analysis для Telegram новостей

Проект для сбора и анализа тональности новостей из Telegram-каналов
## Возможности

- Скрапинг сообщений из Telegram-каналов (Telethon)
- Предобработка текста: удаление эмодзи, URL, служебных фраз, нормализация
- Сохранение сырых и обработанных данных в MongoDB и локальные JSON
- Docker для запуска пайплайна с MongoDB
- Конфигурация через JSON (каналы, пайплайн, правила очистки)

## Установка

```bash
git clone <repo>
cd Sentiment-Analysis-Telegram-news
pip install -r requirements.txt
```

## Настройка

### 1. Переменные окружения (.env)

Создайте `.env` в корне проекта:

```env
# Telegram API (получить на my.telegram.org)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# Сессия
SESSION_NAME=session
SESSION_DIR=sessions

# MongoDB
MONGO_ADDRESS=mongodb://localhost:27017
MONGO_DATABASE_NAME=telegram_sentiment
MONGO_COLLECTION_NAME=messages
```

### 2. Конфигурационные файлы (config/)

| Файл | Описание |
|------|----------|
| `channels.json` | Массив usernames каналов, например `["ruble30", "channel2"]` |
| `pipeline.json` | `messages_per_channel` — лимит сообщений на канал |
| `preprocessing.json` | Правила очистки текста (что удалять, пропускать, фильтровать) |

## Запуск

**Перед запуском обязательно запустите MongoDB:**

```bash
docker-compose up -d mongodb
```

### Локально

```bash
python main.py
```

При первом запуске введите номер телефона и код из Telegram для авторизации.

### Docker Compose

```bash
docker-compose up --build
```

## Структура проекта

```
Sentiment-Analysis-Telegram-news/
├── config/
│   ├── channels.json      # Каналы для парсинга
│   ├── pipeline.json      # Лимиты и настройки пайплайна
│   └── preprocessing.json # Правила предобработки текста
├── src/
│   ├── pipeline.py        # Пайплайн: scrape → clean → classify → save
│   ├── telegram_scraper.py # Скрапинг через Telethon
│   ├── preprocessing.py   # Очистка текста
│   ├── mongo.py           # Работа с MongoDB
│   ├── utils.py           # Загрузка конфигов
│   ├── embedding.py       # (заглушка) Эмбеддинги
│   └── classification.py  # (заглушка) Классификация тональности
├── data/
│   ├── raw/               # Сырые сообщения (JSON)
│   └── processed/         # Обработанные сообщения (JSON)
├── sessions/              # Сессии Telethon (создаётся автоматически)
├── main.py                # Точка входа
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```
