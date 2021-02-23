#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Policy Information Point
Responsible for providing information that was not provided in original request.
Information could be gained from:
- environment
- infection of existing request attributes
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
import logging


class PIP:
    """Policy Information Point"""
    def __init__(self):
        self._information_providers = []
        self._providers_by_provided_attribute = {}

    def evaluate_attribute_value(self, attribute_value, request):
        if len(attribute_value) == 0 or len(attribute_value) > 1:
            # There are more than one key in evaluation expression
            raise ValueError('Calculated attributes should have only one element. %d given: %s.' % (
                len(attribute_value),
                attribute_value
            ))

        if '@' in attribute_value:
            # Extracting value by name
            if attribute_value['@'] in request.attributes:
                return request.attributes[attribute_value['@']]
            else:
                return self.get_attribute_value(attribute_value['@'], request)
        else:
            logging.warning("Unknown operator '%s'." % attribute_value)
            raise ValueError("Unknown operator '%s'." % attribute_value)

    def get_attribute_value(self, attribute_name, request):
        attribute_value = self.fetch_attribute(attribute_name, request)

        if not isinstance(attribute_value, dict):
            # Value is already constant
            return attribute_value

        return self.evaluate_attribute_value(attribute_value, request)

    def evaluate(self, attribute_name, attribute_value, request):
        context_attribute_value = self.get_attribute_value(attribute_name, request)
        # TODO: Cache value

        if not isinstance(attribute_value, dict):
            return context_attribute_value == attribute_value

        if len(attribute_value) > 1:
            # There are more than one key in evaluation expression
            raise ValueError('Calculated attributes should have only one element. %d given: %s.' % (
                len(attribute_value),
                attribute_value
            ))

        # if '@' in attribute_value:
        #     operand = attribute_value['@']
        #     if isinstance(operand, str):
        #         extracted_attribute_value = self.get_attribute_value(operand, request)
        #         return context_attribute_value == extracted_attribute_value
        #     elif operand is None:
        #         return context_attribute_value is None
        #     else:
        #         logging.warning("Only attributes of type string (or None) could be used with operator @ (%s given).",
        #                         operand.__class__.__name__)

        elif '==' in attribute_value:
            operand = attribute_value['==']
            if isinstance(operand, str):
                extracted_attribute_value = self.get_attribute_value(operand, request)
                return context_attribute_value == extracted_attribute_value
            elif operand is None:
                return context_attribute_value is None
            else:
                logging.warning("Only attributes of type string (or None) could be used with operator == (%s given).",
                                operand.__class__.__name__)

        elif '!=' in attribute_value:
            operand = attribute_value['!=']
            if isinstance(operand, str):
                extracted_attribute_value = self.get_attribute_value(operand, request)
                return context_attribute_value != extracted_attribute_value
            elif operand is None:
                return context_attribute_value is not None
            else:
                logging.warning("Only attributes of type string (or None) could be used with operator != (%s given).",
                                operand.__class__.__name__)

        elif '@contains' in attribute_value:
            if context_attribute_value is None:
                return False
            if not isinstance(context_attribute_value, list):
                logging.warning(
                    "Only attributes of type list could be used with operator @contains (got %s for attribute %s).",
                    context_attribute_value.__class__.__name__,
                    attribute_name
                )
                return False
            if isinstance(attribute_value['@contains'], list):
                # If we have a list of values we check each of them
                for item in attribute_value['@contains']:
                    if item in context_attribute_value:
                        return True
                # If none matches
                return False
            if isinstance(attribute_value['@contains'], dict):
                # Attribute value should be calculated first
                calculated_attribute_value = self.evaluate_attribute_value(attribute_value['@contains'], request)

                if isinstance(calculated_attribute_value, list):
                    intersection = list(set(calculated_attribute_value) & set(context_attribute_value))
                    return len(intersection) > 0  # if lists intersect then value is true
                else:
                    return calculated_attribute_value in context_attribute_value
            else:
                return attribute_value['@contains'] in context_attribute_value
        elif '@in' in attribute_value:
            if not isinstance(attribute_value['@in'], list):
                logging.warning("Only attribute values of type list could be used with operator @in (%s given for %s).",
                                attribute_value['@in'].__class__.__name__, attribute_name)
                return False
            return context_attribute_value in attribute_value['@in']
        else:
            logging.warning("Unknown operator '%s'." % attribute_value.keys())
            raise ValueError("Unknown operator '%s'." % attribute_value.keys())

    def add_provider(self, provider):
        if not issubclass(provider, InformationProvider):
            raise ValueError("Only subclass of class InformationProvider could be added to PIP.")
        self._information_providers.append(provider)

        # Adding to reversed index
        for provided_attribute in provider.provided_attributes:
            self._providers_by_provided_attribute.setdefault(provided_attribute, []).append(provider)

    def fetch_attribute(self, attribute_name, request):
        # Avoiding search for known attributes
        if attribute_name in request.attributes:
            return request.attributes[attribute_name]

        # Attribute is absent in context
        if attribute_name not in self._providers_by_provided_attribute:
            # There is no way to get this attribute
            logging.warning("No information providers found for attribute '%s'.", attribute_name)
            return None

        for provider in self._providers_by_provided_attribute[attribute_name]:
            for required_attribute in provider.required_attributes:
                if required_attribute not in request.attributes:
                    # Setting placeholder in request to avoid loop searches
                    request.attributes[required_attribute] = None
                    # Searching for required attribute
                    request.attributes[required_attribute] = self.fetch_attribute(required_attribute, request)
            # Now all required attributes should be present in context
            result = provider.fetch(request)
            if result is not None:
                return result


class InformationProvider:
    """
    Base class for information providers
    """

    @classmethod
    def fetch(cls, request):
        return cls.fetch_value(request.attributes)

    @classmethod
    def fetch_value(cls, request):
        raise NotImplementedError()
# EOF
