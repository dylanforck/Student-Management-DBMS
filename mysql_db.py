#Dylan Forck
#Project
#Description: Student Management System - MySQL Connection



# mysql_db.py
import mysql.connector
from mysql.connector import Error

def open_connection(host_name: str, user_name: str, user_password: str, db_name: str):
    """
    Opens a connection to the MySQL database.
    """
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
        return connection
    except Error as e:
        print(f"The error occurred when connecting: {e}")
        return None

def close_connection(connection):
    """
    Closes the provided MySQL database connection.
    """
    if connection and connection.is_connected():
        connection.close()
        print("MySQL Database connection closed")

def execute_query(connection, query: str, params: tuple = None):
    """
    Executes a write query and returns the affected-row count.
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        affected = cursor.rowcount
        connection.commit()
        return affected
    except Error as e:
        connection.rollback()
        print(f"The error occurred: {e}")
        return None
    finally:
        cursor.close()

def execute_read_query(connection, query: str, params: tuple = None):
    """
    Executes a read query and returns results as a list of dicts.
    """
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except Error as e:
        print(f"The error occurred: {e}")
        return None
    finally:
        cursor.close()
