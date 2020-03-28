# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GifItem(scrapy.Item):
    id = scrapy.Field()
    site = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    tags = scrapy.Field()
    author = scrapy.Field()
    created = scrapy.Field()
    category = scrapy.Field()
    duration = scrapy.Field()
    dimensions = scrapy.Field()
    file_url = scrapy.Field()
