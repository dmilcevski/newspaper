# -*- coding: utf-8 -*-
#!/usr/bin/python
from crawler.database import connect, get_news_source_count, get_news_sources, get_news_source, insert_news_article, insert_news_articles, articles_exist, articles_exist2, articles_for_news_source
import logging
import time

log = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(asctime)s %(name)s - %(message)s')

    crawl()


def crawl():
    import newspaper
    from newspaper import news_pool

    memoize_articles = True

    conn = connect()

    threads_per_source = 4

    round = 0

    #loop indefinetely
    while True:
        count = get_news_source_count(conn)
        offset = 0
        limit = 15
        round += 1
        log.info("Crawling round %s.", round)
        while offset <= count:
            papers = []
            sources = get_news_sources(conn, offset, limit)

            offset += limit

            for source in sources:
                log.info("Creating newspaper for source %s", source[1])
                news_paper = newspaper.build(source[1], memoize_articles=memoize_articles, MIN_WORD_COUNT=100)

                papers.append(news_paper)
                log.info("Found %s articles from %s.", news_paper.size(), source[1])

            log.info("Creating a pool of newspapers for %s newspapers.", len(papers))
            news_pool.set(papers, threads_per_source=threads_per_source)

            log.info("Downloading articles for all newspapers.")
            start_time = time.time()
            news_pool.join()

            end_time = time.time() - start_time
            log.info("Downloading finished in %s", end_time)

            log.info("Storing downloaded articles in the database.")
            for paper in papers:
                #get the source id for this nespaper
                news_source_id = get_news_source(conn, paper.url)[0]

                #Get already cralwed articles for this newspaper
                crawled_urls = articles_exist(conn, paper.article_urls())
                crawled_urls_size = 0
                if crawled_urls:
                    crawled_urls_size = len(crawled_urls)
                else:
                    crawled_urls = ['']

                log.info("For newspaper %s %s articles already crawled.", paper.url, crawled_urls_size)
                #articles = []
                #crawled_articles = articles_for_news_source(conn, news_source_id)

                for article in paper.articles:
                    #if the article is not crawled already
                    if article.url not in crawled_urls:
                        #parse it
                        try:
                            article.parse()
                            #check if its a news article, and not some other page
                            if article.is_valid_body():
                                insert_news_article(conn, article, news_source_id)
                        except:
                            pass

                            #Check if the combination title and publish date already exists for this newspaper
                            #publish_date = article.publish_date
                            #if publish_date:
                            #    publish_date = publish_date.replace(tzinfo=None)

                            #if (article.title, publish_date) not in crawled_articles:
                                #If not, add it for insertion
                            #    articles.append(article)
                            #    crawled_articles.append((article.title, publish_date))
                            #    log.info("Article '%s' publish date '%s' doesn't exists.", article.title, publish_date)
                            #else:
                            #    log.warn("Article '%s' already exists", article.url)

                #Insert the articles in the database
                #insert_news_articles(conn, list(set(articles)), news_source_id)

        time.sleep(1000) #sleep for 1000 seconds before continuing

if __name__ == '__main__':
   main()