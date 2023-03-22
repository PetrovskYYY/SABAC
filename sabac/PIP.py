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


class PIP:
    """Policy Information Point"""
    def __init__(self):
        self._information_providers = []
        self._providers_by_provided_attribute = {}

    def evaluate_attribute_value(self, attribute_value, request):
        if len(attribute_value) == 0 or len(attribute_value) > 1:
            # There are more than one key in evaluation expression
            # FixMe: Avoid calculation requests from userspace
            logging.warning(
                'Calculated attributes should have exactly one element, but {element_count} given: {attribute}.'.format(
                    element_count=len(attribute_value),
                    attribute=attribute_value,
                    request=request
                )
            )
            logging.warning(f"Request: {request}")
            import traceback
            traceback.print_stack()
            return None

        if '@' in attribute_value:
            logging.debug(f"Evaluating `{attribute_value['@']}`...")
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

        if isinstance(attribute_value, dict):
            evaluated_attribute_value = self.evaluate_attribute_value(attribute_value, request)
            if evaluated_attribute_value is None:
                logging.warning(f"Found no value while evaluating attribute`{attribute_name}` in request {request}.")
            return evaluated_attribute_value
        else:
            # Value is already constant
            return attribute_value

    def evaluate(self, attribute_name, attribute_value, request):
        context_attribute_value = self.get_attribute_value(attribute_name, request)
        # TODO: Cache value

        if not isinstance(attribute_value, dict):
            # If attribute value is not evaluable we can compare them directly
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
                # If we have a list of values as an argument we check each of them
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
            if isinstance(attribute_value['@in'], list):
                return context_attribute_value in attribute_value['@in']
            if isinstance(attribute_value['@in'], dict):
                calculated_value = self.evaluate_attribute_value(attribute_value['@in'], request)
                if isinstance(calculated_value, list):
                    return context_attribute_value in calculated_value
                else:
                    logging.warning("Expression '{expression}' value ({calculated_value}) is not a list.".format(
                        expression=attribute_value['@in'],
                        calculated_value=calculated_value
                    ))

            logging.warning(
                "Only attribute values of type list (or a expression that is resolving as a list) "
                "could be used with operator @in (%s given for %s).",
                attribute_value['@in'].__class__.__name__,
                attribute_name
            )
            return False
        else:
            logging.warning("Unknown operator '%s'." % attribute_value.keys())
            raise ValueError("Unknown operator '%s'." % attribute_value.keys())

    def add_provider(self, provider: InformationProvider):
        """
        Adds policy information provider
        :param provider:
        :return:
        """
        if not issubclass(provider, InformationProvider):
            raise ValueError("Only subclass of class InformationProvider could be added to PIP.")
        self._information_providers.append(provider)

        # Adding to reversed index
        for provided_attribute in provider.provided_attributes:
            self._providers_by_provided_attribute.setdefault(provided_attribute, []).append(provider)

    def fetch_attribute(self, attribute_name, request):
        """
        Fetches attribute value by given attribute name
        :param attribute_name: Name of an attribute
        :param request: SABAC request object - used for querying sub attributes
        :return: found attribute value of None if attribute not available
        (or error occurred during attribute value resolution)
        """
        # logging.debug(f"Fetching attribute '{attribute_name}'...")
        # Avoiding search for known attributes
        if attribute_name in request.attributes:
            return request.attributes[attribute_name]

        # Attribute is absent in context
        if attribute_name not in self._providers_by_provided_attribute:
            # There is no direct match for this attribute - will try to resolve
            attribute_name_parts = attribute_name.split('.')
            if len(attribute_name_parts) > 1:
                # Attribute is complex - trying to resolve
                return get_object_by_path(request.attributes, attribute_name_parts)
            else:
                # There is no way to get this attribute
                logging.warning("No information providers found for attribute '%s'.", attribute_name)
                logging.warning("Request data '%s'.", request)
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


def get_object_by_path(root_object, path_parts, prefix=None):
    """
    Returns object using provided path and root object.
    Functions treats dict keys and class properties as path parts
    :param root_object: dict or class
    :param path_parts: list of strings
    :param prefix: prefix for path (used internally for recursion)
    :return: Value of object that if found by given path or None if path resolution failed.
    """
    sub_object = None
    if isinstance(root_object, dict) and path_parts[0] in root_object:
        # Object is dict
        sub_object = root_object[path_parts[0]]
    elif hasattr(root_object, path_parts[0]):
        # Object is some class that has required attribute or property
        sub_object = getattr(root_object, path_parts[0])
    else:
        full_attribute_name = path_parts[0]
        if prefix is not None:
            full_attribute_name = f"{prefix}.{path_parts[0]}"
        logging.warning(f"No information providers found for attribute '{full_attribute_name}' "
                        f"for object ({root_object.__class__.__name__}){root_object}.")
        # logging.warning("root_object '%s'.", root_object)
        # import traceback
        # traceback.print_stack()
        return None

    if len(path_parts) == 1:
        # It is a last portion of given path
        return sub_object

    # There is at least one more level in path
    new_prefix = prefix
    if new_prefix is None:
        new_prefix = path_parts[0]
    else:
        new_prefix = f"{new_prefix}.{path_parts[0]}"

    return get_object_by_path(
        root_object=sub_object,
        path_parts=path_parts[1:],
        prefix=new_prefix
    )
# EOF
