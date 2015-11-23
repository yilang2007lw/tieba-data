# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TiebadataItem(scrapy.Item):
    name = scrapy.Field()
    title = scrapy.Field()
    posttime = scrapy.Field()
    poster = scrapy.Field()
