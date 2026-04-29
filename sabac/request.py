#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Request class
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, SABAC"
__license__ = "LGPL"
__email__ = "yuriy.petrovskiy@gmail.com"

from typing import Any, Dict


class Request:
    attributes: Dict[str, Any]
    return_policy_id_list: bool

    def __init__(self, attributes: Dict[str, Any], return_policy_id_list: bool = False) -> None:
        if attributes and isinstance(attributes, dict) and len(attributes) > 0:
            self.attributes = attributes
        else:  # pragma: no cover
            raise ValueError("Request should contain attributes: %s given." % attributes)
        self.return_policy_id_list = return_policy_id_list

    def __repr__(self) -> str:
        result = "<Request data:"
        for key, value in self.attributes.items():
            result += "\n  %s: %s" % (key, value)
        result += "\n>"
        return result

    def to_json(self) -> Dict[str, Any]:
        return self.attributes
# EOF
