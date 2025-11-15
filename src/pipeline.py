import asyncio
import os
import sys
import json
sys.path.append('src')

from telegram_scraper import TelegramScraper
from mongo import MongoDBClient
from preprocessing import TextPreprocessor
from embedding import FeatureExtractor  
from classification import SentimentModel

class Pipeline:
    def __init__(self, session_name, mongo_config_path="config/mongo_config.json"):
        self.session_name = session_name
        self.mongo_client = MongoDBClient(mongo_config_path)
        self.scraper = TelegramScraper(session_name, self.mongo_client)
        # self.preprocessor = TextPreprocessor()
        # self.embedder = FeatureExtractor()
        # self.classifier = SentimentModel()

    def load_channels(self, channels_file="config/channels.json"):
        with open(channels_file) as f:
            return json.load(f)

    async def scrape_channel(self, channel_name, limit):
        await self.scraper.connect()
        messages = await self.scraper.parse_channel(channel_name, limit)
        await self.scraper.disconnect()
        if messages:
            self.scraper.save2mongodb(messages)
        return messages

    def get_unprocessed_messages(self):
        messages = self.mongo_client.get_all_messages()
        return [msg for msg in messages if not msg.get('is_processed')]

    def preprocess_messages(self, messages):
        return messages

    def classify_messages(self, messages):
        return messages

    def save_results(self, messages):
        return messages

    async def run_full_pipeline(self, channels_file="config/channels.json", limit=10):

        channels = self.load_channels(channels_file)
        for channel in channels:
            await self.scrape_channel(channel, limit)
        unprocessed = self.get_unprocessed_messages()
        processed = self.preprocess_messages(unprocessed)
        classified = self.classify_messages(processed)
        self.save_results(classified)
        
        return classified

    def close(self):
        self.mongo_client.close()

if __name__ == "__main__":

    session_name = os.getenv("SESSION_NAME")
    pipeline = Pipeline(session_name)
    try:
        results = asyncio.run(pipeline.run_full_pipeline())
    finally:
        pipeline.close()