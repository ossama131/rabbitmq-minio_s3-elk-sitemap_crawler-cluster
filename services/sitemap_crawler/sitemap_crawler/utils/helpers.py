import traceback

from .gz import is_gzipped, gunzip
from .sitemap import Sitemap

from .web_client.webclient import WebClient
from .web_client.utils import (
    WebClientResponse,
    SuccessResponse,
    SpecificErrorResponse,
)

from .logger import spider_logger, webclient_logger

def get_valid_response(web_client: WebClient, url:str):
    '''Return SuccessResponse or None in case of Error. All errors are catched and logged'''

    try:
        response = web_client.get(url)
    except Exception as e:
        webclient_logger.error('UncaughtException', extra={'traceback': traceback.format_exc()})
        return
    
    try:
        assert isinstance(response, WebClientResponse) or isinstance(response, SpecificErrorResponse), 'Invalid Response'
    except AssertionError as e:
        return
    
    if isinstance(response, SuccessResponse):
        return response

    return

def get_sitemap_body(response:SuccessResponse):
    '''Unzip body if it is gzipped and decode it. Return None in case of error'''
    body = response.response.content
    if is_gzipped(body):
        try:
            compressed_size = len(body)
            body = gunzip(body)
            decompressed_size = len(body)
            spider_logger.info('CompressedSitemap', extra={
                'compressed_size':compressed_size,
                'decompressed_size':decompressed_size
            })
        except Exception as e:
            spider_logger.info('UnzippingError', extra={'traceback': traceback.format_exc()})
            return
    
    for enc in ('utf-8', 'cp1252', 'utf-8-sig'):
        try:
            body.decode(enc)
        except UnicodeError:
            continue
        
        spider_logger.info('EncodingType', extra={'encoding': enc})
        return body.decode(enc)
        
    spider_logger.info('UnicodeError')
    return

def get_sitemap_object(response_body:str):
    try:
        s = Sitemap(response_body.encode('utf-8'))
    except Exception as e:
        spider_logger.info('SitemapParsingError')
        return
    
    return s


def iter_sitemap_entries(s:Sitemap):
    for entry in s:
        yield entry
