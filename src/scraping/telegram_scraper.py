import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from telethon import TelegramClient
from telethon.errors import RPCError, SessionPasswordNeededError
from src.db.mongo import MongoDBClient

load_dotenv()

class TelegramScraper:

    def __init__(self, session_name: str, mongo_client):
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
    
        session_dir = os.getenv("SESSION_DIR")
        Path(session_dir).mkdir(parents=True, exist_ok=True)

        session_name = os.getenv("SESSION_NAME")
        session_path = os.path.join(session_dir, session_name)
        self.session_name = session_path

        self.client = None
        self.db_client = mongo_client or MongoDBClient()

    async def connect(self):

        try:
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            await self.client.start()

            if not await self.client.is_user_authorized():
                phone = input("Введите номер телефона: ")
                await self.client.send_code_request(phone)
                code = input("Введите код из Telegram: ")
                try:
                    await self.client.sign_in(phone, code)
                except SessionPasswordNeededError:
                    password = input("Введите пароль 2FA: ")
                    await self.client.sign_in(password=password)

            me = await self.client.get_me()
            print(f"Успешно авторизован как: {me.username} ({me.id})")
            return True

        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()
            print("Отключен от Telegram")

    async def get_channel(self, channel_name):
        if not self.client:
            raise RuntimeError("Telegram client is not connected. Call connect() first.")

        try:
            return await self.client.get_entity(channel_name)
        except ValueError:
            print(f"Канал '{channel_name}' не найден.")
            return None
        except RPCError as exc:
            print(f"Ошибка при получении канала '{channel_name}': {exc}")
            return None

    async def parse_channel(self, channel_name, limit=100):
        
        if not self.client:
            raise RuntimeError("Telegram client is not connected. Call connect() first.")

        channel = await self.get_channel(channel_name)
        if channel is None:
            return []

        messages = []
        async for message in self.client.iter_messages(channel, limit=limit):
            if not getattr(message, "message", None):
                continue

            messages.append(
                {
                    "id": message.id,
                    "date": message.date,
                    "message": message.message,
                    "views": message.views,
                    "channel_id": getattr(channel, "id", None),
                    "channel_username": getattr(channel, "username", None),
                }
            )

        return messages

    def save2mongodb(self, messages):
        if not messages:
            print("Нет сообщений для сохранения.")
            return 0

        saved = self.db_client.save_messages(messages)
        print(f"Сохранено сообщений: {saved}")
        return saved
