import os
from .utils import config
from .telegram_scraper import TelegramScraper
from .mongodb import MongoDBClient
from .preprocessing import TextProcessor

class Inference:
    def __init__(self, session_name=None):
        self.mongo = MongoDBClient()
        self.scraper = TelegramScraper(session_name or os.getenv("SESSION_NAME"))
        self.cleaner = TextProcessor()

    async def parse_raw_messages(self, channels, limit):
        raw = []
        for channel in channels:
            messages = await self.scraper.parse_channel(channel, limit)
            if messages:
                self.mongo.save_raw_messages(messages)
                raw.extend(messages)
        return raw

    def clean_raw_messages(self, messages):
        for msg in messages:
            msg["cleaned_text"] = self.cleaner.clean(msg["message"])
            msg["is_processed"] = True
        return messages

    async def run(self):
        pipeline_config = config.get("pipeline", {})
        limit = pipeline_config.get("messages_per_channel")
        channels = config.get("channels") or []
        try:
            await self.scraper.connect()
            raw = await self.parse_raw_messages(channels, limit)
        finally:
            await self.scraper.disconnect()
        cleaned = self.clean_raw_messages(raw)
        self.mongo.save_processed_messages(cleaned)
        return cleaned

    def close(self):
        self.mongo.close()
