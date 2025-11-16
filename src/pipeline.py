import asyncio
import os
import sys
sys.path.append('src')

from utils import config  
from telegram_scraper import TelegramScraper
from mongo import MongoDBClient
from preprocessing import TextProcessor

class Pipeline:

    def __init__(self, session_name):
        self.session_name = session_name
        self.mongo  = MongoDBClient(config.get("mongo_config"))
        self.scraper = TelegramScraper(session_name, self.mongo)
        self.cleaner  = TextProcessor(config.get("preprocessing", {}).get("text_processor", {}))
        # self.embedder = FeatureExtractor()
        # self.classifier = Sentiment

    def _load_channels(self):
        return config.get("channels", [])

    async def scrape(self, channel_name, limit):
        await self.scraper.connect()
        try:
            messages = await self.scraper.parse_channel(channel_name, limit)
            if messages:
                self.scraper.save_to_mongodb(messages)
            return messages
        finally:
            await self.scraper.disconnect()

    def clean_messages(self, messages):
        cleaned = []
        for msg in messages:
            if "message" in msg:
                cleaned_text = self.cleaner.clean(msg["message"])
                if cleaned_text:  
                    msg["cleaned_text"] = cleaned_text
                    msg["is_processed"] = True
                    cleaned.append(msg)
        return cleaned

    def classify(self, messages):
        for message in messages:
            message["sentiment"] = None
            message["confidence"] = None
        return messages

    def save_to_db(self, messages):
        self.mongo.save_processed_messages(messages)

    async def run(self, limit=10):
        all_messages = []
        for channel in self._load_channels():
            all_messages.extend(await self.scrape(channel, limit))
        cleaned_messages = self.clean_messages(all_messages)
        classified_messages = self.classify(cleaned_messages)
        self.save_to_db(classified_messages)
        return classified_messages

    def close(self):
        self.mongo.close()

if __name__ == "__main__":

    pipeline = Pipeline(os.getenv("SESSION_NAME"))
    try:
        asyncio.run(pipeline.run(limit=50))
    except Exception as e:
        print(f"Ошибка в пайплайне: {e}")
    finally:
        pipeline.close()