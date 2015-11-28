# -*- coding: utf-8 -*-

# Scrapy settings for tiebadata project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'tiebadata'

SPIDER_MODULES = ['tiebadata.spiders']
NEWSPIDER_MODULE = 'tiebadata.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tiebadata (+http://www.yourdomain.com)'

DOWNLOADER_MIDDLEWARES = {
    "scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware":None,
    "tiebadata.middleware.useragent.RandomUserAgentMiddleware":300,
}

ITEM_PIPELINES = {
        "tiebadata.pipelines.CatelogPipeline":600,
}

EXTENSIONS = {
    "tiebadata.sqlmanager.SqlManager":500,
}

DB_USER="spider"
DB_HOST="localhost"
DB_PASSWD="tiebaspider"
DB_DATABASE="tiebadata"

DATA_HOME="/Volumes/MobileHD/"
