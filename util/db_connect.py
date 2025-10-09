"""
Module for creating and managing the connection to the database.

Using duckdb and MotherDuck as our database for now, but no guarantee that this will be the 
case in the future.

A MotherDuck authorization token with read-only access is set in util/config.py, which we use
to connect.
"""

import os
import duckdb
import util.config


def create_connection(db_name: str = 'md:') -> duckdb.DuckDBPyConnection:
    """
    Creates the connection object to the database.

    :param _type_ db_name: Name of the database to connect to, defaults to 'md:' which uses
                           the authorization token (which is set as an env var) to auto-
                           resolve the database name.

    :return duckdb.DuckDBPyConnection: The connection object which we can use to query the db.
    """

    # MotherDuck uses the MOTHERDUCK_TOKEN env var to authorize read-only access to the db
    os.environ['MOTHERDUCK_TOKEN'] = util.config.MOTHERDUCK_READ_TOKEN

    conn: duckdb.DuckDBPyConnection = duckdb.connect(db_name, read_only=True)

    return conn
