import json
from datetime import datetime
from pymongo import MongoClient

class MongoDBClient:

    def __init__(self, config_path="config/mongo_config.json"):
        with open(config_path) as f:
            config = json.load(f)
        
        client_config = config["client"]
        self.uri = f"mongodb://{client_config['host']}:{client_config['port']}"
        self.db_name = config["database_name"]
        self.collection_name = config["documents_collection_name"]
        
        self._client = MongoClient(self.uri)
        self._collection = self._client[self.db_name][self.collection_name]
        self._create_indexes()

    def _create_indexes(self):
        try:
            self._collection.create_index(
                [("id", 1), ("channel_id", 1)], 
                unique=True, 
                name="message_channel_unique"
            )
        except Exception:
            pass

    def save_messages(self, messages):
        saved_count = 0
        for message in messages:
            message.setdefault("saved_at", datetime.utcnow())
            message.setdefault("is_processed", False)
            message.setdefault("sentiment", None)
            message.setdefault("confidence", None)
            
            result = self._collection.update_one(
                {"id": message["id"], "channel_id": message["channel_id"]},
                {"$setOnInsert": message},
                upsert=True
            )
            if result.upserted_id:
                saved_count += 1
        
        return saved_count

    def get_all_messages(self):
        return list(self._collection.find({}))

    def close(self):
        self._client.close()