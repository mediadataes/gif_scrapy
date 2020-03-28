import scrapy
import uuid
import itertools
from gif.items import GifItem


class GfycatSpider(scrapy.Spider):
    handle_httpstatus_all = True
    name = "gfycat"

    def start_requests(self):
        url = 'https://gfycat.com/featured/reactions'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        categories = []
        reactions = response.xpath('//a[contains(@class, "tag-card-container")] '
                                   '|'
                                   '//div[contains(@class, "links-list__item")]/a')
        for reaction in reactions:
            href = reaction.xpath('@href').get()
            href = "https://gfycat.com" + href
            categories.append(href)
        yield from response.follow_all(categories, self.parse_gif_list)

    def parse_gif_list(self, response):
        gif_list = response.xpath('//div[contains(@class, "grid-gfy-item")]/a')
        category = response.xpath('//span[contains(@class, "search-text")]/text()').get()

        # We limit into a 6 gifs per category
        for gif in itertools.islice(gif_list, 0, 8):
            href = gif.xpath('@href').get()
            href = "https://gfycat.com" + href

            yield response.follow(url=href, callback=self.parse_gif_info, meta={'category': category})

    def parse_gif_info(self, response):

        gif_item = GifItem()
        container = response.xpath('//div[contains(@class, "gif-info")]')

        duration = container.xpath('//meta[@property="og:video:duration"]/@content').get()

        dim_with = container.xpath('//meta[@property="og:image:width"]/@content').get()
        dim_height = container.xpath('//meta[@property="og:image:height"]/@content').get()
        dimensions = dim_with+"x"+dim_height

        gif_item['id'] = str(uuid.uuid1())
        gif_item['site'] = "gfycat"
        gif_item['title'] = container.xpath('h1/text()').get()
        gif_item['url'] = response.request.url
        tags = container.xpath('//div[contains(@class, "tag-list")]/a/text()').getall()
        k = ','
        tags = k.join(tags)
        gif_item['tags'] = tags
        author = container.xpath('//span[contains(@class, "userid")]/text()').extract()
        if len(author) > 0:
            s = ''
            author = s.join(author)
        else:
            author = None
        gif_item['author'] = author
        created = container.xpath('//div[contains(@class, "gif-created")]/text()').extract()
        created = created[1]
        gif_item['created'] = created
        gif_item['category'] = response.meta.get('category')
        gif_item['duration'] = duration
        gif_item['dimensions'] = dimensions
        gif_item['file_url'] = container.xpath('//meta[@property="og:image:secure_url"]/@content').get()

        yield gif_item
