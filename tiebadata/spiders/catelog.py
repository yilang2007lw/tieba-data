#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.http import Request
from tiebadata.items import CatelogItem
from tiebadata.items import ConvertItemLoader
import urllib
import urlparse
import traceback

class CatelogSpider(Spider):
    name = "catelog"
    allowed_domains = ["tieba.baidu.com"]
    start_urls = (
        #"http://tieba.baidu.com/f/fdir?fd=%D3%E9%C0%D6%C3%F7%D0%C7&sd=%C4%DA%B5%D8%C3%F7%D0%C7",
        "http://tieba.baidu.com/f/index/forumclass",
    )

    def parse_detail(self, response):
        try:
            query = urlparse.urlparse(response.url).query
            params = urlparse.parse_qs(query)
            fd = params["fd"][0].decode("gbk")
            sd = params["sd"][0].decode("gbk")
        except:
            fd = None
            sd = None
            traceback.print_exc()

        contents = response.css(".sub_dir_box").xpath("//table//td")
        nav = response.css("#album_list_page").css(".pagination")
        for a in contents:
            title = a.xpath("a/text()").extract()
            link = a.xpath("a/@href").extract()
            il = ConvertItemLoader(CatelogItem())
            il.add_value(u"name", title)
            il.add_value(u"fd", fd)
            il.add_value(u"sd", sd)
            il.add_value(u"url", link)
            il.load_item()
            yield il.item

        try:
            idx = nav.xpath("a/text()").extract().index(u'\u4e0b\u4e00\u9875')
            np = "http://tieba.baidu.com" + nav.xpath("a/@href").extract()[idx]
            yield Request(np, callback = self.parse)
        except:
            traceback.print_exc()

    def parse(self, response):
        contents = response.css("#right-sec").css(".class-item")
        for c in contents:
            fd = c.xpath("a/text()").extract()[0]
            for sd in c.css(".item-list-ul").xpath("li/a/text()").extract():
                url = "http://tieba.baidu.com/f/fdir?fd=%s&sd=%s" % (urllib.quote(fd.encode("gbk")), urllib.quote(sd.encode("gbk")))
                yield Request(url, self.parse_detail)
