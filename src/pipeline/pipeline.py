from src.scraping.telegram_scraper import TelegramScraper
from src.db.mongo import MongoDBClient
from src.preprocessing.preprocessing import TextPreprocessor
from src.embedding.embedding import FeatureExtractor
from src.classification.classification import SentimentModel



class Pipeline:

    def __init__(self, session_name, mongo_client):

        self.session_name = session_name
        self.mongo_client = mongo_client or MongoDBClient()
        self.scraper = TelegramScraper(session_name, self.mongo_client)
        self.preprocessor = TextPreprocessor()
        self.embedder = FeatureExtractor(method=method)
        self.classifier = SentimentModel()

    def scrape_channel():
        pass

    def preprocess_messages()
        pass

    def classify_messages():
        pass

    def save_results():
        pass

    def run_full_pipeline():
        pass

def run_pipeline(channel_name, limit, session_name)
    pipeline = Pipeline(session_name=session_name)
    return asyncio.run(pipeline.run_full_pipeline(channel_name, limit))

if __name__ == "__main__":
    
    results = run_pipeline(channel_name, limit)
