import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Sequence

import pymongo
from pymongo import MongoClient

class MongoDBClient:

    def __init__(
        self,
        uri: Optional[str] = None,
        db_name: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        self.uri = uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = db_name or os.getenv("MONGODB_DB", "telegram_sentiment")
        self.collection_name = (
            collection_name or os.getenv("MONGODB_COLLECTION", "messages")
        )
        self._client = None
        self._collection = None
        self._memory_store: List[dict] = []

        if MongoClient is not None:
            try:
                self._client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
                self._client.server_info()
                self._collection = self._client[self.db_name][self.collection_name]
            except Exception:
                self._client = None
                self._collection = None

    @property
    def available(self) -> bool:
        return self._collection is not None

    def save_messages_to_json(self, messages: Sequence[dict], filepath: Optional[str] = None) -> int:
        if not messages:
            return 0
        
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/raw/messages_{timestamp}.json"
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        json_messages = []
        for msg in messages:
            json_msg = dict(msg)
            if isinstance(json_msg.get("date"), datetime):
                json_msg["date"] = json_msg["date"].isoformat()
            if isinstance(json_msg.get("saved_at"), datetime):
                json_msg["saved_at"] = json_msg["saved_at"].isoformat()
            json_messages.append(json_msg)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(json_messages, f, ensure_ascii=False, indent=2)
            print(f"Сохранено {len(json_messages)} сообщений в JSON: {filepath}")
            return len(json_messages)
        except Exception as e:
            print(f"Ошибка при сохранении в JSON: {e}")
            return 0

    def save_messages(self, messages: Sequence[dict]) -> int:

        if not messages:
            return 0

        normalized: List[dict] = []
        for message in messages:
            doc = dict(message)
            doc.setdefault("saved_at", datetime.utcnow())
            normalized.append(doc)

        self.save_messages_to_json(normalized)

        if self.available:
            try:
                result = self._collection.insert_many(normalized, ordered=False)  
                return len(result.inserted_ids)
            except PyMongoError:
                pass
            
        self._memory_store.extend(normalized)
        return len(normalized)

    def fetch_cached(self) -> List[dict]:
        return list(self._memory_store)

    def close(self) -> None:
        if self._client is not None:
            self._client.close()