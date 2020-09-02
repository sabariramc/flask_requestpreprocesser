#!/usr/bin/python3
"""
Project : 
Author : sabariram
Date : 02-Sep-2020
"""

from flask import request

from .requestparser import RequestParser


class QueryParamParser(RequestParser):

    def extract_request_data(self, *args, **kwargs):
        return self.parser(self.get_normalize_query_params(), self.definition)

    @staticmethod
    def get_normalize_query_params():
        params_non_flat = request.args.to_dict(flat=False)
        return {key: value if len(value) > 1 else value[0] for key, value in params_non_flat.items()}


class JSONRequestParser(RequestParser):
    def extract_request_data(self, *args, **kwargs):
        return self.parser(request.json, self.definition)


class FormRequestParser(RequestParser):
    def extract_request_data(self, *args, **kwargs):
        return self.parser(request.form, self.definition)


class HeaderParser(RequestParser):
    def extract_request_data(self, *args, **kwargs):
        return self.parser(request.headers, self.definition)


class FileStreamParser(RequestParser):
    def extract_request_data(self, *args, **kwargs):
        return self.parser(request.files, self.definition)


def parse_request_args(query_param_definition, is_strict=True):
    def inner_get_fu(fu):
        return QueryParamParser(query_param_definition, is_strict=is_strict)(fu)

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
        return HeaderParser(header_definition, is_strict=is_strict)(fu)

    return inner_get_fu
