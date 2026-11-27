from datetime import datetime, timedelta
from .embedder import embedding_payload, model_version, point_id

class SemanticSearch:
    def __init__(self, mongo, qdrant):
        self.mongo = mongo
        self.qdrant = qdrant
        self.version = model_version()

    def search(self, channel_id, message_id, limit=10, hours=24):
        key = (channel_id, message_id)
        pid = point_id(*key)
        msg = self.mongo.get_messages_by_keys([key]).get(key)
        payload = embedding_payload(msg or {}, self.version)
        point = self.qdrant.get_points([pid], with_vectors=True).get(pid) if payload else None
        
        if point is None or not point.vector or point.payload != payload:
            return []

        start = end = None
        if hours is not None:
            date = datetime.fromisoformat(payload["date"])
            start, end = date - timedelta(hours=hours), date + timedelta(hours=hours)

        results = {}
        offset = 0
        while len(results) < limit:
            remaining = limit - len(results)
            hits = self.qdrant.search_similar(point.vector, pid, start=start, end=end, limit=remaining, offset=offset)
            keys = []
            for hit in hits:
                data = hit.payload or {}
                keys.append((data.get("channel_id"), data.get("message_id")))

            messages = self.mongo.get_messages_by_keys(keys)
            
            for hit, candidate in zip(hits, keys):
                current = messages.get(candidate)
                if not current or str(hit.id) != point_id(*candidate) or embedding_payload(current, self.version) != hit.payload:
                    continue
                channel, post = candidate
                username = current.get("channel_username")
                link = f"https://t.me/{username}/{post}" if username else f"https://t.me/c/{channel}/{post}"
                results[candidate] = {"channel_id": channel, "message_id": post, "score": hit.score, "date": hit.payload["date"], "link": link, "text": current["cleaned_text"]}
            
            if len(hits) < remaining:
                break
            offset += len(hits)
        
        return list(results.values())
