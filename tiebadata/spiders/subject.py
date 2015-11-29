#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.http import Request
from tiebadata.items import PostItem
from tiebadata.items import PostListItem
import traceback
import json


class SubjectSpider(Spider):
    name = "subject"
    allowed_domains = ["tieba.baidu.com"]

    def __init__(self, subject):
        super(SubjectSpider, self).__init__()
        self.subject = subject
        self.active_post = None
        self.refresh_postlist = True

    def start_requests(self):
        url = self.crawler.sqlmanager.get_subject_url(unicode(self.subject, "utf-8"))
        if url:
            yield Request(url, self.parse)

    def parse_post(self, response):
        contents = response.css("#j_p_postlist").xpath("div[contains(@class, 'j_l_post')]")
        nav = response.css(".l_pager")
        if nav and u'\u4e0b\u4e00\u9875' in nav.xpath("a/text()").extract():
            idx = nav.xpath("a/text()").extract().index(u'\u4e0b\u4e00\u9875')
            np = "http://tieba.baidu.com" + nav.xpath("a/@href").extract()[idx]
            request = Request(np, callback = self.parse_post)
            request.meta['pitem'] = response.meta['pitem']
            yield request
        else:
            try:
                last_data = contents[-1].xpath("@data-field").extract()[-1]
                plistitem = response.meta['pitem']
                plistitem[u"timestamp"] = json.loads(last_data)["content"]["date"].encode("utf-8")
                yield plistitem
            except:
                traceback.print_exc()

        for div in contents:
            data = div.xpath("@data-field").extract()
            item = PostItem()
            try:
                tmp_dict = json.loads(data[0])
                for ko, vo in tmp_dict.iteritems():
                    for ki, vi in vo.iteritems():
                        if ki in item.fields.keys():
                            item[ki] = vi
            except:
                traceback.print_exc()
            else:
                self.active_post = str(response.url.split("/")[-1])
                item["subject"] = response.meta['pitem']["subject"].decode("utf-8")
                yield item

    def parse(self, response):
        contents = response.css("#thread_list").xpath('//li[contains(@data-field, "id")]')
        for li in contents:
            data = li.xpath("@data-field").extract()
            try:
                data_dict = json.loads(data[0])
                data_dict[u"post_id"] = data_dict.pop("id")
                pid = data_dict["post_id"] 
                replynum = data_dict["reply_num"]
                is_top = data_dict["is_top"]

                sql_replynum = self.crawler.sqlmanager.get_post_replynum(pid)
                if sql_replynum is None or replynum > sql_replynum:
                    text = li.css(".threadlist_text").xpath("a/@title").extract()
                    data_dict[u"title"] = text[0]
                    data_dict[u"subject"] = self.subject
                    page = 1 if sql_replynum is None else sql_replynum / 30 + 1
                    post_url = "http://tieba.baidu.com/p/%d?pn=%d" % (pid, page)

                    item = PostListItem()
                    for key in item.fields.keys():
                        if data_dict.has_key(key):
                            if isinstance(data_dict[key], unicode):
                                item[key] = data_dict[key].encode("utf-8")
                            else:
                                item[key] = data_dict[key]
                    request = Request(post_url, self.parse_post)
                    request.meta['pitem'] = item
                    yield request
                elif not is_top:
                    self.refresh_postlist = False
                    break
            except:
                print "-----------parse except------------"
                self.refresh_postlist = False
                traceback.print_exc()

        if self.refresh_postlist:
            nav = response.css(".pager").xpath("a[contains(text(), '>')]")
            if nav:
                np = "http://tieba.baidu.com" + nav.xpath("@href").extract()[0]
                yield Request(np, self.parse)
