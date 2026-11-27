import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

load_dotenv()

class Qdrant:
    def __init__(self, client=None, collection_name=None):
        self.client = client if client is not None else QdrantClient(url=os.getenv("QDRANT_URL") or "http://localhost:6333")
        self.collection_name = collection_name or os.getenv("QDRANT_COLLECTION_NAME") or "news_messages"

    def create_collection(self, vector_size, model_version):
        name = self.collection_name
        expected = models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
        if not self.client.collection_exists(name):
            try:
                self.client.create_collection(name, vectors_config=expected, metadata={"embedding_model": model_version})
            except UnexpectedResponse as exc:
                if exc.status_code not in (400, 409) or not self.client.collection_exists(name):
                    raise
        
        info = self.client.get_collection(name)
        vectors = info.config.params.vectors
        metadata = info.config.metadata or {}
        
        if not isinstance(vectors, models.VectorParams) or (vectors.size, vectors.distance) != (expected.size, expected.distance) or metadata.get("embedding_model") != model_version:
            raise ValueError(f"Collection {name!r} has incompatible vectors or model. Use a new collection to reindex.")
        
        if "date" not in info.payload_schema:
            self.client.create_payload_index(name, "date", field_schema=models.PayloadSchemaType.DATETIME, wait=True)
        
        elif info.payload_schema["date"].data_type != models.PayloadSchemaType.DATETIME:
            raise ValueError(f"Collection {name!r} requires a datetime index for date")

    def upsert(self, points):
        if points:
            self.client.upsert(self.collection_name, points=points, wait=True)

    def get_points(self, ids, with_vectors=False):
        if not ids:
            return {}
        try:
            points = self.client.retrieve(self.collection_name, ids=ids, with_vectors=with_vectors)
        except UnexpectedResponse as exc:
            if exc.status_code != 404:
                raise
            return {}
        return {str(point.id): point for point in points}

    def delete_points(self, ids):
        if ids:
            self.client.delete(self.collection_name, points_selector=models.PointIdsList(points=ids), wait=True)

    def search_similar(self, vector, point_id, start=None, end=None, limit=10, offset=0):
        dates = [models.FieldCondition(key="date", range=models.DatetimeRange(gte=start, lte=end))] if start is not None else []
        query_filter = models.Filter(must=dates, must_not=[models.HasIdCondition(has_id=[point_id])])
        return self.client.query_points(self.collection_name, query=vector, query_filter=query_filter, limit=limit, offset=offset).points

    def close(self):
        self.client.close()
