from datetime import datetime, timezone
from hashlib import sha256
from uuid import NAMESPACE_URL, uuid5
from qdrant_client import models
from .utils import config

from sentence_transformers import SentenceTransformer

def point_id(channel_id, message_id):
    return str(uuid5(NAMESPACE_URL, f"telegram:{channel_id}:{message_id}"))

def model_version():
    cfg = config.get("pipeline")
    return f"{cfg['embedding_model']}@{cfg['embedding_revision']}"

def embedding_payload(msg, version):
    text = msg.get("cleaned_text")
    date = msg.get("date")
    if not msg.get("is_processed", True) or not isinstance(text, str) or not text.strip() or not isinstance(date, datetime):
        return None
    date = date.replace(tzinfo=timezone.utc) if date.tzinfo is None else date.astimezone(timezone.utc)
    return {
        "channel_id": msg["channel_id"],
        "message_id": msg["id"],
        "channel_username": msg.get("channel_username"),
        "date": date.isoformat(timespec="milliseconds"),
        "embedding_model": version,
        "text_hash": sha256(text.strip().encode("utf-8")).hexdigest(),
    }

class Embedder:
    def __init__(self, mongo, qdrant):
        self.mongo = mongo
        self.qdrant = qdrant
        cfg = config.get("pipeline")
        self.model = SentenceTransformer(cfg["embedding_model"], revision=cfg["embedding_revision"])
        self.version = model_version()

    def process_messages(self, batch_size=32):
        self.qdrant.create_collection(self.model.get_embedding_dimension(), self.version)
        with self.mongo.iter_index_messages() as cursor:
            batch = []
            for msg in cursor:
                batch.append(msg)
                if len(batch) == batch_size:
                    self.embedded_batch(batch)
                    batch.clear()
            if batch:
                self.embedded_batch(batch)

    def embedded_batch(self, batch):
        ids = [point_id(msg["channel_id"], msg["id"]) for msg in batch]
        old = self.qdrant.get_points(ids)
        pending = []
        texts = []
        remove = []
        keys = []
        for pid, msg in zip(ids, batch):
            payload = embedding_payload(msg, self.version)
            previous = old.get(pid)
            if payload == (previous.payload if previous else None):
                continue
            key = (msg["channel_id"], msg["id"])
            keys.append(key)
            if payload:
                pending.append((key, pid, payload))
                texts.append(msg["cleaned_text"].strip())
            else:
                remove.append((key, pid))

        if not keys:
            return

        vectors = self.model.encode(texts, show_progress_bar=False) if texts else []
        latest = self.mongo.get_messages_by_keys(keys)
        points = []
        stale = []
        
        for (key, pid, payload), vector in zip(pending, vectors, strict=True):
            if embedding_payload(latest.get(key, {}), self.version) == payload:
                points.append(models.PointStruct(id=pid, vector=list(vector), payload=payload))
        
        for key, pid in remove:
            if embedding_payload(latest.get(key, {}), self.version) is None:
                stale.append(pid)

        self.qdrant.upsert(points)
        self.qdrant.delete_points(stale)
