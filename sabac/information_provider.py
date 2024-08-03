#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base class for information providers
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2024, PerinatalCare backend"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"


class InformationProvider:
    """
    Base class for information providers
    """
    def __init__(self):
        self.provided_attributes = None

    @classmethod
    def fetch(cls, request):
        return cls.fetch_value(request.attributes)

    @classmethod
    def fetch_value(cls, request):
        raise NotImplementedError()
# EOF
