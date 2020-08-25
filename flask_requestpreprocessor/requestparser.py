#!/usr/bin/python3
"""
Project : 
Author : sabariram
Date : 08-Jun-2020
"""

from functools import wraps
from datetime import datetime, date
from decimal import Decimal
import re

from flask import request

from .utility import is_non_empty_value


class HTTPException(Exception):

    def __init__(self, code, message, data):
        self.code = code
        self.data = data
        super().__init__(message)


class HTTPExceptionClientError(HTTPException):

    def __init__(self, code, message, data):
        super(HTTPExceptionClientError, self).__init__(code, message, data)


class HTTPExceptionBadRequest(HTTPExceptionClientError):

    def __init__(self, message, data=None):
        super(HTTPExceptionBadRequest, self).__init__(400, message, data)


class RequestParser:
    def __init__(self, definition, is_strict=True):
        self.is_strict = is_strict
        self.definition = self.validate_type_definition(definition)

    def __call__(self, func_obj):
        @wraps(func_obj)
        def role_checker(*args, **kwargs):
            kwargs.update(self.extract_request_data(*args, **kwargs))
            return func_obj(*args, **kwargs)

        return role_checker

    def extract_request_data(self, *args, **kwargs):
        return {}

    def parser(self, params, definition, parent=None):
        if is_non_empty_value(params) is False:
            params = {}
        validated_params = {}
        for key, type_def in definition.items():
            value = params.pop(key, None)
            required = type_def.pop("required", False)
            alias_key = type_def.pop('alias', key)
            data_type = type_def.pop('data_type')
            validator = type_def.pop('validator', None)
            child = type_def.pop('child', None)
            try:
                print_key = f"{parent}.{key}" if parent else key
                if is_non_empty_value(value):
                    validated_params[alias_key] = self.parse_value(print_key, value, data_type, validator, child,
                                                                   **type_def)
                elif required:
                    raise HTTPExceptionBadRequest(f"{print_key} should not be empty")
            finally:
                type_def["required"] = required
        if self.is_strict and is_non_empty_value(params):
            raise HTTPExceptionBadRequest(f'Unexpected params {list(params.keys())}')
        return validated_params

    @classmethod
    def parse_value(cls, key, value, data_type, validator, child, **value_constraints):
        if validator:
            value = validator(value)
        else:
            try:
                value = cls.type_converter(value, data_type)
            except Exception:
                raise HTTPExceptionBadRequest(f"{key} should be of type {data_type}")
        if child:
            if isinstance(child, dict):
                if data_type is dict:
                    value = cls.parser(value, child, key)
                elif data_type is list:
                    temp_list = []
                    for item in value:
                        list_item = cls.parser(item, child, key)
                        temp_list.append(list_item)
                    value = temp_list
            else:
                if data_type is not list:
                    raise HTTPExceptionBadRequest(f"{data_type} is not compatible for nested checks")
                for i, item in enumerate(value):
                    try:
                        list_item = cls.type_converter(item, child)
                        value[i] = list_item
                    except Exception:
                        raise HTTPExceptionBadRequest(f"{key} should be of {data_type} of {child}")
                    cls.check_value_constraint(list_item, key, **value_constraints)

        else:
            cls.check_value_constraint(value, key, **value_constraints)
        return value

    @staticmethod
    def check_value_constraint(value, key, min_val=None, max_val=None, allowed_value_list=None, regex=None,
                               regex_error_message=None):
        if min_val and value < min_val:
            raise HTTPExceptionBadRequest(f"{key} should be greater than or equal to {min_val}")
        if max_val and value > max_val:
            raise HTTPExceptionBadRequest(f"{key} should be lesser than or equal to {max_val}")
        if allowed_value_list and value not in allowed_value_list:
            raise HTTPExceptionBadRequest(f"{key} should be one of these - {allowed_value_list}")
        if regex and re.search(regex, value) is None:
            if regex_error_message:
                raise HTTPExceptionBadRequest(f"{key} {regex_error_message}")
            else:
                raise HTTPExceptionBadRequest(f"{key} should be of format - {regex}")

    @staticmethod
    def validate_type_definition(type_definition):
        return type_definition

    @staticmethod
    def type_converter(value, data_type):
        if (isinstance(data_type, BaseParam) and isinstance(value, data_type.name) is False) or isinstance(value,
                                                                                                           data_type) is False:
            value = data_type(value)
        return value


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


class BaseParam:
    def __init__(self, data_type):
        self.name = data_type

    def __call__(self, value):
        raise NotImplementedError

    def __repr__(self):
        return str(self.name)


class DateTimeParam(BaseParam):
    def __init__(self, fmt_string):
        self.fmt_string = fmt_string
        super().__init__(data_type=datetime)

    def __call__(self, value):
        if value is None:
            return datetime.now()
        return datetime.strptime(value, self.fmt_string)

    def __repr__(self):
        return f"{self.name} and format {self.fmt_string}"


class DateParam(BaseParam):
    def __init__(self, fmt_string):
        self.fmt_string = fmt_string
        super().__init__(data_type=date)

    def __call__(self, value=None):
        if value is None:
            return date.today()
        return datetime.strptime(value, self.fmt_string).date()

    def __repr__(self):
        return f"{str(self.name)} and format {self.fmt_string}"


class DecimalParam(BaseParam):
    def __init__(self):
        super().__init__(data_type=Decimal)

    def __call__(self, value=None):
        if value is None:
            return Decimal(0)
        return Decimal(str(value))


class FileParam(BaseParam):
    def __init__(self, mime_type=None, mime_list=None):
        self.mime_type = mime_type
        self.mime_list = mime_list
        super().__init__(data_type="File Stream Object")

    def __call__(self, file_mime_type):
        if self.mime_type:
            if file_mime_type.startswith(self.mime_type) is False:
                raise Exception()
        else:
            if file_mime_type not in self.mime_list:
                raise Exception()
        return file_mime_type

    def __repr__(self):
        if self.mime_type:
            return f"{str(self.name)} and mime type should be '{self.mime_type}'"
        super(FileParam, self).__repr__()
