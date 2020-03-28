import scrapy
import uuid
import itertools
from gif.items import GifItem


class TenorSpider(scrapy.Spider):
    handle_httpstatus_all = True
    name = "tenor"
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 300
    }

    def start_requests(self):
        url = 'https://tenor.com/reactions'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        categories = []
        reactions = response.xpath('//a[contains(@class, "SearchTag")]')
        for reaction in reactions:
            href = reaction.xpath('@href').get()
            href = "https://tenor.com" + href
            categories.append(href)
        yield from response.follow_all(categories, self.parse_gif_list)

    def parse_gif_list(self, response):
        gif_list = response.xpath('//figure[contains(@class, "GifListItem")]/a')
        category = response.xpath('//form/input/@value').get()

        # We limit into a 6 gifs per category
        for gif in itertools.islice(gif_list, 0, 6):
            href = gif.xpath('@href').get()
            href = "https://tenor.com" + href

            yield response.follow(url=href, callback=self.parse_gif_info, meta={'category': category})

    def parse_gif_info(self, response):

        gif_item = GifItem()
        container = response.xpath('//div[contains(@class, "main-container")]')

        duration = container.xpath('//dd[1]/text()').extract()
        if len(duration) > 2:
            duration = duration[2]
        else:
            duration = None

        dimensions = container.xpath('//dd[2]/text()').extract()
        if len(dimensions) > 4:
            dimensions = dimensions[2]+dimensions[3]+dimensions[4]
        else:
            dimensions = None

        gif_item['id'] = str(uuid.uuid1())
        gif_item['site'] = "tenor"
        gif_item['title'] = container.xpath('h1/text()').get()
        gif_item['url'] = container.xpath('//meta[@itemprop="url"]/@content').get()
        gif_item['tags'] = container.xpath('//meta[@itemprop="keywords"]/@content').get()
        gif_item['author'] = container.xpath('//meta[@itemprop="author"]/@content').get()
        gif_item['created'] = container.xpath('//meta[@itemprop="datePublished"]/@content').get()
        gif_item['category'] = response.meta.get('category')
        gif_item['duration'] = duration
        gif_item['dimensions'] = dimensions
        gif_item['file_url'] = container.xpath('//div[@itemprop="image"]/div/img/@src').get()

        yield gif_item
