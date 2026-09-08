#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contains different general purpose methods
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2024, SABAC"
__license__ = "LGPL"
__email__ = "yuriy.petrovskiy@gmail.com"

import logging
from typing import Any, List


def get_object_by_path(root_object: Any, path_parts: List[str]) -> Any:
    """
    Returns an object using the provided path and root object.
    :param root_object: Dict or class
    :param path_parts: List of strings
    :return: Value of an object that if found by a given path or None if path resolution failed.
    """
    obj = root_object
    for index, part in enumerate(path_parts):
        try:
            obj = getattr(obj, part)
        except AttributeError:
            if isinstance(obj, list):
                results = []
                for item in obj:
                    result = get_object_by_path(item, path_parts[index:])
                    if result is not None:
                        results.append(result)
                obj = results
                break
            else:
                try:
                    obj = obj[part]
                except (TypeError, KeyError):
                    return None
    return obj

def logging_by_level_name(level_name:str, *args, **kwargs):
    if level_name == 'DEBUG':
        return logging.debug(*args, **kwargs)
    elif level_name == 'INFO':
        return logging.info(*args, **kwargs)
    elif level_name == 'WARNING':
        return logging.warning(*args, **kwargs)
    elif level_name == 'ERROR':
        return logging.error(*args, **kwargs)
    elif level_name == 'CRITICAL':
        return logging.critical(*args, **kwargs)
    else:
        return logging.log(level_name,*args, **kwargs)

# EOF
