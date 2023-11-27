import scrapy
from big_data_pro.settings import MAX_PAGE
from big_data_pro.items import BigDataProItem
from scrapy import Request


class SpaSpider(scrapy.Spider):
    name = 'spa'
    start_urls = [f'https://spa5.scrape.center/api/book/?limit=18&offset={i}' for i in range(0, 18 * MAX_PAGE, 18)]

    def parse(self, response, **kwargs):
        detail_url_list = ['https://spa5.scrape.center/api/book/' + item['id'] for item in response.json()['results']]
        for detail_url in detail_url_list:
            yield Request(url=detail_url, callback=self.parse_detail, meta={'source_url': response.url})

    @staticmethod
    def parse_detail(response):
        response_dict = response.json()
        book_info = dict()
        book_info['name'] = response_dict['name']
        book_info['score'] = response_dict['score']
        book_info['tags'] = response_dict['tags']
        try:
            author_str = response_dict['authors'][0].strip()
            book_info['author'] = author_str if '\n' not in author_str else ''.join(author_str.split('\n            '))
        except IndexError:
            book_info['author'] = '佚名'
        comments_str = ''
        for item in response_dict['comments']:
            try:
                comments_str += item['content'] + '\n'
            except TypeError:
                continue
        book_info['comments'] = comments_str

        item = BigDataProItem()
        item['book_info'] = book_info
        yield item
