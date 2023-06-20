from multiprocessing import Process, Queue
import os
import uuid
import json

from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.item import Field, Item
from scrapy.utils.project import get_project_settings
from scrapy import signals
from twisted.internet import reactor

from dotenv import load_dotenv

load_dotenv()


class MyItem(Item):
    url = Field()


class MySpider(CrawlSpider):
    name = "myspider"

    def __init__(self, *a, **kw):
        self.start_url = kw.pop("start_url", [])
        self.start_urls = [self.start_url]
        self.rules = (
            Rule(
                LinkExtractor(
                    allow=(self.start_url + r".*",),
                ),
                callback="parse_item",
                follow=True,
            ),
        )
        self.max_links = int(os.environ.get("CRAWLER_MAX_LINKS"))
        self.link_count = 0
        super().__init__(*a, **kw)
        reactor.callLater(int(os.environ.get("CRAWLER_MAX_EXECUTION_TIME")), self.stop)

    def parse_item(self, response):
        self.link_count += 1
        if self.link_count > self.max_links:
            self.crawler.engine.close_spider(self, "max_links")
        item = MyItem()
        item["url"] = response.url
        yield {"url": response.url}

    def stop(self):
        self.crawler.engine.close_spider(self, "timeout")


class MyPipeline(object):
    def open_spider(self, spider):
        self.urls = []

    def process_item(self, item, spider):
        self.urls.append(item["url"])
        return item


def run_spider(url, file_path, queue: Queue):
    settings = get_project_settings()
    settings.set("ITEM_PIPELINES", {"crawler.MyPipeline": 1})
    settings.set("USER_AGENT", "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)")
    settings.set("FEEDS", {file_path: {"format": "json"}})
    settings.set("DEPTH_LIMIT", "1")

    process = CrawlerProcess(settings)

    # spider = MySpider(start_url=url)
    crawler = process.create_crawler(MySpider)

    def spider_closed(spider, reason):
        # Now you can handle the reason here, e.g. store it, print it, etc.
        queue.put(reason)
        print(f"Spider closed with reason: {reason}")

    crawler.signals.connect(spider_closed, signals.spider_closed)

    # process.crawl(MySpider, start_url=url)
    process.crawl(crawler, start_url=url)
    process.start()


def crawl(url) -> str:
    queue = Queue()
    unique_id = uuid.uuid4()
    file_path = "./crawl_result/" + str(unique_id) + ".json"
    p = Process(target=run_spider, args=(url, file_path, queue))
    p.start()
    p.join()  # Wait for the process to finish

    if queue.empty():
        raise Exception("Crawler not finished")

    result = queue.get()
    if result == "max_links":
        message = "取得可能なURLの上限に達しました。"
    elif result == "timeout":
        message = "時間制限に達したため、クロールを中断しました。"
    elif result == "finished":
        message = "クロールが完了しました。"
    else:
        raise Exception("Unknown error. message: " + result)

    with open(file_path, "r") as f:
        data = json.load(f)
    urls = [item["url"] for item in data]

    return urls, message


if __name__ == "__main__":
    url = "https://gpt-index.readthedocs.io/en/latest/"
    urls = crawl(url)
