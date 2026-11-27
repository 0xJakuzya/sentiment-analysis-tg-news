import asyncio
from contextlib import closing
from src.embedder import Embedder
from src.inference import Inference
from src.qdrantdb import Qdrant

def main():
    with closing(Inference()) as pipeline:
        asyncio.run(pipeline.run())
        with closing(Qdrant()) as qdrant:
            Embedder(pipeline.mongo, qdrant).process_messages()

if __name__ == "__main__":
    main()
