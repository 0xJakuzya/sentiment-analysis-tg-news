import asyncio
import sys
from pathlib import Path
from inference import Pipeline

def main():
    pipeline = Pipeline()
    try:
        asyncio.run(pipeline.run())
    finally:
        pipeline.close()

if __name__ == "__main__":
    main()
