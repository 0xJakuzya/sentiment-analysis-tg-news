# Sentiment Analysis для Telegram новостей

Проект для анализа тональности новостей из Telegram каналов с использованием машинного обучения.

## Возможности

- Скрапинг сообщений из Telegram каналов
- Предобработка текста (очистка сырых данных, нормализация и т.д.) 
- Классификация тональности (позитив/негатив/нейтрал) с использованием BERT моделей
- Сохранение результатов в MongoDB
- Docker поддержка для легкого развертывания

## Структура проекта
```
Sentiment-Analysis-Telegram-news
├── config/
|   ├── channel.json      # Список телеграмм-каналов 
│   ├── mongo_config.json # Конфигурация MongoDB              
├── src/
│   ├── telegram_scraping # Модуль скрапинга Telegram
│   ├── preprocessing     # Предобработка текста
│   ├── embedding         # Создание эмбеддингов
│   ├── classification    # Классификация тональности
│   ├── pipeline          # Пайплайн обработки
│   └── mongo             # Работа с MongoDB
├── sessions/              # Telegram сессии
├── requirements.txt       # Зависимости
├── Dockerfile             # Docker образ
└── docker-compose.yml     # Docker Compose конфигурация
```


