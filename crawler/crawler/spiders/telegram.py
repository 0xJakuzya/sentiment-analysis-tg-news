import scrapy
import html2text
from datetime import datetime, timezone


def html2text_setup():
    instance = html2text.HTML2Text(bodywidth=0)
    instance.ignore_links = True #ссылки не будут отображться при парсинге
    instance.ignore_images = True  #изображения игнорируются
    instance.ignore_tables = True #таблицы не конвертируются
    instance.ignore_emphasis = True #игнорируются выделения
    instance.ul_item_mark = "" #маркеры списков не отображаются
    return instance


class TelegramSpider(scrapy.Spider):
    name = "telegram"
    channel_url = "https://t.me/s/{}"
    post_url_template = "https://t.me/{}?embed=1"

    def __init__(self, channel_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_name = channel_name
        self.start_urls = [self.channel_url.format(channel_name)]
        self.html2text = html2text_setup()

    def parse(self, response):
        posts = response.css("div.tgme_widget_message_wrap")
        for post in posts:
            text_html = post.css("div.tgme_widget_message_text").get()
            text = self.html2text.handle(text_html).strip()
            pub_time = post.css("time.time::attr(datetime)").get()
            pub_timestamp = None
            if pub_time:
                pub_dt = datetime.strptime(pub_time, "%Y-%m-%dT%H:%M:%S%z")
                pub_timestamp = int(pub_dt.timestamp())

            yield {
                "channel": self.channel_name,
                "text": text,
                "publish_time": pub_time,
                "publish_timestamp": pub_timestamp,
                "post_url": response.url,
            }
