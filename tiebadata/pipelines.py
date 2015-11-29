#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from tiebadata.items import CatelogItem
from tiebadata.items import PostListItem
from tiebadata.items import PostItem
from scrapy.conf import settings
from scrapy.exceptions import DropItem
import os
import json

class CatelogPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, CatelogItem):
            if item.has_key("name") and item.has_key("url"):
                mgr = spider.crawler.sqlmanager
                mgr.insert_catelog_item(item)
            else:
                raise DropItem("Invalid CatelogItem:%s" % item)
        return item

class PostListPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, PostListItem):
            if item.has_key("post_id") and item.has_key("author_name"):
                mgr = spider.crawler.sqlmanager
                mgr.insert_postinfo_item(item)
            else:
                raise DropItem("Invalid PostListItem:%s" % item)
        return item

class PostPipeline(object):

    def open_spider(self, spider):
        spider.files = {}

    def close_spider(self, spider):
        for f in spider.files.itervalues():
            f.close()

    def process_item(self, item, spider):
        if isinstance(item, PostItem):
            pid = spider.active_post.split("?")[0]
            if spider.active_post.count("?") > 0:
                page = str(spider.active_post.split("?")[-1].split("=")[-1])
            else:
                page = "1"

            mgr = spider.crawler.sqlmanager
            ret = mgr.get_subject_fd_sd(item["subject"])
            if ret:
                (fd, sd) = ret
            else:
                raise DropItem("Invalid PostItem:%s" % item)
            post_dir = os.path.join(settings["DATA_HOME"], "tiebadata", fd.encode("utf-8"), sd.encode("utf-8"), item["subject"].encode("utf-8"), pid)
            if not os.path.exists(post_dir):
                os.makedirs(post_dir)
            post_file = os.path.join(post_dir, page)

            if not os.path.exists(post_file):
                open(post_file, "w+").close()

            if not spider.files.has_key(spider.active_post):
                spider.files[spider.active_post] = open(post_file, "w")
            line = json.dumps(dict(item)) 
            spider.files[spider.active_post].writelines(line + "\n")
        return item
