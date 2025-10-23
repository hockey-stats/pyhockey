"""
Module used to construct SQL queries that will be used to query the database.

Instead of each individual module building the queries based on their provided inputs,
use this module to manage this task in a central location.

When each of the primary modules are called, they will call a function here, and using
the provided parameters, an SQL query string will be constructed and returned.
"""
from datetime import datetime

from pyhockey.util.input_validation import check_input_type, check_input_values

# Define custom type for inputs into our queries
type QueryValue = str | int | float | list[str] | list[int] | list[float]


def construct_query(table_name: str,
                    column_mapping: dict[str, QueryValue],
                    qualifiers: dict[str, str] | None = None,
                    order_by: list[str] | None = None) -> str:
    """
    Method that takes parameters passed into the primary functions and constructs an
    SQL query that can be used to query the data.

    :param str table_name: The name of the table being queried.
    :param dict[str, QueryValue] column_mapping: A dict mapping column names in the table to values
                                                 they need to be evaluated against. Multiple values
                                                 can be provided in a list and all will be combined
                                                 in an 'OR' statement.
    :param dict[str, str] qualifiers: A dict mapping certain column names to evaluations which will
                                      be applied to the query, e.g. '<' or '>' conditions, defaults
                                      to None.
    :param list[str] order_by: A list of strings corresponding to column names that the results
                               will be sorted by.

    :return str: The full query provided as a string.
    """

    # This condition will raise an error if mis-matched types or invalid values were provided
    if check_input_type(column_mapping=column_mapping) and \
       check_input_values(column_mapping=column_mapping):
        pass

    query: str = f"SELECT * FROM {table_name} WHERE "

    query_conditions: list[str] = []
    for column_name, value in column_mapping.items():
        # The keys of the column_mapping dict will be strings corresponding to the column
        # names in the table, whereas the values will be filters applied to those columns.
        # These values can be of multiple types, and can also potentially be a list of items.
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

        # When dealing with date ranges, some additional checks are necessary
        if 'start_date' in qualifiers.keys() or 'end_date' in qualifiers.keys():
            column_mapping = validate_date_range_inputs(column_mapping, qualifiers)

        for column_name, value in qualifiers.items():
            # 'start_date' and 'end_date' need slightly special handling, as they don't
            # correspond to actual table columns
            if column_name == 'start_date':
                query_conditions.append(f"gameDate >= '{value}'")
            elif column_name == 'end_date':
                query_conditions.append(f"gameDate <= '{value}'")
            else:
                query_conditions.append(f"{column_name} {value}")

    all_conditions: str = " AND ".join(query_conditions)

    query += all_conditions

    if order_by:
        # If order_by is provided, it will be a list of column names, so construct
        # the ORDER BY statement and append it to the query.
        order: str = f" ORDER BY {', '.join(order_by)}"

        query += order

    return query


def validate_date_range_inputs(column_mapping: dict[str, QueryValue],
                               qualifiers: dict[str, str]) -> dict[str, QueryValue]:
    """
    Function to check any date inputs (e.g. 'start_date', 'end_date') where given in the
    expected format, and to make sure there are no conflicts between these inputs and the
    'season' input.

    :param dict[str, QueryValue] column_mapping: The column mapping provided for the query.
    :param dict[str, str] qualifiers: The qualifiers provided for the query.

    :raises ValueError: Raises a ValueError if a date value was provided in a format that
                        isn't YYYY-MM-DD.

    :return dict[str, QueryValue]: An updated version of the column mapping.
    """

    # First checks that both 'start_date' and 'end_date', if provided, match the YYYY-MM-DD format
    # using datetime.strptime().
    if 'start_date' in qualifiers.keys():
        start_date: str = qualifiers['start_date']
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"'start_date' provided in unsupported format. Must be YYYY-MM-DD. "\
                             f"Recieved {start_date}.") from e

    if 'end_date' in qualifiers.keys():
        end_date: str = qualifiers['end_date']
        try:
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"'end_date' provided in unsupported format. Must be YYYY-MM-DD. "\
                             f"Recieved {end_date}.") from e

    # Then, if both 'start_date' and 'end_date' were provided in addition to 'season', remove
    # 'season' from the column_mapping and print the reason why.
    if column_mapping.get('season', False) and qualifiers.get('start_date', False) and \
        qualifiers.get('end_date', False):
        print("Input values were provided for 'start_date', 'end_date', and 'season'. "\
              "Disregarding the input for 'season' and returning all games between "\
              f"{start_date} and {end_date}.")

        del column_mapping['season']

    return column_mapping
