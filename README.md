# Sentiment Analysis для Telegram новостей

Проект для анализа тональности новостей из Telegram каналов с использованием машинного обучения.

## Будущие Возможности

- Скрапинг сообщений из Telegram каналов
- Предобработка текста (очистка HTML, нормализация, удаление URL и т.д.)
- Классификация тональности (позитив/негатив/нейтрал) с использованием BERT моделей
- Сохранение результатов в MongoDB и JSON
- Docker поддержка для легкого развертывания

## Структура проекта
```
Sentiment-Analysis-Telegram-news/
├── src/
│   ├── scraping/          # Модуль скрапинга Telegram
│   ├── preprocessing/     # Предобработка текста
│   ├── embedding/         # Создание эмбеддингов
│   ├── classification/    # Классификация тональности
│   ├── pipeline/          # Пайплайн обработки
│   └── db/                # Работа с MongoDB
├── data/                  # Данные (raw, processed, labeled)
├── sessions/              # Telegram сессии
├── config.py              # Конфигурация
├── main.py                # Главный скрипт
├── requirements.txt       # Зависимости
├── Dockerfile             # Docker образ
└── docker-compose.yml     # Docker Compose конфигурация
```
### Структура модулей

- `src/scraping/` - Скрапинг через Telethon
- `src/preprocessing/` - Очистка и нормализация текста
- `src/embedding/` - Создание векторных представлений (BERT, TF-IDF)
- `src/classification/` - Классификация тональности
- `src/pipeline/` - Оркестрация всех компонентов
- `src/db/` - Работа с MongoDB

