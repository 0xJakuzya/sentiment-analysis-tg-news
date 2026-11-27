import asyncio
import os
from getpass import getpass
from pathlib import Path
import qrcode
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

load_dotenv()

class TelegramScraper:
    def __init__(self, session_name=None):
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.client = None
        session_path = Path(os.getenv("SESSION_DIR", "sessions")) / (session_name or "session")
        session_path.parent.mkdir(parents=True, exist_ok=True)
        self.session_name = str(session_path)

    async def connect(self):
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        await self.client.connect()
        if not await self.client.is_user_authorized():
            while True:
                qr_login = await self.client.qr_login()
                wait_task = asyncio.create_task(qr_login.wait())
                await asyncio.sleep(0)
                qr = qrcode.QRCode(border=2)
                qr.add_data(qr_login.url)
                qr.make(fit=True)
                qr.print_ascii(invert=True)
                try:
                    await wait_task
                    break
                except asyncio.TimeoutError:
                    continue
                except SessionPasswordNeededError:
                    password = getpass("Введите пароль двухэтапной аутентификации Telegram: ")
                    await self.client.sign_in(password=password)
                    break
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
