#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from tiebadata.items import CatalogItem
from tiebadata.items import PostListItem
from tiebadata.items import PostItem
from scrapy.exceptions import DropItem
import os
import json
import codecs

class CatalogPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, CatalogItem):
            keys = item.keys()
            if "name" in keys and "url" in keys:
                mgr = spider.crawler.sqlmanager
                mgr.insert_catalog_item(item)
            else:
                raise DropItem("Invalid CatalogItem")
        return item

class PostListPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, PostListItem):
            keys = item.keys()
            if "post_id" in keys and "author_name" in keys:
                mgr = spider.crawler.sqlmanager
                mgr.insert_postinfo_item(item)
            else:
                raise DropItem("Invalid PostListItem")
        return item

class PostPipeline(object):

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
                raise DropItem("Invalid PostItem")
            post_dir = os.path.join(spider.settings["DATA_HOME"], "tiebadata", fd.encode("utf-8"), sd.encode("utf-8"), item["subject"].encode("utf-8"), pid)
            if not os.path.exists(post_dir):
                os.makedirs(post_dir)

            post_file = os.path.join(post_dir, page)

            with codecs.open(post_file, "a", "utf-8") as f:
                f.write(json.dumps(dict(item), ensure_ascii=False))
                f.write("\n")
        return item
