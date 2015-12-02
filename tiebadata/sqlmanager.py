#!/usr/bin/env python
# -*- coding:utf-8

import MySQLdb
import logging
from scrapy.utils.project import get_project_settings

settings = get_project_settings()
conn = MySQLdb.connect(host=settings.get('DB_HOST'), user=settings.get('DB_USER'), 
        passwd=settings.get('DB_PASSWD'), db=settings.get('DB_DATABASE'),  use_unicode=True, charset="utf8")

logger = logging.getLogger()

def ensure_str(string):
    if isinstance(string, unicode):
        return string.encode("utf-8")
    else:
        return string

def ensure_item(item):
    for key ,value in item.iteritems():
        item[key] = ensure_str(value)

class SqlManager(object):

    def __init__(self):
        cursor = conn.cursor()
        cursor.execute('create database if not exists %s' % settings.get('DB_DATABASE'))

        table_catalog_sql = '''create table if not exists catalog (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            fd VARCHAR(255),
            sd VARCHAR(255),
            url VARCHAR(255),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
        cursor.close()
        conn.commit()

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.sqlmanager = ext
        return ext

    def insert_catalog_item(self, item):
        cursor = conn.cursor()
        ensure_item(item)
        try:
            insert_sql = "replace into catalog (name, fd, sd, url) VALUES ('%s', '%s', '%s', '%s')" % (item["name"], item["fd"], item["sd"], item["url"])
            cursor.execute(insert_sql)
            conn.commit()
        except:
            logger.warning("----insert catalog item failed--------%s" % item)
            conn.rollback()
        finally:
            cursor.close()

    def insert_postinfo_item(self, item):
        cursor = conn.cursor()
        ensure_item(item)
        try:
            insert_sql = "replace into postinfo (id, author_name, first_post_id, reply_num, is_bakan,  \
                          vid, is_good, is_top, is_protal, title, timestamp, subject) VALUES \
                          (%d, '%s', %d, %d, %d,'%s', %d, %d, %d, '%s', '%s', '%s') " %  \
                          (item["post_id"], item["author_name"], item["first_post_id"], item["reply_num"],
                          item["is_bakan"], item["vid"], item["is_good"], item["is_top"], item["is_protal"], 
                          item["title"], item["timestamp"], item["subject"])
            cursor.execute(insert_sql)
            conn.commit()
        except:
            logger.warning("----insert postinfo item failed--------%s" % item)
            conn.rollback()
        finally:
            cursor.close()

    def get_subject_url(self, subject):
        cursor = conn.cursor()
        sql = "select url from catalog where name = '%s' " % ensure_str(subject)
        ret = None
        if cursor.execute(sql):
            ret = cursor.fetchone()[0]
        cursor.close()
        return ret

    def get_subject_fd_sd(self, subject):
        cursor = conn.cursor()
        s_sql = "select fd, sd from catalog where name = '%s'" % ensure_str(subject)
        ret = None
        if cursor.execute(s_sql):
            ret = cursor.fetchone()
        cursor.close()
        return ret
        
    def get_post_replynum(self, postid):
        cursor = conn.cursor()
        sql = "select reply_num from postinfo where id = %s" % postid
        ret = None
        if cursor.execute(sql):
            ret = cursor.fetchone()[0]
        cursor.close()
        return ret
