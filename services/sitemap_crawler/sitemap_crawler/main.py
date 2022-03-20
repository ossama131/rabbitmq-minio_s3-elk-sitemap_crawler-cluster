from hashlib import md5
import time
import os, sys
import json

import tldextract

from crawler import SitemapSpider
from utils.rabbitmq_utils import publish, start_consuming
from utils.init_connections import (
    input_consumer_conn,
    input_producer_conn,
    output_producer_conn,
    logs_producer_conn,
    input_consumer_channel,
    input_producer_channel,
    output_producer_channel,
    input_queue,
    output_queue,
)

spider = SitemapSpider()

def close_all_rabbitmq_conn():
    try:
        if input_consumer_conn:
            input_consumer_conn.close()
        if input_producer_conn:
            input_producer_conn.close()
        if output_producer_conn:
            output_producer_conn.close()
        if logs_producer_conn:
            logs_producer_conn.close()
        return True, ''
    except Exception as e:
        return False, e

def callback(ch, method, properties, body):
    #print(" [x] Received %r" % body)
    body_json = json.loads(body)
    sitemap_url = body_json['url']
    recursive_level = int(body_json['recursive_level'])
    parsed = spider.fetch_sitemap(sitemap_url, recursive_level)
    if parsed:
        if parsed['type'] == 'sitemapindex' and parsed['urls']:
            for url in parsed['urls']:
                body = {
                    'url': url,
                    'recursive_level': recursive_level + 1
                }
                publish(input_producer_channel, input_queue, body)
        elif parsed['type'] == 'urlset' and parsed['urls']:
            for url in parsed['urls']:
                url=str(url)
                parsed_url = tldextract.extract(url)
                url_domain_name = parsed_url.domain + '.' + parsed_url.suffix
                domain_hash = md5(url_domain_name.encode('utf-8')).hexdigest()
                body = {
                    'domain_hash': domain_hash,
                    'url': url,
                    'subdomain': parsed_url.subdomain,
                    'domain': parsed_url.domain,
                    'suffix': parsed_url.suffix
                }
                publish(output_producer_channel, output_queue, body)
    #print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    start_consuming(input_consumer_channel, input_queue, callback)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        print('Closing Connections to RabbitMQ')
        conn_closed, e = close_all_rabbitmq_conn()
        while not conn_closed:
            print(f'Failed: {e}')
            print('Trying Again to close all connections after 5 sec!')
            time.sleep(5)
            conn_closed = close_all_rabbitmq_conn()
        print('All connections closed succefully!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
