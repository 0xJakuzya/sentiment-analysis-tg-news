# sentiment analysis for telegram news

a project for sentiment analysis of news from Telegram channels using machine learning

## features

- scraping messages from Telegram channels  
- text preprocessing (raw data cleaning, normalization, etc.)  
- sentiment classification (positive / negative / neutral) using BERT-based models  
- storing results in MongoDB  
- docker support for easy deployment  

## project Structure
```
sentiment-analysis-telegram-news
├── config/
|   ├── channel.json      # list telegram-channels 
│   ├── mongo_config.json # configuration MongoDB              
├── src/
│   ├── telegram_scraping # telegram scrap modules
│   ├── preprocessing     # text processing
│   ├── embedding         # embedding generation
│   ├── classification    # sentiment classification
│   ├── pipeline          # processing pipeline
│   └── mongo             # mongodb integration
├── sessions/              # telegram sessions
├── requirements.txt       
├── Dockerfile             
└── docker-compose.yml     
```



