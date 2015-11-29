# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field
from scrapy import Item
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import MapCompose 
from scrapy.contrib.loader.processor import TakeFirst


def encode_utf8(value):
    if isinstance(value, unicode):
        return value.encode("utf-8")
    else:
        return value

class ConvertItemLoader(ItemLoader):

    default_input_processor = MapCompose(encode_utf8)
    default_output_processor = TakeFirst()

class CatelogItem(Item):
    name = Field()
    fd = Field()
    sd = Field()
    url = Field()

class PostListItem(Item):
    post_id = Field()
    author_name = Field()
    first_post_id = Field()
    reply_num = Field()
    is_bakan = Field(default=0)
    vid = Field(default=None)
    is_good = Field(default=0)
    is_top = Field(default=0)
    is_protal = Field(default=0)
    title = Field()
    timestamp = Field()
    subject = Field()

class PostItem(Item):
    user_id = Field()
    user_name = Field()
    name_u = Field()
    user_sex = Field()
    portrait = Field()
    is_like = Field()
    level_id = Field()
    level_name = Field()
    cur_score = Field()
    bawu = Field()
    post_id = Field()
    is_anonym = Field()
    open_id = Field()
    open_type = Field()
    date = Field()
    vote_crypt = Field()
    post_no = Field()
    content_type = Field()
    comment_num = Field()
    ptype = Field()
    is_saveface = Field()
    props = Field()
    post_index = Field()
    subject = Field()
