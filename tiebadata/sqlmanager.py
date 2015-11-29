#!/usr/bin/env python
# -*- coding:utf-8

import MySQLdb

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.conf import settings

class SqlManager(object):

    def __init__(self):
        self.conn = None

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

    def initialize(self, spider):
        self.conn = MySQLdb.connect(host=settings.get('DB_HOST'), user=settings.get('DB_USER'), 
                passwd=settings.get('DB_PASSWD'), use_unicode=True, charset="utf8")
        cursor = self.conn.cursor()
        cursor.execute('create database if not exists %s' % settings.get('DB_DATABASE'))
        self.conn.select_db(settings.get('DB_DATABASE'))

        table_catalog_sql = '''create table if not exists catalog (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            fd VARCHAR(255),
            sd VARCHAR(255),
            url VARCHAR(255),
            UNIQUE (name)
        ) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;'''
        cursor.execute(table_catalog_sql)

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
        cursor.execute(table_postinfo_sql)
        self.conn.commit()
        cursor.close()

    def finalize(self, spider, reason):
        self.conn.commit()
        self.conn.close()

    def insert_catalog_item(self, item):
        cursor = self.conn.cursor()
        try:
            insert_sql = "replace into catalog (name, fd, sd, url) VALUES ('%s', '%s', '%s', '%s')" % (item["name"], item["fd"], item["sd"], item["url"])
            cursor.execute(insert_sql)
            self.conn.commit()
        except:
            print "----insert catalog item failed--------", item
            self.conn.rollback()
        finally:
            cursor.close()

    def insert_postinfo_item(self, item):
        cursor = self.conn.cursor()
        try:
            insert_sql = "replace into postinfo (id, author_name, first_post_id, reply_num, is_bakan,  \
                          vid, is_good, is_top, is_protal, title, timestamp, subject) VALUES \
                          (%d, '%s', %d, %d, %d,'%s', %d, %d, %d, '%s', '%s', '%s') " %  \
                          (item["post_id"], item["author_name"], item["first_post_id"], item["reply_num"],
                          item["is_bakan"], item["vid"], item["is_good"], item["is_top"], item["is_protal"], 
                          item["title"], item["timestamp"], item["subject"])
            cursor.execute(insert_sql)
            self.conn.commit()
        except:
            print "----insert postinfo item failed--------", item
            self.conn.rollback()
        finally:
            cursor.close()

    def get_subject_url(self, subject):
        cursor = self.conn.cursor()
        sql = "select url from catalog where name = '%s' " % subject.encode("utf-8")
        ret = None
        if cursor.execute(sql):
            ret = cursor.fetchone()[0]
        cursor.close()
        return ret

    def get_subject_fd_sd(self, subject):
        cursor = self.conn.cursor()
        s_sql = "select fd, sd from catalog where name = '%s'" % subject.encode("utf-8")
        ret = None
        if cursor.execute(s_sql):
            ret = cursor.fetchone()
        cursor.close()
        return ret
        
    def get_post_replynum(self, postid):
        cursor = self.conn.cursor()
        sql = "select reply_num from postinfo where id = %s" % postid
        ret = None
        if cursor.execute(sql):
            ret = cursor.fetchone()[0]
        cursor.close()
        return ret
