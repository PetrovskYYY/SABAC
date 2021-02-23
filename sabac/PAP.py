#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Policy administration point
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, sabac"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__version__ = "0.0.0"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"
__status__ = "dev"

# Standard library imports
import json
# Local source imports
from .algorithm import deny_unless_permit
from .policy_set import PolicySet


class PAP:
    def __init__(self, algorithm=deny_unless_permit):
        self.root_policy_set = PolicySet(algorithm=algorithm)  # Policy and policy sets are collected here

    def add_item(self, data):
        self.root_policy_set.add_item(data)

    def reload(self):  # pragma: no cover
        raise NotImplementedError("Base PAP class abstract reload method called.")


class FilePAP(PAP):
    def __init__(self, file_name, algorithm=deny_unless_permit, encoding='UTF-8'):
        PAP.__init__(self, algorithm=algorithm)
        self.load(file_name, encoding)

    def load(self, file_name, encoding='UTF-8'):
        self.file_name = file_name
        self.encoding = encoding
        json_file = open(file_name, encoding=encoding)
        data = json.load(json_file, encoding=encoding)
        self.root_policy_set = PolicySet(data)

    def reload(self):
        self.load(self.file_name, self.encoding)
# EOF
