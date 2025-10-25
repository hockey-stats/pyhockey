import pytest

from pyhockey.util.input_validation import check_input_type, check_input_values, \
validate_date_range


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


def test_date_range_validation_start_and_end():
    """
    Test that validate_date_range() works as expected when both a start_date and end_date are
    provided.
    """
    column_mapping = {
        'season': 2025,
        'situation': 'all'
    }

    qualifiers = {
        'start_date': '2025-10-10',
        'end_date': '2025-10-30'
    }

    expected = {
        'situation': 'all'
    }

    result = validate_date_range(column_mapping=column_mapping, qualifiers=qualifiers)

    assert result == expected
   

def test_date_range_validation_start_and_season():
    """
    Test that validate_date_range() works as expected when just a start_date is provided in
    addition to a season.
    """
    column_mapping = {
        'season': 2025,
        'situation': 'all'
    }

    qualifiers = {
        'start_date': '2025-10-10',
    }

    result = validate_date_range(column_mapping=column_mapping, qualifiers=qualifiers)

    assert result == column_mapping


def test_date_range_validation_raises_error_on_bad_date_format():
    """
    Test that validate_date_range() raises a ValueError when a date range in an incorrect
    format is provided.
    """
    column_mapping = {
        'season': 2025,
        'situation': 'all'
    }

    qualifiers = {
        'start_date': '10-10-2025',
        'end_date': '2025-10-30'
    }

    with pytest.raises(ValueError):
        validate_date_range(column_mapping=column_mapping, qualifiers=qualifiers)


def test_date_range_validation_raises_error_on_end_before_start():
    """
    Test that validate_date_range() raises a ValueError when an end_date that comes before the
    start_date is provided
    """
    column_mapping = {
        'season': 2025,
        'situation': 'all'
    }

    qualifiers = {
        'start_date': '2025-10-30',
        'end_date': '2024-10-30'
    }

    with pytest.raises(ValueError):
        validate_date_range(column_mapping=column_mapping, qualifiers=qualifiers)
