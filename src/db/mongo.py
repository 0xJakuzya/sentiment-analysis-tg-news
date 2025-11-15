import os
import json
from datetime import datetime
from pathlib import Path

from pymongo import MongoClient
from pymongo.errors import PyMongoError, BulkWriteError


class MongoDBClient:

    def __init__(self, uri=None, db_name=None, collection_name=None):
        self.uri = uri or os.getenv("MONGODB_URI")
        self.db_name = db_name or os.getenv("MONGODB_DB")
        self.collection_name = collection_name or os.getenv("MONGODB_COLLECTION")
        self._client = None
        self._collection = None
        self._connect()
        self._create_indexes()    

    def _connect(self):
        try:
            self._client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            self._client.server_info()  
            self._collection = self._client[self.db_name][self.collection_name]
            print(f"Подключено к MongoDB: {self.db_name}/{self.collection_name}")
        except Exception as e:
            print(f"Не удалось подключиться к MongoDB: {e}")
            self._client = None
            self._collection = None

    def _create_indexes(self):
        if not self.available:
            return
        try:
            existing_indexes = self._collection.index_information()
            if "message_channel_unique" in existing_indexes:
                self._collection.drop_index("message_channel_unique")
                print("Старый индекс удален")

            self._collection.create_index(
                [("id", 1), ("channel_id", 1)], 
                unique=True, 
                name="message_channel_unique"
            )
            self._collection.create_index([("date", -1)], name="date_desc")
            self._collection.create_index([("channel_id", 1)], name="channel_id")
            self._collection.create_index(
            [("is_processed", 1)], 
            name="is_processed"
            )
            self._collection.create_index([("sentiment", 1)], name="sentiment")
            print("Все индексы успешно созданы")
            
        except Exception as e:
            print(f"Ошибка при создании индексов: {e}")

    @property
    def available(self):
        return self._collection is not None

    def _save_to_raw_files(self, messages):
        try:
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
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(json_messages, f, ensure_ascii=False, indent=2)
            print(f"Сохранено {len(json_messages)} сообщений в JSON: {filepath}")
        except Exception as e:
            print(f"Ошибка при сохранении в JSON: {e}")

    def save_messages(self, messages):
        if not messages:
            return 0

        normalized = []
        for message in messages:
            doc = dict(message)
            doc.setdefault("saved_at", datetime.utcnow())
            doc.setdefault("is_processed", False)
            doc.setdefault("sentiment", None)
            doc.setdefault("confidence", None)
            normalized.append(doc)

        self._save_to_raw_files(normalized)

        if self.available:
            saved_count = 0
            for message in normalized:
                try:
                    result = self._collection.update_one(
                        {
                            "id": message["id"],
                            "channel_id": message["channel_id"]
                        },
                        {
                            "$setOnInsert": message  
                        },
                        upsert=True
                    )
                    if result.upserted_id:
                        saved_count += 1
                except PyMongoError as e:
                    print(f"Ошибка при сохранении сообщения {message.get('id')}: {e}")
                    continue
            print(f"Сохранено {saved_count} новых сообщений в MongoDB")
            return saved_count
        print("MongoDB недоступна. Сообщения сохранены только в JSON.")
        return 0

    def close(self) -> None:
        if self._client:
            self._client.close()
            print("Соединение с MongoDB закрыто")