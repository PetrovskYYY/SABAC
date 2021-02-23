#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simplified Attribute Based Access Control
"""
__author__ = "Yuriy Petrovskiy"
__copyright__ = "Copyright 2020, SABAC"
__credits__ = ["Yuriy Petrovskiy"]
__license__ = "LGPL"
__version__ = "0.0.0"
__maintainer__ = "Yuriy Petrovskiy"
__email__ = "yuriy.petrovskiy@gmail.com"
__status__ = "dev"

# Standard library imports
import logging
# 3rd party imports
import pytest
# Local source imports
from .sabac import PDP, PAP, PIP, InformationProvider, DenyBiasedPEP, deny_unless_permit, Request


@pytest.fixture(scope="module")
def pdp_instance():
    # Prepairing logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Creating Policy Administration Point
    test_pap = PAP(deny_unless_permit)

    # Adding policy to PAP
    test_pap.add_item({
        "description": "Admin permissions",
        "target": {
            'subject.attribute.roles': {'@contains': 'admin'},
        },
        "algorithm": "DENY_UNLESS_PERMIT",
        'rules': [
            {
                "effect": "PERMIT",
                "description": "Allow to manage users",
                "target": {
                    'resource.type': 'user',
                    'action': {'@in': ['create', 'view', 'update', 'erase_personal_data', 'delete']},
                },
            }
        ]
    })

    test_pap.add_item({
        "description": "User  can view, edit, or erase_personal_data his/her own profile",
        "target": {
            'resource.type': 'user',
            'subject.id': {'!=': None},
        },
        "algorithm": "DENY_UNLESS_PERMIT",
        'rules': [
            {
                "description": "User  can view his/her own profile",
                "target": {
                    'action': 'view',
                },
                "condition": {
                    'subject.id': {'==': 'resource.id'},
                },
                "effect": "PERMIT",
            },
            {
                "description":
                    "User  can edit, or erase_personal_data his/her own profile. "
                    "Action should be logged (if possible).",
                "target": {
                    'action': {'@in': ['update', 'erase_personal_data']},
                },
                "condition": {
                    'resource.id': {'==': 'subject.id'},
                },
                "effect": "PERMIT",
                "advices": [{
                    'action': 'log',
                    'fulfill_on': 'PERMIT',
                    'attributes': {
                        'user': {'@': 'user'},
                        'action': {'@': 'action'},
                        'message': "User {user.display_name}(#{user.public_id}) is going to perform action {action} "
                                   "on own profile."
                    }
                }],
                "obligations": [
                    {
                        'action': 'admin_email',
                        'fulfill_on': 'PERMIT',
                        'attributes': {
                            'user': {'@': 'user'},
                            'action': {'@': 'action'},
                            'message':
                                "User {user.display_name}(#{user.public_id}) is going to erase own personal data."
                        }
                    }
                ]
            }
        ]
    })

    test_pap.add_item({
      "description": "Permissions for common department user",
      "target": {
        "resource.type": {"@in": ["exam"]},
        "subject.department": {"!=": None}
      },
      "algorithm": "DENY_UNLESS_PERMIT",
      "rules": [
        {
          "description": "User can access exam list.",
          "effect": "PERMIT",
          "target": {
            "resource.type": "exam",
            "action": {"@in": ["view"]},
            "resource": None
          }
        },
        {
          "description": "User can view exam if he is member of department, that has access to this exam.",
          "effect": "PERMIT",
          "target": {
            "resource.type": "exam",
            "action": {"@in": ["view"]},
            "resource.allowed_departments": {"@contains": {"@": "subject.department"}}
          }
        }
      ]
    })

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


def test_pep1(pdp_instance):
    context = {
        'resource.type': 'user',
        'action': 'create',
        'subject.id': 1
    }
    test_pep = DenyBiasedPEP(pdp_instance)
    assert not test_pep.evaluate(context)


def test_pep2(pdp_instance):
    context = {
        'resource.type': 'user',
        'action': 'create',
        'subject.id': 2
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
        'subject.id': 1
    }
    test_pep = DenyBiasedPEP(pdp_instance)
    assert not test_pep.evaluate(context)


def test_pep4(pdp_instance):
    context = {
        'resource.type': 'user',
        'resource.id': {'@': 'subject.id'},
        'action': 'view',
        'subject.id': 1
    }

    test_pep = DenyBiasedPEP(pdp_instance)
    assert test_pep.evaluate(context, True, debug=True)


def test_pep5(pdp_instance):
    context = {
        'resource.type': 'user',
        'resource.id': 2,
        'action': 'view',
        'subject.id': 1
    }

    test_pep = DenyBiasedPEP(pdp_instance)
    assert not test_pep.evaluate(context, True)


def test_pep6(pdp_instance):
    context = {
        'resource.type': 'user',
        'resource.id': 1,
        'action': 'view',
        'subject.id': 1
    }

    test_pep = DenyBiasedPEP(pdp_instance)
    assert test_pep.evaluate(context, True, debug=True)


def test_pep7(pdp_instance):
    """
    Attempt to update other user by common user
    """
    context = {
        'resource.type': 'user',
        'resource.id': 5,
        'action': 'update',
        'subject.id': 1
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
    assert not test_pep.evaluate(context, True, debug=True)


def test_pip_3(pdp_instance):
    """
    list users
    """
    context = {
        'resource.type': 'user',
        'action': 'view',
        'subject.attribute.roles': None,
        'subject.id': 1,
        'resource.id': None
    }

    test_pep = DenyBiasedPEP(pdp_instance)
    assert not test_pep.evaluate(context, True, debug=True)


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
    'subject': {},
    'subject.department': ['moderators'],
    'action': 'view',
    'resource': 1,
    'resource.type': 'exam',
    'resource.allowed_departments': ['moderators']
    }, True, debug=True)
    assert permit
# EOF
