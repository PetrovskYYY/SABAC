#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contains different general purpose methods
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2024, PerinatalCare backend"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"

import logging


def get_object_by_path(root_object, path_parts, prefix=None):
    """
    Returns object using provided path and root object.
    Functions treats dict keys and class properties as path parts
    :param root_object: dict or class
    :param path_parts: list of strings
    :param prefix: prefix for path (used internally for recursion)
    :return: Value of object that if found by given path or None if path resolution failed.
    """
    sub_object = None
    if isinstance(root_object, dict) and path_parts[0] in root_object:
        # Object is dict
        sub_object = root_object[path_parts[0]]
    elif hasattr(root_object, path_parts[0]):
        # Object is some class that has required attribute or property
        sub_object = getattr(root_object, path_parts[0])
    else:
        full_attribute_name = path_parts[0]
        if prefix is not None:
            full_attribute_name = f"{prefix}.{path_parts[0]}"
        logging.info(
            f"No information providers found for attribute '{full_attribute_name}' "
            f"for object ({root_object.__class__.__name__}){root_object}."
        )
        return None

    if len(path_parts) == 1:
        # It is a last portion of given path
        return sub_object

    # There is at least one more level in path
    new_prefix = prefix
    if new_prefix is None:
        new_prefix = path_parts[0]
    else:
        new_prefix = f"{new_prefix}.{path_parts[0]}"

    return get_object_by_path(
        root_object=sub_object,
        path_parts=path_parts[1:],
        prefix=new_prefix
    )
# EOF
