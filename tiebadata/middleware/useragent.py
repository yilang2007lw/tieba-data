#!/usr/bin/env python

import random
import os
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

class RandomUserAgentMiddleware(UserAgentMiddleware):

    def __init__(self, settings, user_agent = "Scrapy"):
        super(RandomUserAgentMiddleware, self).__init__()
        self.user_agent = user_agent
        agentfile = os.path.join(os.path.dirname(__file__), "useragent.list")
        with open(agentfile, 'r') as f:
            self.user_agent_list = [line.strip() for line in f.readlines()]

    @classmethod
    def from_crawler(cls, crawler):
        obj = cls(crawler.settings)
        crawler.signals.connect(obj.spider_opened, signal=signals.spider_opened)
        return obj

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agent_list)
        if user_agent:
            request.headers.setdefault("User-Agent", user_agent)
