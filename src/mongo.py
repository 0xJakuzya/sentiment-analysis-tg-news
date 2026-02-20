import json
import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class MongoDBClient:
    
    def __init__(self):

        self.uri = os.getenv("MONGO_ADDRESS")
        self.db_name = os.getenv("MONGO_DATABASE_NAME")
        self.collection_name = os.getenv("MONGO_COLLECTION_NAME")

        os.makedirs("data/raw", exist_ok=True)
        os.makedirs("data/processed", exist_ok=True)

        self.client = MongoClient(self.uri)
        self.collection = self.client[self.db_name][self.collection_name]
        self.create_indexes()

    def create_indexes(self):
        """create unique indexes for the collection"""
        self.collection.create_index(
            [("id", 1), ("channel_id", 1)], 
            unique=True, 
            name="message_channel_unique"
        )

    def save_local(self, messages, suffix):
        now = datetime.utcnow()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"data/{suffix}/{suffix}_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2, default=str)

    def save_raw_messages(self, messages):
        self.save_local(messages, "raw")
        now = datetime.utcnow()
        count = 0
        for msg in messages:
            result = self.collection.update_one(
                {"id": msg["id"], "channel_id": msg["channel_id"]},
                {
                    "$setOnInsert": {
                        "id": msg["id"],
                        "channel_id": msg["channel_id"],
                        "created_at": now,
                    },
                    "$set": {
                        "message": msg.get("message"),
                        "views": msg.get("views"),
                        "date": msg.get("date"),
                        "channel_username": msg.get("channel_username"),
                        "is_processed": msg.get("is_processed", False),
                        "sentiment": msg.get("sentiment"),
                        "confidence": msg.get("confidence"),
                        "updated_at": now
                    }
                },
                upsert=True
            )
            count += 1 if result.upserted_id else 0
        return count

    def save_processed_messages(self, messages):
        self.save_local(messages, "processed")
        now = datetime.utcnow()
        for msg in messages:
            self.collection.update_one(
                {"id": msg["id"], "channel_id": msg["channel_id"]},
                {
                    "$set": {
                        "cleaned_text": msg.get("cleaned_text"),
                        "is_processed": True,
                        "processed_at": now
                    }
                },
                upsert=True
            )

    def get_messages(self):
        return list(self.collection.find({}))

    def close(self):
        """close the mongoDB client"""
        self.client.close()