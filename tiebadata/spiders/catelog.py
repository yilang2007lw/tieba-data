#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.http import Request
from tiebadata.items import CatelogItem
from tiebadata.items import ConvertItemLoader
import traceback

class CatelogSpider(Spider):
    name = "catelog"
    allowed_domains = ["tieba.baidu.com"]
    start_urls = (
        "http://tieba.baidu.com/f/fdir?fd=%D3%E9%C0%D6%C3%F7%D0%C7&sd=%C4%DA%B5%D8%C3%F7%D0%C7",
    )

    def __init__(self, fd = u"娱乐明星", sd = u"内地明星"):
        super(CatelogSpider, self).__init__()
        self.fd = fd
        self.sd = sd

    def parse(self, response):
        contents = response.css(".sub_dir_box").xpath("//table//td")
        nav = response.css("#album_list_page").css(".pagination")
        for a in contents:
            title = a.xpath("a/text()").extract()
            link = a.xpath("a/@href").extract()
            il = ConvertItemLoader(CatelogItem())
            il.add_value(u"name", title)
            il.add_value(u"fd", self.fd)
            il.add_value(u"sd", self.sd)
            il.add_value(u"url", link)
            il.load_item()
            yield il.item

        try:
            idx = nav.xpath("a/text()").extract().index(u'\u4e0b\u4e00\u9875')
            np = "http://tieba.baidu.com" + nav.xpath("a/@href").extract()[idx]
            yield Request(np, callback = self.parse)
        except:
            traceback.print_exc()
