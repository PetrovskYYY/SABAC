# Test expression_evaluators module
import pytest
from sabac import evaluate_expression, uuid_evaluator, str_evaluator
from sabac import PIP, Request


class MockPIP:
    """Mock PIP for testing - simulates PIP.get_attribute_value"""
    def get_attribute_value(self, attr, request):
        if isinstance(attr, str):
            return request.attributes.get(attr)
        return None
    
    def evaluate_expression(self, expression, request):
        """Simulate PIP.evaluate_expression for dict expressions."""
        if isinstance(expression, dict) and len(expression) == 1:
            key = next(iter(expression))
            if key == '@':
                return self.get_attribute_value(expression[key], request)
            elif key == '@UUID':
                return uuid_evaluator(self, expression[key], request)
            elif key == '@STR':
                return str_evaluator(self, expression[key], request)
        return expression


def test_evaluate_expression_with_string():
    """Test evaluate_expression with string (attribute name)."""
    pip = MockPIP()
    request = Request(attributes={'test': 'value'})
    result = evaluate_expression(pip, 'test', request)
    assert result == 'value'


def test_evaluate_expression_with_missing_attribute():
    """Test evaluate_expression with missing attribute."""
    pip = MockPIP()
    request = Request(attributes={'test': 'value'})
    result = evaluate_expression(pip, 'missing', request)
    assert result is None


def test_evaluate_expression_with_none():
    """Test evaluate_expression with None attribute."""
    pip = MockPIP()
    request = Request(attributes={'test': None})
    result = evaluate_expression(pip, 'test', request)
    assert result is None


def test_uuid_evaluator_with_valid_uuid_string():
    """Test uuid_evaluator with valid UUID string."""
    pip = MockPIP()
    request = Request(attributes={'dummy': 'value'})
    result = uuid_evaluator(pip, '12345678-1234-5678-1234-567812345678', request)
    from uuid import UUID
    assert isinstance(result, UUID)


def test_uuid_evaluator_with_invalid_string():
    """Test uuid_evaluator with invalid UUID string."""
    pip = MockPIP()
    request = Request(attributes={'dummy': 'value'})
    result = uuid_evaluator(pip, 'invalid-uuid', request)
    assert result is None


def test_uuid_evaluator_with_list_of_uuids():
    """Test uuid_evaluator with list of UUID strings."""
    pip = MockPIP()
    request = Request(attributes={'dummy': 'value'})
    result = uuid_evaluator(pip, ['12345678-1234-5678-1234-567812345678', '87654321-4321-8765-4321-210987654321'], request)
    from uuid import UUID
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(u, UUID) for u in result)


def test_uuid_evaluator_with_expression():
    """Test uuid_evaluator with dict expression."""
    pip = MockPIP()
    request = Request(attributes={'id': '12345678-1234-5678-1234-567812345678'})
    result = uuid_evaluator(pip, {'@': 'id'}, request)
    from uuid import UUID
    assert isinstance(result, UUID)


def test_uuid_evaluator_with_invalid_expression():
    """Test uuid_evaluator with expression that returns invalid UUID."""
    pip = MockPIP()
    request = Request(attributes={'id': 'invalid-uuid'})
    result = uuid_evaluator(pip, {'@': 'id'}, request)
    assert result is None


def test_str_evaluator_with_string():
    """Test str_evaluator with string input."""
    pip = MockPIP()
    request = Request(attributes={'dummy': 'value'})
    result = str_evaluator(pip, 12345, request)
    assert result == '12345'


def test_str_evaluator_with_none():
    """Test str_evaluator with None input."""
    pip = MockPIP()
    request = Request(attributes={'dummy': 'value'})
    result = str_evaluator(pip, None, request)
    assert result == 'None'


def test_str_evaluator_with_complex_object():
    """Test str_evaluator with complex object."""
    pip = MockPIP()
    request = Request(attributes={'dummy': 'value'})
    result = str_evaluator(pip, {'key': 'value'}, request)
    assert isinstance(result, str)


def test_pip_evaluate_expression_with_at_sign():
    """Test PIP.evaluate_expression with {'@': 'attr'} expression."""
    pip = PIP()
    request = Request(attributes={'test': 'value'})
    result = pip.evaluate_expression({'@': 'test'}, request)
    assert result == 'value'


def test_pip_evaluate_expression_with_uuid_string():
    """Test PIP.evaluate_expression with {'@UUID': 'uuid-string'} expression."""
    pip = PIP()
    request = Request(attributes={'dummy': 'value'})
    result = pip.evaluate_expression({'@UUID': '12345678-1234-5678-1234-567812345678'}, request)
    from uuid import UUID
    assert isinstance(result, UUID)


def test_pip_evaluate_expression_with_uuid_and_at():
    """Test PIP.evaluate_expression with {'@UUID': {'@': 'id'}} expression."""
    pip = PIP()
    request = Request(attributes={'id': '12345678-1234-5678-1234-567812345678'})
    result = pip.evaluate_expression({'@UUID': {'@': 'id'}}, request)
    from uuid import UUID
    assert isinstance(result, UUID)


def test_pip_evaluate_expression_with_str():
    """Test PIP.evaluate_expression with {'@STR': value} expression."""
    pip = PIP()
    request = Request(attributes={'dummy': 'value'})
    result = pip.evaluate_expression({'@STR': 12345}, request)
    assert result == '12345'


def test_pip_evaluate_expression_with_str_and_at():
    """Test PIP.evaluate_expression with {'@STR': {'@': 'num'}} expression.
    
    Note: str_evaluator doesn't evaluate expressions - it converts directly to string.
    So {'@STR': {'@': 'num'}} will convert the dict to string, not evaluate it.
    """
    pip = PIP()
    request = Request(attributes={'num': 12345})
    result = pip.evaluate_expression({'@STR': {'@': 'num'}}, request)
    # str_evaluator just does str(expression), so it converts the dict to string
    assert isinstance(result, str)
    assert "'@'" in result or '"@"' in result
