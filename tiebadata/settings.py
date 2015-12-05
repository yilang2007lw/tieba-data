# -*- coding: utf-8 -*-

# Scrapy settings for tiebadata project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
import logging

BOT_NAME = 'tiebadata'

SPIDER_MODULES = ['tiebadata.spiders']
NEWSPIDER_MODULE = 'tiebadata.spiders'

SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tiebadata (+http://www.yourdomain.com)'

DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware":None,
    "tiebadata.middleware.useragent.RandomUserAgentMiddleware":300,
}

ITEM_PIPELINES = {
        "tiebadata.pipelines.CatalogPipeline":600,
        "tiebadata.pipelines.PostListPipeline": 500,
        "tiebadata.pipelines.PostPipeline": 400,
}

EXTENSIONS = {
    "scrapy.telnet.TelnetConsole": None,
    "tiebadata.sqlmanager.SqlManager":500,
}

DB_USER="spider"
DB_HOST="localhost"
DB_PASSWD="tiebaspider"
DB_DATABASE="tiebadata"

DATA_HOME="/Volumes/MobileHD/"

LOG_LEVEL=logging.INFO
