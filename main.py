import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from pipeline import Pipeline

def main():
    pipeline = Pipeline()
    try:
        asyncio.run(pipeline.run())
    finally:
        pipeline.close()

if __name__ == "__main__":
    main()
