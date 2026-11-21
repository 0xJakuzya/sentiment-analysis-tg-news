import asyncio
from src.inference import Inference

def main():
    pipeline = Inference()
    try:
        asyncio.run(pipeline.run())
    finally:
        pipeline.close()

if __name__ == "__main__":
    main()
