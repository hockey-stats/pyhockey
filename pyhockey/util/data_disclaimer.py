"""
Module for simple function that displays the source of the data provided by each request.
"""


def print_data_disclaimer(source: str) -> None:
    """
    Prints a simple data disclaimer depending on the source of the data.

    :param str source: Name of the data source, ATM either MoneyPuck or NaturalStatTrick
    """

    source_map = {
        'MoneyPuck': 'https://moneypuck.com',
        'NaturalStatTrick': 'https://naturalstattrick.com'
    }

    print(f"Data for this query provided by {source} ({source_map[source]}).")
