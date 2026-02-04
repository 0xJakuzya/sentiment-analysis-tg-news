import os
from pathlib import Path
from dotenv import load_dotenv
import sys
sys.path.append('src')

from telethon import TelegramClient
from telethon.errors import RPCError, SessionPasswordNeededError
from mongo import MongoDBClient

load_dotenv()

class TelegramScraper:
    def __init__(self, session_name: str, mongo_client):
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        
        session_path = Path(os.getenv("SESSION_DIR")) / os.getenv("SESSION_NAME")
        session_path.parent.mkdir(parents=True, exist_ok=True)
        self.session_name = str(session_path)
        
        self.client = None
        self.db_client = mongo_client

    async def connect(self):
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
        
        return True

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()

    async def parse_channel(self, channel_name, limit=100):
        channel = await self.client.get_entity(channel_name)
        messages = []
        
        async for message in self.client.iter_messages(channel, limit=limit):
            if message.message:
                messages.append({
                    "id": message.id,
                    "date": message.date,
                    "message": message.message,
                    "views": message.views,
                    "channel_id": channel.id,
                    "channel_username": channel.username,
                    "is_processed": False,
                    "sentiment": None,
                    "confidence": None
                })
        
        return messages

    def save2mongodb(self, messages):
        return self.db_client.save_messages(messages) if messages else 0