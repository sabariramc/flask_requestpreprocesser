#!/usr/bin/python3
"""
Project : 
Author : sabariram
Date : 02-Sep-2020
"""

from flask import request
from functools import wraps
from copy import deepcopy

from funcargpreprocessor import FunctionArgPreProcessor
from funcargpreprocessor import FieldError


class FlaskRequestParser(FunctionArgPreProcessor):

    def __call__(self, func_obj):
        @wraps(func_obj)
        def inner_function(*args, **kwargs):

            raw_argument = self.extract_request_data(*args, **kwargs)
            try:
                parsed_argument = self.parser(raw_argument, deepcopy(self.definition))
            except FieldError as e:
                return {
                           "error": {
                               "code": e.error_code.name
                               , "field": e.field_name
                               , "message": str(e)
                               , "description": e.error_data
                           }
                       }, 400
            kwargs.update(parsed_argument)
            return func_obj(*args, **kwargs)

        return inner_function


class QueryParamParser(FlaskRequestParser):

    def extract_request_data(self, *args, **kwargs):
        return self.get_normalize_query_params()

    @staticmethod
    def get_normalize_query_params():
        params_non_flat = request.args.to_dict(flat=False)
        return {key: value if len(value) > 1 else value[0] for key, value in params_non_flat.items()}


class JSONRequestParser(FlaskRequestParser):
    def extract_request_data(self, *args, **kwargs):
        return request.json


class FormRequestParser(FlaskRequestParser):
    def extract_request_data(self, *args, **kwargs):
        return request.form


class RequestHeaderParser(FlaskRequestParser):
    def extract_request_data(self, *args, **kwargs):
        return request.headers


class FileStreamParser(FlaskRequestParser):
    def extract_request_data(self, *args, **kwargs):
        return request.files


def parse_request_query_param(query_param_definition, is_strict=True, auto_type_cast=True):
    def inner_get_fu(fu):
        return QueryParamParser(query_param_definition, is_strict=is_strict, auto_type_cast=auto_type_cast)(fu)

    return inner_get_fu


def parse_request_form(form_definition, is_strict=True):
    def inner_get_fu(fu):
        return FormRequestParser(form_definition, is_strict=is_strict)(fu)

    return inner_get_fu


def parse_request_json(json_definition, is_strict=True):
    def inner_get_fu(fu):
        return JSONRequestParser(json_definition, is_strict=is_strict)(fu)

    return inner_get_fu


def parse_request_file(file_definition, is_strict=True):
    def inner_get_fu(fu):
        return FileStreamParser(file_definition, is_strict=is_strict)(fu)

    return inner_get_fu


def parse_request_header(header_definition, is_strict=False):
    def inner_get_fu(fu):
        return RequestHeaderParser(header_definition, is_strict=is_strict)(fu)

    return inner_get_fu
