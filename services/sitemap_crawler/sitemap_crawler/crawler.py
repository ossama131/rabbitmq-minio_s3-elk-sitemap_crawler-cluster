from utils.web_client.webclient import WebClient
from utils.helpers import (
    get_valid_response, 
    get_sitemap_body, 
    get_sitemap_object, 
    iter_sitemap_entries
)
from utils.logger import spider_logger

class SitemapSpider:
    def __init__(self, max_response_length=100*1024*1024, timeout=10, max_recursion_level=10) -> None:
        self.client = WebClient(max_response_length, timeout)
        self._max_recursion_level = max_recursion_level

    def fetch_sitemap(self, url:str, recursion_level):
        response = get_valid_response(self.client, url)
        if response:
            body = get_sitemap_body(response)
            if body:
                s = get_sitemap_object(body)
                if s:
                    if s.type == 'sitemapindex':
                        if recursion_level >= self._max_recursion_level:
                            spider_logger.info('MaxRecursionLevelReached', extra={'max_recursion_level': self._max_recursion_level})
                            return
                        else:
                            parsed = {'type': s.type, 'urls': []}
                            for entry in iter_sitemap_entries(s):
                                parsed['urls'].append(entry['loc'])
                            number_of_urls = len(parsed['urls'])
                            spider_logger.info('Parsed', extra={
                                "type":s.type,
                                "#urls": number_of_urls,
                                "depth": recursion_level
                            })
                            return parsed

                    elif s.type == 'urlset':
                        parsed = {'type': s.type, 'urls': []}
                        for entry in iter_sitemap_entries(s):
                            parsed['urls'].append(entry['loc'])
                        number_of_urls = len(parsed['urls'])
                        spider_logger.info('Parsed', extra={
                            "type":s.type,
                            "#urls": number_of_urls,
                            "depth": recursion_level
                        })
                        return parsed
                    else:
                        spider_logger.info('Parsed', extra={"type":s.type})
                        return
