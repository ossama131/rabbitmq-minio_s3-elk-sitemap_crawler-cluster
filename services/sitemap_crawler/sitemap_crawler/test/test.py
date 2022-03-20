import sys
sys.path.append("..")

from init_connections import input_producer_channel, input_queue, input_producer_conn

from utils.rabbitmq_utils import publish


url_gz = 'https://vimeo.com/sitemap/latest.xml.gz'
url = 'https://www.uni-passau.de/sitemaps/sitemap_de.xml'
url_non_sitemap = 'https://github.com/scrapy/scrapy/blob/master/scrapy/utils/sitemap.py'
url_sitemap_index = 'https://www.bbc.com/sitemaps/https-index-com-news.xml'
url_rss = 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'

body = {
    'url': 'https://www.bbc.com/sitemaps/https-index-com-news.xml',
    'recursive_level': 1
}

publish(input_producer_channel, input_queue, body)

try:
    input_producer_conn.close()
except:
    print('failed to close connection to RabbitMQ')

print('Connection closed successfully!')