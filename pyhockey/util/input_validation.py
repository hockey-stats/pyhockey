"""
Module for checking that provided inputs are of the correct type as expected by the database 
schema, and also checking that the values provided are valid in the context of what the
database expects (i.e. using the proper team acronyms and seasons for which data is
available).
"""

import datetime
from datetime import datetime


# Define custom type for inputs into our queries
type QueryValue = str | int | float | list[str] | list[int] | list[float]


### CONSTANTS #####################################################################################

# The valid values accepted for each column
VALID_SITUATIONS = ['all', '5on5', '4on5', '5on4', 'other']

VALID_SEASONS = list(range(2008, 2026))

VALID_TEAMS = ['ANA', 'ARI', 'ATL', 'BOS', 'BUF', 'CAR', 'CBJ', 'CGY', 'CHI', 'COL', 'DAL', 'DET',
               'EDM', 'FLA', 'L.A', 'LAK', 'MIN', 'MTL', 'N.J', 'NJD', 'NSH', 'NYI', 'NYR', 'OTT',
               'PHI', 'PIT', 'S.J', 'SEA', 'SJS', 'STL', 'T.B', 'TBL', 'TOR', 'UTA', 'VAN', 'VGK',
               'WPG', 'WSH', 'ALL']

VALID_INPUT_VALUES_MONEYPUCK = {
    'season': VALID_SEASONS,
    'team': VALID_TEAMS,
    'situation': VALID_SITUATIONS
}

VALID_INPUT_VALUES_NST = {
    'season': VALID_SEASONS,
    'team': VALID_TEAMS,
    'situation': ['ev', 'pp', 'pk', 'all']
}

# A mapping of column names in the database to the expected types of the values in those columns
COLUMN_SCHEMA = {
    'name': str,
    'gameID': int,
    'gameDate': str,
    'season': int,
    'team': str,
    'state': str,
    'situation': str,
    'iceTime': (int, float),
    'shotsAgainst': int,
    'goalsAgainst': int,
    'xGoalsAgainst': (int, float),
    'gamesPlayed': int,
    'xGoals': (int, float),
    'goals': int,
    'lowDangerShots': int,
    'mediumDangerShots': int,
    'highDangerShots': int,
    'lowDangerxGoals': (int, float),
    'mediumDangerxGoals': (int, float),
    'highDangerxGoals': (int, float),
    'lowDangerGoals': int,
    'mediumDangerGoals': int,
    'highDangerGoals': int,
    'position': str,
    'primaryAssists': int,
    'secondaryAssists': int,
    'shots': int,
    'individualxGoals': (int, float),
    'goalsFor': int,
    'xGoalsFor': (int, float),
    'xGoalsShare': (int, float),
    'corsiFor': int,
    'corsiAgainst': int,
    'corsiShare': (int, float),
    'xGoalsForPerHour': (int, float),
    'xGoalsAgainstPerHour': (int, float),
    'goalsForPerHour': (int, float),
    'goalsAgainstPerHour': (int, float),
    'pointsPerHour': (int, float),
    'goalsPerHour': (int, float),
    'averageIceTime': (int, float),
    'corsiPercentage': (int, float),
}
### END CONSTANTS #################################################################################


def check_input_values(column_mapping: dict[str], table: str) -> bool:
    """ Checks that provided inputs use valid values.

    Function to determine if the input values provided by a user are valid in the context of the
    tables being queried, e.g. make sure whatever season value is provided fits within the range
    of seasons which have available data.

    If inputs are found to contain any invalid values, raise a ValueError with details on what the
    valid inputs are.

    Args:

        column_mapping: 
            A mapping of the columns to check with their provided inputs
        table: 
            Name of the table being queried, as depending on the source, some expect different
            values.

    Returns:

        Returns True if no ValueError is raised

    Raises:

        ValueError: An input of either incorrect value or type was provided.
    """

    if table in {'skaters', 'goalies', 'teams', 'team_games'}:
        value_map = VALID_INPUT_VALUES_MONEYPUCK
    else:
        value_map = VALID_INPUT_VALUES_NST

    for column, input_value in column_mapping.items():

        # Default value for most columns is None, so skip those
        if input_value is None:
            continue

        if not value_map.get(column, False):
            # Some columns don't need to have their inputs validated (e.g. names)
            continue

        valid_inputs: list[str | int] = value_map[column]

        # If input_value is a singleton check that it's in the list of valid inputs, but
        # if input_value is a list check that it is a subset
        if (not isinstance(input_value, list) and input_value not in valid_inputs) or \
           (isinstance(input_value, list) and not set(input_value).issubset(valid_inputs)):

            # If valid_inputs does not contain input_value, construct the error message and
            # raise the error
            msg: str = f"Invalid input '{input_value}' provided for {column}.\n"\
                       f"Valid inputs are {valid_inputs}"

            raise ValueError(msg)

    return True


