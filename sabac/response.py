#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO Add file description
"""
ABAC Response class
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
import copy
# Local source imports
from .constants import *


class Response:

    def __init__(self, request, decision=RESULT_NOT_APPLICABLE):
        self.request = request
        self.decision = decision
        # Obligations to execute
        self.obligations = []
        # Advices to execute
        self.advices = []
        # Policies that were involved in decision
        self.polices = []

    def to_json(self):
        result = {
            'decision': self.decision,
        }

        if len(self.obligations) > 0:
            result['obligations'] = self.obligations

        if len(self.advices) > 0:
            result['advices'] = self.advices

        if len(self.polices) > 0:
            result['polices'] = self.polices

        return result

    def copy(self):
        new_copy = Response(self.request)  # Adding reference to request object
        new_copy.decision = self.decision
        new_copy.obligations = copy.deepcopy(self.obligations)
        new_copy.advices = copy.deepcopy(self.advices)
        new_copy.polices = copy.deepcopy(self.polices)
        return new_copy

    def join_data(self, other_request, prepend=False):
        """
        Joins request data (obligations, advices, used_policy_list) with other request.
        :param other_request: Request object to join with
        :param prepend: Add other object data before data of current object
        """
        if prepend is True:
            self.obligations = other_request.obligations + self.obligations
            self.advices = other_request.advices + self.advices
            self.polices = other_request.polices + self.polices
        else:
            self.obligations = self.obligations + other_request.obligations
            self.advices = self.advices + other_request.advices
            self.polices = self.polices + other_request.polices

    def add_advice(self, advice):
        self.advices.append(advice)

    def __repr__(self):
        return "<Response %s>" % self.to_json()
# EOF
