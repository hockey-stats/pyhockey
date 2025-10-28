import pytest

from pyhockey.util.query_builder import construct_query, handle_names


def test_construct_query_simple():
    """
    Test the construction of a simple query with one string filter and one int filter.
    """
    conditions: dict[str] = {
        'team': 'TOR',
        'season': 2025,
        'situation': '5on5'
    }

    result: str = construct_query(table_name='skaters', column_mapping=conditions)

    expected: str = "SELECT * FROM skaters WHERE team = 'TOR' AND season = 2025 AND "\
                    "situation = '5on5'"

    assert result == expected


def test_construct_query_complex():
    """
    Test the construct of a more complex query with multiple filter values on columns, as well
    as a qualifier.
    """
    conditions: dict[str] = {
        'team': ['TOR', 'MTL', 'OTT'],
        'season': [2024, 2025],
        'situation': ['all', '5on5'],
        'name': ['Stolarz', 'Sam Montembault']
    }

    qualifiers: dict[str] = {
        'iceTime': '<100'
    }

    result: str = construct_query(table_name='goalies', column_mapping=conditions,
                                  qualifiers=qualifiers, order_by=['team', 'season'])

    expected: str = "SELECT * FROM goalies WHERE "\
                    "iceTime <100 "\
                    "AND (team = 'TOR' OR team = 'MTL' OR team = 'OTT') "\
                    "AND (season = 2024 OR season = 2025) "\
                    "AND (situation = 'all' OR situation = '5on5') "\
                    "AND (name LIKE '%Stolarz%' OR name LIKE '%Sam%Montembault%') "\
                    "ORDER BY team, season"

    assert result == expected


def test_construct_query_fails_with_bad_input_type():
    """
    That that construct_query() raises a ValueError if given a column mapping with mis-matched
    input types.
    """
    conditions: dict[str] = {
        'team': 'TOR',
        'season': '2025'
    }

    with pytest.raises(ValueError):
        construct_query(table_name='skaters', column_mapping=conditions)


def test_construct_query_with_date_range():
    """
    Test that construct_query() works as expected when providing date ranges.
    """
    conditions: dict[str] = {
        'team': 'TOR',
        'season': [2024],
        'situation': ['all', '5on5'],
    }

    qualifiers: dict[str] = {
        'start_date': '2024-10-30',
        'end_date': '2025-03-25'
    }

    result: str = construct_query(table_name='team_games', column_mapping=conditions,
                                  qualifiers=qualifiers, order_by=['team', 'gameDate'])

    expected: str = "SELECT * FROM team_games WHERE "\
                    "gameDate >= '2024-10-30' "\
                    "AND gameDate <= '2025-03-25' "\
                    "AND team = 'TOR' "\
                    "AND (situation = 'all' OR situation = '5on5') "\
                    "ORDER BY team, gameDate"

    assert result == expected


def test_handle_names_singleton():
    """
    Test that handle_names works as expected when a single name is provided, either a full
    name or just a last name.
    """
    condition: str = handle_names('Matthews')
    assert condition == "name LIKE '%Matthews%'"

    condition_b: str = handle_names('Auston Matthews')
    assert condition_b == "name LIKE '%Auston%Matthews%'"


def test_handle_names_list():
    """
    Test that handle_names works as expected when a list of names is provided.
    """
    condition: str = handle_names(['Matthews', 'William Nylander'])
    assert condition == "(name LIKE '%Matthews%' OR name LIKE '%William%Nylander%')"
