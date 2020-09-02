#!/usr/bin/python3
"""
Project : 
Author : sabariram
Date : 02-Sep-2020
"""


class HTTPError(Exception):

    def __init__(self, code, message, data):
        self.code = code
        self.data = data
        super().__init__(message)


class HTTPClientError(HTTPError):

    def __init__(self, code, message, data):
        super(HTTPClientError, self).__init__(code, message, data)


class HTTPBadRequestError(HTTPClientError):

    def __init__(self, message, data=None):
        super(HTTPBadRequestError, self).__init__(400, message, data)
