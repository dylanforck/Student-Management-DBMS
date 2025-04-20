# mysql_db.py
# Author: Dylan Forck

'''
Provides helper functions to manage MySQL database connections
and execute SQL queries for the Student Management System.
'''

# Standard library imports
import mysql.connector
from mysql.connector import Error


# Establishes and returns a connection to the MySQL database
def open_connection(host_name: str,
                    user_name: str,
                    user_password: str,
                    db_name: str,
                    port: int = 3306):

    try:
        # Attempt to create a database connection
        connection = mysql.connector.connect(
            host=host_name,
            port=port,
            user=user_name,
            password=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
        return connection

    except Error as e:
        # Log connection errors and return None for failure
        print(f"The error occurred when connecting: {e}")
        return None

# Closes the provided MySQL database connection if it is open
def close_connection(connection):

    # Check if connection exists and is open before closing
    if connection and connection.is_connected():
        connection.close()
        print("MySQL Database connection closed")

# Executes a write (INSERT, UPDATE, DELETE) query against the database
def execute_query(connection, query: str, params: tuple = None):
    
    # Create a new cursor for executing the query
    cursor = connection.cursor()
    try:
        # Execute the SQL statement with optional parameters
        cursor.execute(query, params)
        affected = cursor.rowcount

        # Commit the transaction to persist changes
        connection.commit()
        return affected

    except Error as e:
        # Roll back transaction on error to maintain data integrity
        connection.rollback()
        print(f"The error occurred: {e}")
        return None

    finally:
        # Ensure cursor is closed in all cases to free resources
        cursor.close()

# Executes a read (SELECT) query and returns the results
def execute_read_query(connection, query: str, params: tuple = None):

    # Using dictionary=True to fetch rows as dicts instead of tuples
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        return cursor.fetchall()

    except Error as e:
        # Log errors
        print(f"The error occurred: {e}")
        return None

    finally:
        # Always close cursor to free up resources
        cursor.close()
