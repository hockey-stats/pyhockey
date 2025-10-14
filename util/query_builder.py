"""
Module used to construct SQL queries that will be used to query the database.

Instead of each individual module building the queries based on their provided inputs,
use this module to manage this task in a central location.

When each of the primary modules are called, they will call a function here, and using
the provided parameters, an SQL query string will be constructed and returned.
"""

import datetime

# A mapping of column names in the database to the expected types of the values in those columns
COLUMN_SCHEMA = {
    'name': str,
    'gameID': int,
    'gameDate': datetime.date,
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


def construct_query(table_name: str,
                    column_mapping: dict[str],
                    qualifiers: dict[str] = None) -> str:
    """
    Method that takes parameters passed into the primary functions and constructs an
    SQL query that can be used to query the data.

    :param str table_name: The name of the table being queried.
    :param dict[str] column_mapping: A dict mapping column names in the table to values they
                                     need to be evaluated against. Multiple values can be provided
                                     in a list and all will be combined in an 'OR' statement.
    :param dict[str] qualifiers: A dict mapping certain column names to evaluations which will be
                                 applied to the query, e.g. '<' or '>' conditions, defaults to None.

    :return str: The full query provided as a string.
    """

    query: str = f"SELECT * FROM {table_name} WHERE "

    query_conditions: list[str] = []
    for column_name, value in column_mapping.items():
        # The keys of the column_mapping dict will be strings corresponding to the column
        # names in the table, whereas the values will be filters applied to those columns.
        # These values can be of multiple types, and can also potentially be a list of items.

        # This condition will raise an error if mis-matched types were provided.
        if check_input_type(value, column_name, COLUMN_SCHEMA[column_name]):
            pass

        if isinstance(value, list):
            if isinstance(value[0], str):
                # Add single quotes to value if dealing with strings
                condition: str = " OR ".join(f"{column_name} = '{v}'" for v in value)
            else:
                condition: str = " OR ".join(f"{column_name} = {v}" for v in value)

            # Make sure the 'OR' conditions are bracketed
            condition = f"({condition})"

        # If we're dealing with a singleton and not a list...
        else:
            # Add single quotes to value if dealing with strings
            if isinstance(value, str):
                condition: str = f"{column_name} = '{value}'"
            else:
                condition: str = f"{column_name} = {value}"

        query_conditions.append(condition)

    if qualifiers:
        # Qualifiers will be provided in a dict in a format, e.g.,
        #   'iceTime': '>100',
        # to indicate that the query should filter for entries with iceTime > 100.

        for column_name, value in qualifiers.items():
            query_conditions.append(f"{column_name} {value}")

    all_conditions: str = " AND ".join(query_conditions)

    query += all_conditions

    return query


def check_input_type(value: str | int | list[int] | list[str],
                     column_name: str,
                     desired_type: type) -> bool:
    """
    Validates the types provided to the primary functions to make sure they align with
    database expectations when building the query.

    :param str | int | list[int] | list[str] value: The input value being provided. Since the
                                                    type of this is what's being checked, it can
                                                    be of any type that a user may provide, as well
                                                    as lists of that type.
    :param str column_name: The column name in the database that the value is filtering against.
    :param type desired_type: The type that the database will expect the value to be.

    :raises ValueError: This function will raise a ValueError, ending the program, if a mismatched
                        type for the value is provided.

    :return bool: If no error is raised, the function will return True.
    """

    # First make sure values that were supplied are the correct types.
    if not isinstance(value, desired_type):
        if isinstance(value, list):
            for v in value:
                if not isinstance(v, desired_type):
                    raise ValueError(f"ERROR: Values provided for {column_name} must be "\
                                     f"{desired_type}, received {type(v)}: {v}")
        else:
            raise ValueError(f"ERROR: Values provided for {column_name} must be "\
                                f"{desired_type}, received {type(value)}: {value}")

    return True
