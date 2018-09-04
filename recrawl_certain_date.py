# -*- coding: utf-8 -*-
#!/usr/bin/python
from crawler.database import connect ,get_articles_for_date, update_news_article, get_news_articles_count_for_date
import logging
from newspaper import Article

log = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(asctime)s %(name)s - %(message)s')

    re_crawl()


def re_crawl():
    conn = connect()

    from_date = '2018-05-17'
    to_date = '2018-05-18'

    count = get_news_articles_count_for_date(conn, from_date, to_date )

    log.info("To re-crawl %s articles.",count)

    offset = 0
    limit = 1000

    while offset <= count:
        log.info("Offset %s, Limit %s", offset, limit)
        articles = get_articles_for_date(conn, from_date, to_date, offset, limit)

        offset += limit

        article_count = 0
        for a in articles:
            id = a[0]
            url = a[1]
            language = a[2]
            news_source_id = a[3]
            log.info("Crawling article with id=%s, url=%s, language=%s and news_source_id=%s", id, url, language, news_source_id)
            try:
                article = Article(url, language=language, fetch_images=False)
                article.download()
                article.parse()

                article_count += 1
                update_news_article(conn, article, news_source_id, id)
            except:
                pass
        log.info("Crawled %s articles in this round.", article_count)

if __name__ == '__main__':
    main()