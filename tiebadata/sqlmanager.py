#!/usr/bin/env python
# -*- coding:utf-8

import MySQLdb

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.conf import settings
import traceback

class SqlManager(object):

    def __init__(self):
        self.conn = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        if settings.get('DB_USER') is None:
            raise NotConfigured
        if settings.get('DB_PASSWD') is None:
            raise NotConfigured
        if settings.get('DB_HOST') is None:
            raise NotConfigured
        if settings.get('DB_DATABASE') is None:
            raise NotConfigured

        ext = cls()
        crawler.signals.connect(ext.initialize, signal = signals.spider_opened)
        crawler.signals.connect(ext.finalize, signal = signals.spider_closed)
        crawler.sqlmanager = ext

        return ext

    def initialize(self):
        self.conn = MySQLdb.connect(host=settings.get('DB_HOST'), user=settings.get('DB_USER'), 
                passwd=settings.get('DB_PASSWD'), use_unicode=True, charset="utf8")
        self.cursor = self.conn.cursor()
        self.cursor.execute('create database if not exists %s' % settings.get('DB_DATABASE'))
        self.conn.select_db(settings.get('DB_DATABASE'))

        table_catelog_sql = '''create table if not exists catelog (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            fd VARCHAR(255),
            sd VARCHAR(255),
            url VARCHAR(255),
            UNIQUE (name)
        ) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;'''
        self.cursor.execute(table_catelog_sql)

        table_postinfo_sql = '''create table if not exists postinfo (
            id BIGINT PRIMARY KEY,
            author_name VARCHAR(255) NOT NULL, 
            first_post_id BIGINT, 
            reply_num INT, 
            is_bakan BOOLEAN, 
            vid VARCHAR(255), 
            is_good BOOLEAN, 
            is_top BOOLEAN, 
            is_protal BOOLEAN, 
            title VARCHAR(1024),
            timestamp DATETIME, 
            subject VARCHAR(255),
            INDEX subindex (subject)
        )  ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;'''
        self.cursor.execute(table_postinfo_sql)
        self.conn.commit()

    def finalize(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def insert_catelog_item(self, item):
        try:
            insert_sql = "replace into catelog (name, fd, sd, url) VALUES ('%s', '%s', '%s', '%s')" % (item["name"], item["fd"], item["sd"], item["url"])
            self.cursor.execute(insert_sql)
            self.conn.commit()
        except:
            print "----insert catelog item failed--------", item
            traceback.print_exc()

    def insert_postinfo_item(self, item):
        try:
            insert_sql = "replace into postinfo (id, author_name, first_post_id, reply_num, is_bakan,  \
                          vid, is_good, is_top, is_protal, title, timestamp, subject) VALUES \
                          (%d, '%s', %d, %d, %d,'%s', %d, %d, %d, '%s', '%s', '%s') " %  \
                          (item["post_id"], item["author_name"], item["first_post_id"], item["reply_num"],
                          item["is_bakan"], item["vid"], item["is_good"], item["is_top"], item["is_protal"], 
                          item["title"], item["timestamp"], item["subject"])
            self.cursor.execute(insert_sql)
            self.conn.commit()
        except:
            print "----inset postinfo item failed--------", item
            traceback.print_exc()

    def get_subject_url(self, subject):
        sql = "select url from catelog where name = '%s' " % subject
        if self.cursor.execute(sql):
            return self.cursor.fetchone()[0]
        else:
            return None

    def get_post_fd_sd(self, postid):
        p_sql = "select subject from postinfo where id = %s" % postid
        if self.cursor.execute(p_sql):
            subject = self.cursor.fetchone()[0]
            s_sql = "select fd, sd from catelog where name = '%s'" % subject
            if self.cursor.execute(s_sql):
                return self.cursor.fetchone()
        return None

    def get_post_replynum(self, postid):
        sql = "select reply_num from postinfo where id = %s" % postid
        if self.cursor.execute(sql):
            return self.cursor.fetchone()[0]
        return None
