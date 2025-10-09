import pytest

from util.query_builder import construct_query, check_input_type


def test_construct_query_simple():
    """
    Test the construction of a simple query with one string filter and one int filter.
    """
    conditions: dict[str] = {
        'team': 'TOR',
        'season': 2025
    }

    result: str = construct_query(table_name='skaters', column_mapping=conditions)

    expected: str = "SELECT * FROM skaters WHERE team = 'TOR' AND season = 2025"

    assert result == expected


def test_construct_query_complex():
    """
    Test the construct of a more complex query with multiple filter values on columns, as well
    as a qualifier.
    """
    conditions: dict[str] = {
        'team': ['TOR', 'MTL', 'OTT'],
        'season': [2024, 2025],
        'situation': ['pk', 'pp']
    }

    qualifiers: dict[str] = {
        'iceTime': '<100'
    }

    result: str = construct_query(table_name='goalies', column_mapping=conditions,
                             qualifiers=qualifiers)

    expected: str = "SELECT * FROM goalies WHERE (team = 'TOR' OR team = 'MTL' OR team = 'OTT') "\
                    "AND (season = 2024 OR season = 2025) "\
                    "AND (situation = 'pk' OR situation = 'pp') "\
                    "AND iceTime <100"

    assert result == expected


def test_check_input_type_singleton_success():
    """
    Test that check_input_type() works as expected with single strings and ints.
    """
    result_str: bool = check_input_type(value='TOR', column_name='team', desired_type=str)
    result_int: bool = check_input_type(value=2024, column_name='season', desired_type=int)

    assert result_str and result_int


def test_check_input_type_singleton_failure():
    """
    Test that check_input_type() raises a ValueError when mismatched singletons are provided.
    """
    with pytest.raises(ValueError):
        check_input_type(value='2024', column_name='season', desired_type=int)


def test_check_input_type_list_success():
    """
    Test that check_input_type() works as expected with lists of strings and ints.
    """
    result_str: bool = check_input_type(value=['TOR', 'MTL', 'OTT'], column_name='team',
                                        desired_type=str)
    result_int: bool = check_input_type(value=[2023, 2024, 2025], column_name='season',
                                        desired_type=int)

    assert result_str and result_int


def test_check_input_type_list_failure():
    """
    Test that check_input_type() fails as expected when given a list with at least one incorrect
    type.
    """
    with pytest.raises(ValueError):
        check_input_type(value=[2023, 2024, '2025'], column_name='season', desired_type=int)
