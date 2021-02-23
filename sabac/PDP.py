#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Policy Decision Point
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, SABAC"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__version__ = "0.0.0"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"
__status__ = "dev"

# Local source imports
from .PAP import PAP
from .PIP import PIP


class PDP:
    """Policy decision point"""

    def __init__(self, pap_instance=None, pip_instance=None):
        # Setting Policy Administration Point
        if pap_instance is not None:
            self.PAP = pap_instance
        else:  # pragma: no cover
            self.PAP = PAP()  # Using empty PAP as a stub

        # Setting Policy Information Point
        if pip_instance is not None:
            self.PIP = pip_instance
        else:   # pragma: no cover
            self.PIP = PIP()  # Using empty PIP as a stub

    def evaluate(self, request):
        request.PDP = self
        return self.PAP.root_policy_set.evaluate(request)
# EOF
