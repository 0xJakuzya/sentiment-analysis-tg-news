import asyncio
import os

from utils import config
from telegram_scraper import TelegramScraper
from mongo import MongoDBClient
from preprocessing import TextProcessor


class Pipeline:

    def __init__(self, session_name=None):
        self.session_name = session_name or os.getenv("SESSION_NAME")
        self.mongo = MongoDBClient()
        self.scraper = TelegramScraper(self.session_name, self.mongo)
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
        out = []
        for msg in messages:
            text = self.cleaner.clean(msg["message"])
            msg["cleaned_text"] = text
            msg["is_processed"] = True
            out.append(msg)
        return out

    def classify(self, messages):
        for msg in messages:
            msg["sentiment"] = None
            msg["confidence"] = None
        return messages

    async def run(self):
        pipeline_config = config.get("pipeline", {})
        limit = pipeline_config.get("messages_per_channel", 50)
        channels = config.get("channels") or []

        await self.scraper.connect()
        try:
            raw = await self.parse_raw_messages(channels, limit)
        finally:
            await self.scraper.disconnect()
        cleaned = self.clean_raw_messages(raw)
        classified = self.classify(cleaned)
        self.mongo.save_processed_messages(classified)
        return classified

    def close(self):
        self.mongo.close()
