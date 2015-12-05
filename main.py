#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor
from twisted.internet import defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from tiebadata.spiders.catalog import CatalogSpider
from tiebadata.spiders.subject import SubjectSpider
from tiebadata.sqlmanager import setup_db
from tiebadata.sqlmanager import get_all_subject
from tiebadata.sqlmanager import get_subject_by_fd
from tiebadata.sqlmanager import get_subject_by_sd
import argparse
import traceback
import logging
import os
import time

settings = get_project_settings()

def crawl_catalog_table():
    print "------crawl catalog table---------"
    return crawl_spiders([CatalogSpider()])

def crawl_all_catalog():
    print "-------crawl all catalog-----------"
    try:
        spiders = map(lambda x: SubjectSpider(x[0]), get_all_subject())
        return crawl_spiders(spiders)
    except:
        traceback.print_exc()

def crawl_fd_catalog(fd):
    print "------crawl fd catalog---------", fd
    try:
        spiders = map(lambda x: SubjectSpider(x[0]), get_subject_by_fd(fd))
        return crawl_spiders(spiders)
    except:
        traceback.print_exc()

def crawl_sd_catalog(sd):
    print "------crawl sd catalog---------", sd
    try:
        spiders = map(lambda x: SubjectSpider(x[0]), get_subject_by_sd(sd))
        return crawl_spiders(spiders)
    except:
        traceback.print_exc()

def crawl_one_subject(subject):
    print "------crawl one subject---------", subject
    crawl_spiders([SubjectSpider(subject)])

@defer.inlineCallbacks
def crawl_spiders(spiders):
    for spider in spiders:
        if isinstance(spider, SubjectSpider):
            yield runner.crawl(spider, spider.subject)
        else:
            yield runner.crawl(spider)
    reactor.stop()

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

    path = os.path.join(os.path.dirname(__file__), "log", time.strftime('%Y%m%d_%H%M%S'))
    logging.basicConfig(filename=path, level=logging.WARNING)
    configure_logging()

    runner = CrawlerRunner(settings)
    setup_db()

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
