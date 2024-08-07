#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simplified Attribute Based Access Control
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, SABAC"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"

# Standard library imports
import json
import os
import logging
# 3rd party imports
import pytest
# Local source imports
from sabac import PDP, FilePAP, PIP, InformationProvider, DenyBiasedPEP, Request


@pytest.fixture(scope="module")
def pdp_instance():
    # Preparing logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Creating Policy Administration Point
    # Using file to import policies
    script_dir = os.path.dirname(os.path.realpath(__file__))
    test_pap = FilePAP(f"{script_dir}/test_policies.json")

    # Creating Policy Information Point
    test_pip = PIP()

    # Creating Information Provider Class

    class ResourceTypeProvider(InformationProvider):
        required_attributes = ['resource']
        provided_attributes = ['resource.type']

        @classmethod
        def fetch_value(cls, attributes):
            if isinstance(attributes['resource'], dict) and 'type' in attributes['resource']:
                return attributes['resource']['type']

    # Adding information provider to PIP
    test_pip.add_provider(ResourceTypeProvider)

    class ResourceIDProvider(InformationProvider):
        required_attributes = ['resource']
        provided_attributes = ['resource.id']

        @classmethod
        def fetch_value(cls, attributes):
            if isinstance(attributes['resource'], dict) and 'id' in attributes['resource']:
                return attributes['resource']['id']

    test_pip.add_provider(ResourceIDProvider)

    test_pdp = PDP(pap_instance=test_pap, pip_instance=test_pip)
    return test_pdp


def test_pap_reload(pdp_instance):
    pdp_instance.PAP.reload()


def test_pep1(pdp_instance):
    context = {
        'resource.type': 'user',
        'action': 'create',
        'subject': {'id': 1},
        # 'subject.id': 1
    }
    test_pep = DenyBiasedPEP(pdp_instance)
    assert test_pep.evaluate(context)


def test_pep2(pdp_instance):
    context = {
        'resource.type': 'user',
        'action': 'create',
        'subject': {'id': 2},
    }

    test_pep = DenyBiasedPEP(pdp_instance)
    assert not test_pep.evaluate(context, True)


def test_pep3(pdp_instance):
    """
    Incorrect request - no 'resource.id' attribute
    """
    context = {
        'resource.type': 'user',
        'action': 'view',
        'subject': {'id': 1},
    }
    test_pep = DenyBiasedPEP(pdp_instance)
    assert not test_pep.evaluate(context)


def test_pep4(pdp_instance):
    """
    User may view own properties
    """
    context = {
        'resource': {
            'type': 'user',
            'id': 2
        },
        'action': 'view',
        'subject': {'id': 2},
    }

    test_pep = DenyBiasedPEP(pdp_instance)
    assert test_pep.evaluate(context)


def test_pep5(pdp_instance):
    """
    Admin can view other users
    """
    context = {
        'resource': {
            'type': 'user',
            'id': 2
        },
        'action': 'view',
        'subject': {'id': 1},
    }

    test_pep = DenyBiasedPEP(pdp_instance)
    assert test_pep.evaluate(context)


def test_pep5_1(pdp_instance):
    """
    Common users can NOT view other users
    """
    context = {
        'resource': {
            'type': 'user',
            'id': 1
        },
        'action': 'view',
        'subject': {'id': 2},
    }

    test_pep = DenyBiasedPEP(pdp_instance)
    assert not test_pep.evaluate(context)


def test_pep6(pdp_instance):
    """
    Any user can edit own properties
    """
    context = {
        'resource.type': 'user',
        'resource.id': 2,
        'action': 'view',
        'subject.id': 2
    }

    test_pep = DenyBiasedPEP(pdp_instance)
    assert test_pep.evaluate(context)


def test_pep7(pdp_instance):
    """
    Attempt to update other user by common user
    """
    context = {
        'resource.type': 'user',
        'resource.id': 5,
        'action': 'update',
        'subject.id': 2
    }

    test_pep = DenyBiasedPEP(pdp_instance)
    assert not test_pep.evaluate(context, True)


