#!/usr/bin/python3
"""
Project : 
Author : sabariram
Date : 08-Jun-2020
"""

from functools import wraps
import re

from .utility import is_non_empty_value
from .exceptions import HTTPBadRequestError
from .customparams import BaseParam


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
                    raise HTTPBadRequestError(f"{print_key} should not be empty")
            finally:
                type_def["required"] = required
        if self.is_strict and is_non_empty_value(params):
            raise HTTPBadRequestError(f'Unexpected params {list(params.keys())}')
        return validated_params

    @classmethod
    def parse_value(cls, key, value, data_type, validator, child, **value_constraints):
        if validator:
            value = validator(value)
        else:
            try:
                value = cls.type_converter(value, data_type)
            except Exception:
                raise HTTPBadRequestError(f"{key} should be of type {data_type}")
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
                    raise HTTPBadRequestError(f"{data_type} is not compatible for nested checks")
                for i, item in enumerate(value):
                    try:
                        list_item = cls.type_converter(item, child)
                        value[i] = list_item
                    except Exception:
                        raise HTTPBadRequestError(f"{key} should be of {data_type} of {child}")
                    cls.check_value_constraint(list_item, key, **value_constraints)

        else:
            cls.check_value_constraint(value, key, **value_constraints)
        return value

    @staticmethod
    def check_value_constraint(value, key, min_val=None, max_val=None, allowed_value_list=None, regex=None,
                               regex_error_message=None):
        if min_val and value < min_val:
            raise HTTPBadRequestError(f"{key} should be greater than or equal to {min_val}")
        if max_val and value > max_val:
            raise HTTPBadRequestError(f"{key} should be lesser than or equal to {max_val}")
        if allowed_value_list and value not in allowed_value_list:
            raise HTTPBadRequestError(f"{key} should be one of these - {allowed_value_list}")
        if regex and re.search(regex, value) is None:
            if regex_error_message:
                raise HTTPBadRequestError(f"{key} {regex_error_message}")
            else:
                raise HTTPBadRequestError(f"{key} should be of format - {regex}")

    @staticmethod
    def validate_type_definition(type_definition):
        return type_definition

    @staticmethod
    def type_converter(value, data_type):
        if (isinstance(data_type, BaseParam) and isinstance(value, data_type.name) is False) or isinstance(value,
                                                                                                           data_type) is False:
            value = data_type(value)
        return value
