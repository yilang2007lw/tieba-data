#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor
from scrapy.crawler import Crawler
#from scrapy import signals
from scrapy import log
from scrapy.conf import settings
#from tiebadata.spiders.catalog import CatalogSpider
from tiebadata.spiders.subject import SubjectSpider
import argparse
import MySQLdb
import traceback


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

def crawl_spiders(spiders):
    for spider in spiders:
        crawler = Crawler(settings)
        #crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
        crawler.configure()
        crawler.crawl(spider)
        crawler.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--all", action="store_true", help="crawl full tieba")
    group.add_argument("-o", "--one", action="store_true", help="crawl this tieba")
    parser.add_argument("-f", "--fd", action="store_true", help="crawl tieba in the fd")
    parser.add_argument("-s", "--sd", action="store_true", help="crawl tieba in the sd")
    parser.add_argument("target", type=lambda s: unicode(s, "utf-8"), help="crawl target for one/fd/sd")
    args = parser.parse_args()

    if args.all:
        crawl_all_catalog()
    elif args.one:
        crawl_one_subject(args.target)
    elif args.fd:
        crawl_fd_catalog(args.target)
    elif args.sd:
        crawl_sd_catalog(args.target)
    else:
        print "------invalid---------"
    log.start()
    reactor.run()
