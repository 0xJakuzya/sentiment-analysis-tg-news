import os
import joblib
from .utils import PROJECT_ROOT, config
from .telegram_scraper import TelegramScraper
from .mongodb import MongoDBClient
from .preprocessing import TextProcessor

class Inference:
    def __init__(self, session_name=None):
        self.session_name = session_name or os.getenv("SESSION_NAME")
        model_dir = PROJECT_ROOT / "models"
        missing = [name for name in ("tfidf.pkl", "logreg.pkl") if not (model_dir / name).is_file()]
        if missing:
            print(f'missing models in {model_dir}')
        self.tfidf = joblib.load(model_dir / "tfidf.pkl")
        self.model = joblib.load(model_dir / "logreg.pkl")
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
        batch = [msg for msg in messages if (msg.get("message") or "").strip()]
        if not batch:
            return messages
        features = self.tfidf.transform([msg["message"] for msg in batch])
        probabilities = self.model.predict_proba(features)
        for msg, scores in zip(batch, probabilities):
            index = scores.argmax()
            msg["sentiment"] = int(self.model.classes_[index])
            msg["confidence"] = float(scores[index])
        return messages

    async def run(self):
        pipeline_config = config.get("pipeline", {})
        limit = pipeline_config.get("messages_per_channel", 50)
        channels = config.get("channels") or []
        try:
            await self.scraper.connect()
            raw = await self.parse_raw_messages(channels, limit)
        finally:
            await self.scraper.disconnect()
        cleaned = self.clean_raw_messages(raw)
        classified = self.classify(cleaned)
        self.mongo.save_processed_messages(classified)
        return classified

    def close(self):
        self.mongo.close()
