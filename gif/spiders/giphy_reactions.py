import scrapy
import uuid
import requests
from gif.items import GifItem
from scrapy_selenium import SeleniumRequest


class GiphySpider(scrapy.Spider):
    handle_httpstatus_all = True
    name = "giphy"
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 300
    }

    def start_requests(self):
        url = 'https://giphy.com/categories/reactions'
        yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response):
        gif_item = GifItem()
        reactions = response.xpath('//a[contains(@class, "tag")] | //div[contains(@class, "grid_3 ")]/a')
        for reaction in reactions:
            href = reaction.xpath('@href').get()
            href = href.replace('/', '')
            href = href.replace('search', '')
            if href == 'categories':
                pass
            else:
                url = "https://api.giphy.com/v1/gifs/search?api_key=<>&limit=6&q=" + href
                payload = {}
                headers = {}
                resp = requests.request("GET", url, headers=headers, data=payload)
                resp = resp.json()
                for item in resp['data']:
                    gif_item['id'] = str(uuid.uuid1())
                    gif_item['site'] = "giphy"
                    gif_item['title'] = item['title']
                    gif_item['url'] = item['url']
                    gif_item['tags'] = None
                    gif_item['author'] = item['username']
                    gif_item['created'] = item['import_datetime']
                    gif_item['category'] = href
                    gif_item['duration'] = None
                    gif_item['dimensions'] = item['images']['original']['width'] + "x" + item['images']['original'][
                        'height']
                    gif_item['file_url'] = item['images']['original']['url']

                    yield gif_item








