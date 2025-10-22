"""
Module used to construct SQL queries that will be used to query the database.

Instead of each individual module building the queries based on their provided inputs,
use this module to manage this task in a central location.

When each of the primary modules are called, they will call a function here, and using
the provided parameters, an SQL query string will be constructed and returned.
"""

from util.input_validation import check_input_type, check_input_values

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

        for column_name, value in qualifiers.items():
            query_conditions.append(f"{column_name} {value}")

    all_conditions: str = " AND ".join(query_conditions)

    query += all_conditions

    if order_by:
        # If order_by is provided, it will be a list of column names, so construct
        # the ORDER BY statement and append it to the query.
        order: str = f" ORDER BY {', '.join(order_by)}"

        query += order

    return query
