import traceback
import requests

from .utils import (
    SuccessResponse,
    ErrorResponse, 
    TimeoutError, 
    MaxLengthReached, 
    EmptyResponse,
    UncaughtError, 
    INDEFINE_ERROR_STATUS_CODE
)

from ..logger import webclient_logger

class WebClient:

    __USER_AGENT = 'cc_sitemap_spider'

    def __init__(self, max_response_length=100*1024*1024, timeout=10) -> None:
        self._max_response_length = max_response_length
        self._timeout = timeout

    def get(self, url:str):
        try:
            response = requests.get(
                url,
                timeout=self._timeout,
                stream=True,
                allow_redirects=False,
                headers={'User-Agent': self.__USER_AGENT}
            )

        except requests.exceptions.Timeout as ex:
            webclient_logger.info('RequestFailed', extra={
                'reason':'Timeout',
                'timeout_duration':self._timeout
            })
            return TimeoutError

        except requests.exceptions.RequestException as ex:
            if hasattr(response, 'status_code'):
                status_code = response.status_code
            else:
                status_code = INDEFINE_ERROR_STATUS_CODE
            webclient_logger.info('RequestFailed', extra={
                'reason':'RequestException', 
                'status_code': status_code
            })
            return ErrorResponse(status_code)
        
        except:
            webclient_logger.error('UncaughtException', extra={'traceback': traceback.format_exc()})
            return UncaughtError
        
        else:
            if 200 <= response.status_code <= 299:
                content_length = int(response.headers.get('Content-Length', 0))
                if content_length > self._max_response_length:
                    webclient_logger.info('RequestSucceeded', extra={
                        'max_length_reached':True,
                        'max_length': self._max_response_length,
                        'status_code':response.status_code
                    })
                    return MaxLengthReached
                    
                content_length = 0
                content = b''
                for chunk in response.iter_content(1024):
                    content_length += len(chunk)
                    if content_length > self._max_response_length:
                        webclient_logger.info('RequestSucceeded', extra={
                            'max_length_reached':True,
                            'max_length': self._max_response_length,
                            'status_code':response.status_code
                        })
                        return MaxLengthReached
                    content += chunk

                if not content: #Empty page
                    webclient_logger.info('RequestSucceeded', extra={
                        'empty_page':True,
                        'status_code':response.status_code
                    })
                    return EmptyResponse

                response._content = content
                webclient_logger.info('RequestSucceeded', extra={
                    'Content-Length':len(content),
                    'status_code':response.status_code
                })
                return SuccessResponse(response.status_code, response)
                
            webclient_logger.info('RequestFailed', extra={
                'reason':'RequestException',
                'status_code': response.status_code
            })
            return ErrorResponse(response.status_code)