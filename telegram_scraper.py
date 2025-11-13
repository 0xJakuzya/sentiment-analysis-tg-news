import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from telethon import TelegramClient
from telethon.errors import RPCError, SessionPasswordNeededError

from config import TELEGRAM_API_HASH, TELEGRAM_API_ID
from mongo import MongoDBClient


class TelegramScraper:

    def __init__(self, session_name: str, mongo_client: Optional[MongoDBClient] = None):
        self.api_id = TELEGRAM_API_ID
        self.api_hash = TELEGRAM_API_HASH

        session_dir = os.getenv("SESSION_DIR", "sessions")
        Path(session_dir).mkdir(parents=True, exist_ok=True)
        session_path = os.path.join(session_dir, session_name)

        self.session_name = session_path
        self.client: Optional[TelegramClient] = None
        self.db_client = mongo_client or MongoDBClient() 

    async def connect(self) -> bool:
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

    async def disconnect(self) -> None:
        if self.client:
            await self.client.disconnect()
            print("Отключен от Telegram")

    async def get_channel(self, channel_name: str):
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

    async def parse_channel(self, channel_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        
        if not self.client:
            raise RuntimeError("Telegram client is not connected. Call connect() first.")

        channel = await self.get_channel(channel_name)
        if channel is None:
            return []

        messages: List[Dict[str, Any]] = []
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

    def save2mongodb(self, messages: List[Dict[str, Any]]) -> int:
        if not messages:
            print("Нет сообщений для сохранения.")
            return 0

        saved = self.db_client.save_messages(messages)
        print(f"Сохранено сообщений: {saved}")
        return saved
