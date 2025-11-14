class TextPreprocessor:

    def __init__(self):
        pass

    def clean_html(self, texts):
        pass


    def normalize_text(self, texts):
        pass


    def remove_urls(self, texts):
        pass

    def remove_mentions(self, texts):
        pass

    def remove_hashtags(self, texts):
        pass

    def preprocess_articles(self, texts)

        processed = []
        for text in texts:
            
            text = self.clean_html(text)
            text = self.remove_urls(text)
            text = self.remove_mentions(text)
            text = self.remove_hashtags(text)
            text = self.normalize_text(text)

            processed.append(text)

        return processed
