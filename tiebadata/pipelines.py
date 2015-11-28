# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from tiebadata.items import CatelogItem

class CatelogPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, CatelogItem):
            if item.has_key("name") and item.has_key("url"):
                mgr = spider.crawler.sqlmanager
                mgr.insert_catelog_item(item)
