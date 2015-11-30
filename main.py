#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import signals
from scrapy.log import ScrapyFileLogObserver
from scrapy.conf import settings
from tiebadata.spiders.catalog import CatalogSpider
from tiebadata.spiders.subject import SubjectSpider
import argparse
import MySQLdb
import traceback
import logging
import os
import time
import copy

remain_spiders = []

def crawl_catalog_table():
    print "------crawl catalog table---------"
    return crawl_spiders([CatalogSpider()])

def crawl_all_catalog():
    print "-------crawl all catalog-----------"

def crawl_fd_catalog(fd):
    print "------crawl fd catalog---------", fd
    try:
        conn = MySQLdb.connect(host=settings.get('DB_HOST'), user=settings.get('DB_USER'), 
                passwd=settings.get('DB_PASSWD'), use_unicode=True, charset="utf8")
        cursor = conn.cursor()
        conn.select_db(settings.get('DB_DATABASE'))
        sql = "select name from catalog where fd = '%'" % fd.encode("utf-8")
        cursor.execute(sql)
        spiders = map(lambda x: SubjectSpider(x[0]), cursor.fetchall())
        cursor.close()
        conn.close()
        return crawl_spiders(spiders)
    except:
        traceback.print_exc()

def crawl_sd_catalog(sd):
    print "------crawl sd catalog---------", sd
    try:
        conn = MySQLdb.connect(host=settings.get('DB_HOST'), user=settings.get('DB_USER'), 
                passwd=settings.get('DB_PASSWD'), use_unicode=True, charset="utf8")
        cursor = conn.cursor()
        conn.select_db(settings.get('DB_DATABASE'))
        sql = "select name from catalog where sd = '%'" % sd.encode("utf-8")
        cursor.execute(sql)
        spiders = map(lambda x: SubjectSpider(x[0]), cursor.fetchall())
        cursor.close()
        conn.close()
        return crawl_spiders(spiders)
    except:
        traceback.print_exc()

def crawl_one_subject(subject):
    print "------crawl one subject---------", subject
    return crawl_spiders([SubjectSpider(subject)])

def spider_closed_cb(spider):
    global remain_spiders
    remain_spiders.remove(spider)
    print "-------spider closed---------", spider, len(remain_spiders)
    if not remain_spiders:
        reactor.stop()
    
def crawl_spiders(spiders):
    global remain_spiders
    remain_spiders = copy.copy(spiders)
    for spider in spiders:
        crawler = Crawler(settings)
        crawler.signals.connect(spider_closed_cb, signal=signals.spider_closed)
        crawler.configure()
        crawler.crawl(spider)
        crawler.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--catalog", action="store_true", help="crawl catalog table")
    group.add_argument("-a", "--all", action="store_true", help="crawl full tieba")
    group.add_argument("-o", "--one", action="store_true", help="crawl this tieba")
    group.add_argument("-f", "--fd", action="store_true", help="crawl tieba in the fd")
    group.add_argument("-s", "--sd", action="store_true", help="crawl tieba in the sd")
    parser.add_argument("-t", "--target", type=str, help="crawl target for one/fd/sd")
    args = parser.parse_args()

    path = os.path.join(os.path.dirname(__file__), "log", time.strftime('%Y-%m-%d_%H:%M:%s'))
    logfile = open(path, "w")
    log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
    log_observer.start()

    if args.catalog:
        crawl_catalog_table()
    elif args.all:
        crawl_all_catalog()
    elif args.one:
        crawl_one_subject(args.target)
    elif args.fd:
        crawl_fd_catalog(args.target)
    elif args.sd:
        crawl_sd_catalog(args.target)
    else:
        print "------invalid---------"
    reactor.run()
