"""
Module for checking that provided inputs are of the correct type as expected by the database 
schema, and also checking that the values provided are valid in the context of what the
database expects (i.e. using the proper team acronyms and seasons for which data is
available).
"""

import datetime

### CONSTANTS #####################################################################################

# The valid values accepted for each column
VALID_SITUATIONS = ['all', '5on5', '4on5', '5on4', 'other']

VALID_SEASONS = list(range(2008, 2026))

VALID_TEAMS = ['ANA', 'ARI', 'ATL', 'BOS', 'BUF', 'CAR', 'CBJ', 'CGY', 'CHI', 'COL', 'DAL', 'DET',
               'EDM', 'FLA', 'L.A', 'LAK', 'MIN', 'MTL', 'N.J', 'NJD', 'NSH', 'NYI', 'NYR', 'OTT',
               'PHI', 'PIT', 'S.J', 'SEA', 'SJS', 'STL', 'T.B', 'TBL', 'TOR', 'UTA', 'VAN', 'VGK',
               'WPG', 'WSH',]

VALID_INPUT_VALUES = {
    'season': VALID_SEASONS,
    'team': VALID_TEAMS,
    'situation': VALID_SITUATIONS
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


def check_input_values(column_mapping: dict[str]) -> bool:
    """
    Function to determine if the input values provided by a user are valid in the context of the
    tables being queried, e.g. make sure whatever season value is provided fits within the range
    of seasons which have available data.

    If inputs are found to contain any invalid values, raise a ValueError with details on what the
    valid inputs are.

    :param dict[str] column_mapping: A mapping of the columns to check with their provided inputs

    :raises ValueError: This function will raise a ValueError, ending the program, if an invalid
                        value is provided.

    :return bool: Returns True if no ValueError is raised
    """

    for column, input_value in column_mapping.items():

        valid_inputs: list[str | int] = VALID_INPUT_VALUES[column]

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
    """
    Validates the types provided to the primary functions to make sure they align with
    database expectations when building the query.

    :param dict[str] column_mapping: A mapping of the columns to check with their provided inputs

    :raises ValueError: This function will raise a ValueError, ending the program, if a mismatched
                        type for the value is provided.

    :return bool: If no error is raised, the function will return True.
    """

    for column_name, value in column_mapping.items():
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
