import json
import os
from datetime import datetime
from pymongo import MongoClient

class MongoDBClient:
    def __init__(self, config):
        client_config = config["client"]
        self.uri = f"mongodb://{client_config['host']}:{client_config['port']}"
        self.db_name = config["database_name"]
        self.collection_name = config["documents_collection_name"]
        
        os.makedirs("data/raw", exist_ok=True)
        os.makedirs("data/processed", exist_ok=True)
        
        self._client = MongoClient(self.uri)
        self._collection = self._client[self.db_name][self.collection_name]
        self._create_indexes()

    def _create_indexes(self):
        self._collection.create_index(
            [("id", 1), ("channel_id", 1)], 
            unique=True, 
            name="message_channel_unique"
        )

    def _save_local(self, messages, suffix):
        filename = f"data/{suffix}/{suffix}_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2, default=str)

    def save_messages(self, messages):
        self._save_local(messages, "raw")
        saved_count = 0
        for msg in messages:
            result = self._collection.update_one(
                {"id": msg["id"], "channel_id": msg["channel_id"]},
                {
                    "$setOnInsert": {
                        "id": msg["id"],
                        "channel_id": msg["channel_id"],
                        "created_at": datetime.utcnow(),
                    },
                    "$set": {
                        "message": msg.get("message"),
                        "views": msg.get("views"),
                        "date": msg.get("date"),
                        "channel_username": msg.get("channel_username"),
                        "is_processed": msg.get("is_processed", False),
                        "sentiment": msg.get("sentiment"),
                        "confidence": msg.get("confidence"),
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            if result.upserted_id:
                saved_count += 1
        return saved_count

    def save_processed_messages(self, messages):
        self._save_local(messages, "processed")
        for msg in messages:
            self._collection.update_one(
                {"id": msg["id"], "channel_id": msg["channel_id"]},
                {
                    "$set": {
                        "cleaned_message": msg.get("cleaned_message"),
                        "is_processed": True,
                        "processed_at": datetime.utcnow()
                    }
                }
            )

    def get_all_messages(self):
        return list(self._collection.find({}))

    def close(self):
        self._client.close()