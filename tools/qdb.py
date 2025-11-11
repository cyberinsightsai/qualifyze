'''
database.py
This file create the database connection and load the data files as tables to be queried.
'''
import tools.utils as utils

duckdb_conn = utils.get_duckdb_conn()

def setup_database(duckdb_conn):
    # Create requests table
    duckdb_conn.execute("""
        create table if not exists requests as
        from 'data/data_requests.csv'
    """)
    print("Requests table created.")

    #create  Suppliers table
    duckdb_conn.sql("""
        create table if not exists suppliers as
        from 'data/suppliers.csv'
    """)
    print("Suppliers table created.")

    # Create the Suppliers Blacklist table
    duckdb_conn.sql("""
        create table if not exists blacklist as
        from 'data/supplier_blacklist.csv'
    """)
    print("Blacklist table created.")

    # Create the credits table
    duckdb_conn.sql("""
        create table if not exists credits as
        from 'data/credits.csv'
    """)
    print("Credits table created.")

    # Create the quality officers table
    duckdb_conn.sql("""
        create table if not exists quality_officers as
        from 'data/quality_officers.csv'
    """)
    print("Quality Officers table created.")

    duckdb_conn.commit()