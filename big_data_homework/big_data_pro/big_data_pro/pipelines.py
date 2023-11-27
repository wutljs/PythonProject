# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import time
from itemadapter import ItemAdapter
from redis import StrictRedis


# noinspection PyAttributeOutsideInit
class BigDataProPipeline:

    @classmethod
    def from_crawler(cls, crawler):
        cls.host = crawler.settings.get('REDIS_HOST')
        cls.port = crawler.settings.get('REDIS_PORT')
        cls.db = crawler.settings.get('REDIS_DB')
        return cls()

    def open_spider(self, spider):
        self.redis = StrictRedis(host=self.host, port=self.port, db=self.db)
        self.start_time = time.time()

    def process_item(self, item, spider):
        book_info = item['book_info']
        key = book_info['name']
        value = json.dumps({key: (book_info['score'], book_info['author'], book_info['tags'], book_info['comments'])})
        self.redis.set(key, value)
        print(key, '已写入数据库!')
        return item

    def close_spider(self, spider):
        self.redis.close()
        print('spider工作完毕,共耗时', time.time() - self.start_time, '秒!')
