#!/usr/bin/python27
import psycopg2
import logging

from crawler.config import config

log = logging.getLogger(__name__)
def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        log.info('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)


        # create a cursor
        cur = conn.cursor()

        # execute a statement
        log.info('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        log.info(db_version)

        # close the communication with the PostgreSQL
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        log.error(error)
    #finally:
    #    if conn is not None:
    #        conn.close()
    #        print('Database connection closed.')

def insert_source(conn, url, domain, brand, description, logo_url, language):
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO news_source(url, domain, brand, description, logo_url, language)
             VALUES(%s, %s, %s, %s, %s, %s) RETURNING id;"""
    try:
        # create a cursor
        cur = conn.cursor()

        try:
            #execute insert
            cur.execute(sql, (url, domain, brand, description, logo_url, language))

        except psycopg2.IntegrityError:
            conn.rollback()
        else:
            conn.commit()
        cur.close()
    except Exception as error:
        #log.critical("ERRRRR %s", error)
        pass

def get_news_source_count(conn):
    sql = """SELECT count(*) FROM news_source"""
    try:
        # create a cursor
        cur = conn.cursor()

        #execute query
        cur.execute(sql)

        #fetch all data
        rows = cur.fetchone()

        cur.close()
        return rows[0];
    except (Exception, psycopg2.DatabaseError) as error:
        log.critical(error)


def get_news_sources(conn, offset, limit):
    sql = """SELECT * FROM news_source LIMIT %s OFFSET %s;"""
    try:
        # create a cursor
        cur = conn.cursor()

        #execute query
        cur.execute(sql, (limit, offset))

        #fetch all data
        rows = cur.fetchall()

        cur.close()
        return rows;
    except (Exception, psycopg2.DatabaseError) as error:
        log.critical(error)

def get_news_source(conn, url):
    sql = """SELECT * FROM news_source WHERE url=%(url)s"""

    try:
        # create a cursor
        cur = conn.cursor()

        #execute query
        cur.execute(sql, ({'url': url }))

        #fetch all data
        row = cur.fetchone()

        cur.close()
        return row
    except (Exception, psycopg2.DatabaseError) as error:
        log.critical(error)

def insert_news_article(conn, article, news_source_id):
    import time
    import datetime

    log.info("Inserting document [%s] into the database.", article.url)

    sql = """INSERT INTO news_article(title, url, image_url, text, language, crawl_date, publish_date, news_source_id, authors)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);"""

    try:
        # create a cursor
        cur = conn.cursor()

        try:
            #execute insert
            cur.execute(sql, (article.title, article.url, article.top_image, article.text, article.language, datetime.datetime.fromtimestamp(time.time()), article.publish_date, news_source_id, article.authors))

        except psycopg2.IntegrityError as error:
            log.warn("Error: %s", error)
            conn.rollback()
        else:
            conn.commit()

        cur.close()
    except Exception as error:
        log.critical(error)
        pass

def insert_news_articles(conn, articles, news_source_id):
    import time
    import datetime

    log.info("Inserting %s articles into the database from source %s.", len(articles), news_source_id)

    if articles and news_source_id:
        try:
            # create a cursor
            cur = conn.cursor()

            dataText = ','.join(cur.mogrify('(%s, %s, %s, %s, %s, %s, %s, %s, %s)', (article.title, article.url, article.top_image, article.text, article.language, datetime.datetime.fromtimestamp(time.time()), article.publish_date, article.authors, news_source_id)).decode('utf-8') for article in articles)

            #execute insert
            cur.execute("INSERT INTO news_article(title, url, image_url, text, language, crawl_date, publish_date, authors, news_source_id) VALUES " +dataText)

            conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            log.critical(error)
            pass

def articles_exist(conn, articles):
    sql = """SELECT url from news_article WHERE url IN %(articles)s"""
    if articles:
        try:
            cur = conn.cursor()

            cur.execute(sql, {
                'articles': tuple(articles), # Converts the list to a tuple.
            })

            rows = cur.fetchall()

            cur.close()
            if rows:
                return [i[0] for i in rows]
            else:
                return None
        except (Exception, psycopg2.DatabaseError) as error:
            log.critical(error)
            pass
    else:
        return None

def articles_exist2(conn, news_source_id):
    sql = """SELECT url from news_article WHERE news_source_id = %(news_source_id)s"""
    if news_source_id:
        try:
            cur = conn.cursor()

            cur.execute(sql, {
                'news_source_id': news_source_id,
            })

            rows = cur.fetchall()

            cur.close()
            if rows:
                return [i[0] for i in rows]
            else:
                return ['']
        except (Exception, psycopg2.DatabaseError) as error:
            log.critical(error)
            pass
    else:
        return ['']

def articles_for_news_source(conn, news_source_id):
    sql = """SELECT title, publish_date from news_article WHERE news_source_id=%(news_source_id)s"""
    if news_source_id:
        try:
            cur = conn.cursor()

            cur.execute(sql, {
                'news_source_id': news_source_id,
            })

            rows = cur.fetchall()

            cur.close()
            return rows
        except (Exception, psycopg2.DatabaseError) as error:
            log.critical(error)
            pass
    else:
        return ['']

def articles_exist3(conn, news_source_id, title, publish_date):
    log.info("Check if article with title '%s', and publish_date: '%s' for news source id '%s' already exists.", title, publish_date, news_source_id)
    sql = """SELECT title, publish_date from news_article WHERE news_source_id=%(news_source_id)s AND title=%(title)s AND publish_date=%(publish_date)s"""

    try:
        cur = conn.cursor()

        cur.execute(sql, {
            'news_source_id':news_source_id,
            'title': title,
            'publish_date': publish_date,
        })

        rows = cur.fetchall()

        cur.close()
        if rows:
            return True
        else:
            return False
    except (Exception, psycopg2.DatabaseError) as error:
        log.critical(error)
        pass

def get_articles_with_null_date(conn, language, news_source_id):
    sql = """SELECT id, url from news_article WHERE publish_date is null and language=%(language)s and news_source_id=%(news_source_id)s"""
    try:
        cur = conn.cursor()

        #execute query
        cur.execute(sql, ({'language': language, 'news_source_id': news_source_id}))

        #fetch all data
        rows = cur.fetchall()

        cur.close()
        return rows
    except (Exception, psycopg2.DatabaseError) as error:
        log.critical(error)
        pass

def get_articles_for_date(conn, from_date, to_date, offset, limit):
    sql = """SELECT id, url, language, news_source_id FROM news_article WHERE crawl_date >=%(from_date)s and crawl_date < %(to_date)s order by id asc OFFSET %(offset)s LIMIT %(limit)s"""
    try:
        cur = conn.cursor()

        #execute query
        cur.execute(sql, ({'from_date': from_date,
                           'to_date': to_date,
                           'offset': offset,
                           'limit': limit,
                           }))

        #fetch all data
        rows = cur.fetchall()

        cur.close()
        return rows
    except (Exception, psycopg2.DatabaseError) as error:
        log.critical(error)
        pass


def get_articles_by_url(conn, url):
    sql = """SELECT id, news_source_id, language FROM news_article WHERE url=%(url)s"""
    try:
        cur = conn.cursor()

        #execute query
        cur.execute(sql, ({'url': url}))

        #fetch all data
        rows = cur.fetchone()

        cur.close()
        return rows
    except (Exception, psycopg2.DatabaseError) as error:
        log.critical(error)
        pass


def get_news_articles_count_for_date(conn, from_date, to_date):
    sql = """SELECT count(*) FROM news_article WHERE crawl_date >=%(from_date)s and crawl_date < %(to_date)s"""
    try:
        # create a cursor
        cur = conn.cursor()

        #execute query
        cur.execute(sql, ({'from_date': from_date,
                           'to_date': to_date
                           }))

        #fetch all data
        rows = cur.fetchone()

        cur.close()
        return rows[0];
    except (Exception, psycopg2.DatabaseError) as error:
        log.critical(error)

def update_aritlce_pub_date(conn, id, pubdate):
    try:
        log.info("Updating article id %s", id)
        # create a cursor
        cur = conn.cursor()

        try:
            #execute insert
            cur.execute(""" UPDATE news_article SET publish_date=%s WHERE id=%s""", (pubdate, id,))

        except psycopg2.IntegrityError as error:
            log.critical("Error %s, rollback.", error)
            conn.rollback()
        else:
            log.info("Commiting...")
            conn.commit()

        cur.close()
        log.debug("Update finished.")
    except (Exception, psycopg2.DatabaseError) as error:
        log.critical(error)
        pass

def update_news_article(conn, article, news_source_id, id):
    try:
        log.info("Updating article id %s", id)
        # create a cursor
        cur = conn.cursor()
        try:
            #execute insert
            cur.execute("""UPDATE news_article SET title=%s, text=%s WHERE id=%s and news_source_id=%s""", (article.title, article.text, id,news_source_id))
        except psycopg2.IntegrityError as error:
            log.critical("Error %s, rollback.", error)
            conn.rollback()
        else:
            log.info("Commiting...")
            conn.commit()
        cur.close()
        log.debug("Update finished.")
    except (Exception, psycopg2.DatabaseError) as error:
        log.critical(error)
        pass