def check_input_type(column_mapping: dict[str]) -> bool:
    """ Checks that provided inputs are of the valid type.

    Validates the types provided to the primary functions to make sure they align with
    database expectations when building the query.

    Args:

        column_mapping: 
            A mapping of the columns to check with their provided inputs

    Returns:

        If no error is raised, the function will return True.

    Raises:

        ValueError: 
            This function will raise a ValueError, ending the program, if a mismatched type for
            the value is provided.

    """

    for column_name, value in column_mapping.items():

        # Default value for most columns is None, so skip those
        if value is None:
            continue

        desired_type = COLUMN_SCHEMA[column_name]
        # First make sure values that were supplied are the correct types.
        if not isinstance(value, desired_type):
            if isinstance(value, list):
                for v in value:
                    if not isinstance(v, desired_type):
                        raise ValueError(f"Values provided for {column_name} must be "\
                                         f"{desired_type}, received {type(v)}: {v}")
            else:
                raise ValueError(f"Values provided for {column_name} must be "\
                                 f"{desired_type}, received {type(value)}: {value}")

    return True


def validate_date_range(column_mapping: dict[str, QueryValue],
                        qualifiers: dict[str, str]) -> dict[str, QueryValue]:
    """ Checks that date inputs are valid.

    Function to check any date inputs (e.g. 'start_date', 'end_date') where given in the
    expected format, and to make sure there are no conflicts between these inputs and the
    'season' input.

    Args:

        column_mapping: 
            The column mapping provided for the query.
        qualifiers: 
            The qualifiers provided for the query.

    Returns:

        An updated version of the column mapping.

    Raises:
    
        Raises a ValueError if a date value was provided in a format that isn't YYYY-MM-DD,
        or if end_date is not after start_date.

    """

    # First checks that both 'start_date' and 'end_date', if provided, match the YYYY-MM-DD format
    # using datetime.strptime().
    for date in ['start_date', 'end_date']:
        if date in qualifiers.keys():
            date_string: str = qualifiers[date]
            try:
                datetime.strptime(date_string, '%Y-%m-%d')
            except ValueError as e:
                raise ValueError(f"'{date}' provided in unsupported format. Must be YYYY-MM-DD. "\
                                 f"Recieved {date_string}.") from e

    # Check that, if both start_date and end_date were provided, that start_date comes before
    # end_date
    if qualifiers.get('end_date', False) and qualifiers.get('start_date', False):
        start = datetime.strptime(qualifiers['start_date'], '%Y-%m-%d')
        end = datetime.strptime(qualifiers['end_date'], '%Y-%m-%d')
        if end < start:
            raise ValueError(f"Provided end date ({qualifiers['end_date']}) comes before "\
                             f"provided start date ({qualifiers['start_date']}). Start date "\
                              "must be before or equal to end date.")

    # Then, if both 'start_date' and 'end_date' were provided in addition to 'season', remove
    # 'season' from the column_mapping and print the reason why.
    if column_mapping.get('season', False) and qualifiers.get('start_date', False) and \
        qualifiers.get('end_date', False):
        print("Input values were provided for 'start_date', 'end_date', and 'season'. "\
              "Disregarding the input for 'season' and returning all games between "\
              f"{qualifiers['start_date']} and {qualifiers['end_date']}.")

        del column_mapping['season']

    return column_mapping
