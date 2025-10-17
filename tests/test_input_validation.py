import pytest

from util.input_validation import check_input_values, check_input_type


def test_check_valid_inputs_singleton_success():
    """
    Checks to see that valid singleton inputs do not raise any errors.
    """
    test_inputs: dict[str] = {
        'season': 2024,
        'team': 'TOR',
        'situation': '5on5'
    }

    result: bool = check_input_values(test_inputs)

    assert result


def test_check_valid_inputs_list_success():
    """
    Checks to see that valid list inputs do not raise any errors.
    """
    test_inputs: dict[str] = {
        'season': [2023, 2024, 2025],
        'team': ['TOR', 'MTL', 'OTT'],
        'situation': '5on5'
    }

    result: bool = check_input_values(test_inputs)

    assert result


def test_check_valid_inputs_singleton_failure():
    """
    Checks to see that invalid singleton inputs raise errors as expected
    """
    test_inputs: dict[str] = {
        'season': 1999,
        'team': ['TOR', 'MTL', 'OTT'],
        'situation': '5on5'
    }

    with pytest.raises(ValueError):
        check_input_values(test_inputs)


def test_check_valid_inputs_list_failure():
    """
    Checks to see that invalid list inputs raise errors as expected
    """
    test_inputs: dict[str] = {
        'season': 2024,
        'team': ['TOR', 'FOO', 'OTT', 'BAR'],
        'situation': '5on5'
    }

    with pytest.raises(ValueError):
        check_input_values(test_inputs)


def test_check_input_type_singleton_success():
    """
    Test that check_input_type() works as expected with single strings and ints.
    """
    test_inputs: dict[str] = {
        'season': 2024,
        'team': 'TOR',
        'situation': '5on5'
    }

    result: bool = check_input_type(column_mapping=test_inputs)

    assert result


def test_check_input_type_singleton_failure():
    """
    Test that check_input_type() raises a ValueError when mismatched singletons are provided.
    """
    test_inputs: dict[str] = {
        'season': '2024',
        'team': 'TOR',
        'situation': '5on5'
    }

    with pytest.raises(ValueError):
        check_input_type(test_inputs)


def test_check_input_type_list_success():
    """
    Test that check_input_type() works as expected with lists of strings and ints.
    """
    test_inputs: dict[str] = {
        'season': [2023, 2024, 2025],
        'team': ['TOR', 'MTL', 'OTT'],
        'situation': '5on5'
    }

    result: bool = check_input_type(test_inputs)

    assert result


def test_check_input_type_list_failure():
    """
    Test that check_input_type() fails as expected when given a list with at least one incorrect
    type.
    """
    test_inputs: dict[str] = {
        'team': ['TOR', 'MTL', 'OTT'],
        'situation': '5on5',
        'season': [2023, 2024, '2025']
    }

    with pytest.raises(ValueError):
        check_input_type(test_inputs)
