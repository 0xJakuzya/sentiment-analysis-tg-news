import asyncio
import json
import os
from pathlib import Path

from src.scraping.telegram_scraper import TelegramScraper
from src.db.mongo import MongoDBClient


def load_channels(channels_file):
    try:
        with open(channels_file, "r", encoding="utf-8") as f:
            channels = json.load(f)
        if isinstance(channels, list):
            return channels
        return []
    except FileNotFoundError:
        print(f"Файл {channels_file} не найден. Создайте файл со списком каналов.")
        return []
    except json.JSONDecodeError:
        print(f"Ошибка при чтении {channels_file}. Проверьте формат JSON.")
        return []


async def parse_channel(channels, session_name, limit=10):

    if not channels:
        print("Нет каналов для парсинга.")
        return

    mongo_client = MongoDBClient()
    scraper = TelegramScraper(session_name, mongo_client)

    print("Подключение к Telegram...")
    if not await scraper.connect():
        print("Не удалось подключиться к Telegram")
        return

    for channel_name in channels:

        try:
            messages = await scraper.parse_channel(channel_name, limit=10)
            
            if messages:
                saved = scraper.save2mongodb(messages)
                print(f"Успешно: получено {len(messages)} сообщений, сохранено {saved}")
            else:
                print(f"Нет сообщений из канала {channel_name}")
                
        except Exception as e:
            print(f"Ошибка при парсинге канала {channel_name}: {e}")


    await scraper.disconnect()
    mongo_client.close()

async def main():

    channels_file = "config/channels.json"
    session_name = os.getenv("SESSION_NAME")
    channels = load_channels(channels_file)
    await parse_channel(channels, session_name=session_name, limit=10)


if __name__ == "__main__":
    asyncio.run(main())