def test_pep8(pdp_instance):
    """
    Attempt to update other user by admin
    """
    context = {
        'resource.type': 'user',
        'resource.id': 5,
        'action': 'update',
        'subject.id': 1,
        'subject.attribute.roles': ['test', 'admin']
    }

    test_pep = DenyBiasedPEP(pdp_instance)
    assert test_pep.evaluate(context, True)


def test_advice_1(pdp_instance):
    """
    Attempt to erase_personal_data should return advice
    """
    context = {
        'resource.type': 'user',
        'resource.id': 1,
        'action': 'erase_personal_data',
        'subject.id': 1
    }

    test_pep = DenyBiasedPEP(pdp_instance)
    request = Request(attributes=context, return_policy_id_list=True)
    result = pdp_instance.evaluate(request)

    assert len(result.advices) == 1

    assert test_pep.evaluate(context, True)


def test_pip_1(pdp_instance):
    """
    Attempt to update other user by admin
    """
    context = {
        'resource': {'type': 'user', 'id': 5},
        'action': 'update',
        'subject.id': 1,
        'subject.attribute.roles': ['test', 'admin']
    }

    test_pep = DenyBiasedPEP(pdp_instance)
    assert test_pep.evaluate(context, True)


def test_pip_2(pdp_instance):
    """
    Attempt to update other user by admin
    """
    context = {
        'resource': {'type': 'user'},
        'action': 'update',
    }

    test_pep = DenyBiasedPEP(pdp_instance)
    assert not test_pep.evaluate(context, True)


def test_pip_3(pdp_instance):
    """
    list users
    """
    context = {
        'resource.type': 'user',
        'action': 'view',
        'subject.id': 1,
        'resource.id': None
    }

    test_pep = DenyBiasedPEP(pdp_instance)
    assert not test_pep.evaluate(context, True)


def test_pip_4(pdp_instance):
    """
    Request for update of different user data by common user
    """
    test_pep = DenyBiasedPEP(pdp_instance)

    permit3 = test_pep.evaluate({
        'resource': {'type': 'user', 'id': 1},
        'action': 'update',
        'subject.id': 5,
        'subject.attribute.roles': ['test']
    }, True, debug=True)
    assert not permit3


def test_pip_5(pdp_instance):
    """
    Repeated request
    """
    test_pep = DenyBiasedPEP(pdp_instance)

    permit2 = test_pep.evaluate({
        'resource': {'type': 'user', 'id': 5},
        'action': 'update',
        'subject.id': 5,
        'subject.attribute.roles': ['test']
    }, True, debug=True)
    assert permit2

    permit1 = test_pep.evaluate({
        'resource': {'type': 'user', 'id': 1},
        'action': 'update',
        'subject.id': 1,
        'subject.attribute.roles': ['test', 'admin']
    }, True)
    assert permit1

    permit3 = test_pep.evaluate({
        'resource': {'type': 'user', 'id': 1},
        'action': 'update',
        'subject.id': 5,
        'subject.attribute.roles': ['test']
    }, True, debug=True)
    assert not permit3


def test_pip_6(pdp_instance):
    """
    Repeated request
    """
    test_pep = DenyBiasedPEP(pdp_instance)

    # request = Request(attributes=context, return_policy_id_list=return_policy_id_list)
    # result = pdp_instance.evaluate(request)

    permit = test_pep.evaluate({
        'subject.id': 2,
        'subject.department': ['moderators'],
        'action': 'view',
        'resource': 1,
        'resource.type': 'exam',
        'resource.allowed_departments': ['moderators']
    }, True, debug=True)
    assert permit


def test_tests_from_file(pdp_instance):
    """
    Loads list of tests from JSON file
    """
    script_dir = os.path.dirname(os.path.realpath(__file__))
    json_file = open(f"{script_dir}/policy_tests.json")
    test_json_data = json.load(json_file)
    test_pep = DenyBiasedPEP(pdp_instance)
    tests_result = test_pep.run_tests(test_json_data)

    assert tests_result == []
# EOF
