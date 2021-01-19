#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Request class
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, SABAC"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__version__ = "0.0.0"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"
__status__ = "dev"


class Request:
    def __init__(self, attributes, return_policy_id_list=False):
        if attributes and isinstance(attributes, dict) and len(attributes) > 0:
            self.attributes = attributes
        else:  # pragma: no cover
            raise ValueError("Request should contain attributes: %s given." % attributes)
        self.return_policy_id_list = return_policy_id_list

    def __repr__(self):
        return "<Request %s>" % self.to_json()

    def to_json(self):
        return self.attributes
# EOF
