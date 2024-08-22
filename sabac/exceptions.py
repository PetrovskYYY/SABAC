#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO Add file description
"""

"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2024, PerinatalCare backend"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = ""  # TODO Add licence
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"

from dataclasses import dataclass

from .constants import TestFailReasons


@dataclass()
class TestFailedException(Exception):
    reason: TestFailReasons
    message: str
# EOF
