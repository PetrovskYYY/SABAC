# Test operator_evaluators module
from sabac import (
    calculate_operator_eval,
    equals_operator_eval,
    not_equals_operator_eval,
    contains_operator_eval,
    contained_in_operator_eval,
    uuid_operator_eval,
    not_operator_eval
)
from sabac import Request


class MockPIP:
    """Mock PIP for testing"""
    def get_attribute_value(self, attr, request):
        return request.attributes.get(attr)
    
    def evaluate_statement(self, left_part, right_part, request):
        """Mock evaluate_statement for @not operator."""
        if isinstance(right_part, dict) and len(right_part) == 1:
            key = next(iter(right_part))
            if key == '@in':
                return left_part in right_part[key]
            elif key == '@contains':
                if isinstance(left_part, list):
                    return right_part[key] in left_part
                return False
            elif key == '@not':
                return not self.evaluate_statement(left_part, right_part[key], request)
        return left_part == right_part


def test_calculate_operator_eval_with_string():
    """Test calculate_operator_eval with string operand (attribute name)."""
    pip = MockPIP()
    request = Request(attributes={'attr': 'value', 'other': 'value'})
    # calculate_operator_eval resolves operand as attribute name
    result = calculate_operator_eval(pip, 'attr', 'value', 'other', request)
    assert result == True  # 'value' == request.attributes['other'] == 'value'


def test_calculate_operator_eval_with_none_operand():
    """Test calculate_operator_eval with None operand."""
    pip = MockPIP()
    request = Request(attributes={'attr': 'value'})
    result = calculate_operator_eval(pip, 'attr', 'value', None, request)
    assert result == False  # 'value' is not None


def test_calculate_operator_eval_with_none_attribute():
    """Test calculate_operator_eval when the attribute is None."""
    pip = MockPIP()
    request = Request(attributes={'attr': None})
    result = calculate_operator_eval(pip, 'attr', None, None, request)
    assert result == True  # None is None


def test_equals_operator_eval_with_string():
    """Test equals_operator_eval with string equality."""
    pip = MockPIP()
    request = Request(attributes={'attr': 'test'})
    result = equals_operator_eval(pip, 'attr', 'test', 'test', request)
    assert result == True


def test_equals_operator_eval_with_dict_expression():
    """Test equals_operator_eval with dict expression operand."""
    pip = MockPIP()
    request = Request(attributes={'attr': 'value', 'other': 'value'})
    # Operand is {'@': 'other'} - it should look up 'other' attribute
    result = equals_operator_eval(pip, 'attr', 'value', {'@': 'other'}, request)
    assert result == True  # 'value' == request.attributes['other'] == 'value'


def test_equals_operator_eval_not_equal():
    """Test equals_operator_eval when values are not equal."""
    pip = MockPIP()
    request = Request(attributes={'attr': 'value1'})
    result = equals_operator_eval(pip, 'attr', 'value1', 'value2', request)
    assert result == False


def test_not_equals_operator_eval():
    """Test not_equals_operator_eval with different values."""
    pip = MockPIP()
    request = Request(attributes={'attr': 'value1'})
    result = not_equals_operator_eval(pip, 'attr', 'value1', 'value2', request)
    assert result == True


def test_not_equals_operator_eval_with_none():
    """Test not_equals_operator_eval with None."""
    pip = MockPIP()
    request = Request(attributes={'attr': 'value'})
    result = not_equals_operator_eval(pip, 'attr', 'value', None, request)
    assert result == True  # value is not None


def test_contains_operator_eval():
    """Test contains_operator_eval with a list attribute."""
    pip = MockPIP()
    request = Request(attributes={'attr': [1, 2, 3]})
    result = contains_operator_eval(pip, 'attr', [1, 2, 3], 2, request)
    assert result == True


def test_contains_operator_eval_not_found():
    """Test contains_operator_eval when item not in list."""
    pip = MockPIP()
    request = Request(attributes={'attr': [1, 2, 3]})
    result = contains_operator_eval(pip, 'attr', [1, 2, 3], 4, request)
    assert result == False


def test_contains_operator_eval_with_non_list():
    """Test contains_operator_eval with a non-list attribute."""
    pip = MockPIP()
    request = Request(attributes={'attr': 'not-a-list'})
    result = contains_operator_eval(pip, 'attr', 'not-a-list', 'a', request)
    assert result == False


def test_contains_operator_eval_with_list_operand():
    """Test contains_operator_eval with list operand."""
    pip = MockPIP()
    request = Request(attributes={'attr': [1, 2, 3]})
    result = contains_operator_eval(pip, 'attr', [1, 2, 3], [2, 3], request)
    assert result == True


def test_contained_in_operator_eval():
    """Test contained_in_operator_eval with list operand."""
    pip = MockPIP()
    request = Request(attributes={'attr': 2})
    result = contained_in_operator_eval(pip, 'attr', 2, [1, 2, 3], request)
    assert result == True


def test_contained_in_operator_eval_not_in():
    """Test contained_in_operator_eval when not in the list."""
    pip = MockPIP()
    request = Request(attributes={'attr': 4})
    result = contained_in_operator_eval(pip, 'attr', 4, [1, 2, 3], request)
    assert result == False


def test_uuid_operator_eval_with_valid_string():
    """Test uuid_operator_eval with a valid UUID string as operand."""
    pip = MockPIP()
    request = Request(attributes={'attr': 'value'})
    # uuid_operator_eval expects operand to be a UUID string
    result = uuid_operator_eval(pip, 'attr', None, '12345678-1234-5678-1234-567812345678', request)
    from uuid import UUID
    assert isinstance(result, UUID)


def test_uuid_operator_eval_with_invalid_string():
    """Test uuid_operator_eval with an invalid UUID string raises ValueError."""
    pip = MockPIP()
    request = Request(attributes={'attr': 'value'})
    # uuid_operator_eval does not catch exceptions - it lets ValueError propagate
    try:
        uuid_operator_eval(pip, 'attr', None, 'invalid-uuid', request)
        assert False, "Expected ValueError"
    except ValueError:
        pass  # Expected


def test_not_operator_eval_with_dict():
    """Test not_operator_eval with a dict expression."""
    pip = MockPIP()
    request = Request(attributes={'attr': True})
    # {'@in': [1, 2, 3]} - checking if attr is in list
    result = not_operator_eval(pip, 'attr', True, {'@in': [1, 2, 3]}, request)
    assert result == True  # True is not in [1, 2, 3]


def test_not_operator_eval_with_string():
    """Test not_operator_eval with string operand."""
    pip = MockPIP()
    request = Request(attributes={'attr': 'value1'})
    result = not_operator_eval(pip, 'attr', 'value1', 'value2', request)
    assert result == True  # 'value1' != 'value2'
