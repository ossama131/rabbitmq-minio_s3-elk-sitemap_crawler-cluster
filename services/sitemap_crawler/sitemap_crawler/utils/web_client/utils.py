import requests

class WebClientResponse:
    def __init__(self, status_code:int) -> None:
        self.status_code = status_code

class SuccessResponse(WebClientResponse):
    def __init__(self, status_code: int, response: requests.Response) -> None:
        super().__init__(status_code)
        self.response = response

class ErrorResponse(WebClientResponse):
    pass

class SpecificErrorResponse:
    pass

class TimeoutError(SpecificErrorResponse):
    pass

class MaxLengthReached(SpecificErrorResponse):
    pass

class EmptyResponse(SpecificErrorResponse):
    pass

class UncaughtError(SpecificErrorResponse):
    pass

INDEFINE_ERROR_STATUS_CODE = 999