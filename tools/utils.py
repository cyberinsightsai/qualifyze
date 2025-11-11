import duckdb
import streamlit as st


@st.cache_resource
def get_duckdb_conn():
    duckdb_conn = duckdb.connect("data/qdb.duckdb", read_only=False)

    return duckdb_conn


def get_customer_credits(duckdb_conn, customer_id):
    query = f"""
        SELECT count(credit_id) FROM credits WHERE customer_id = '{customer_id}' and credit_state = 'available'
    """
    result = duckdb_conn.sql(query).df().iloc[0, 0]
    return result


def get_total_requests(duckdb_conn):
    query = """
        SELECT count(*) FROM requests
    """
    result = duckdb_conn.sql(query).df().iloc[0, 0]
    return result

def get_total_customers(duckdb_conn):
    query = """
        SELECT count(DISTINCT customer_id) FROM credits
    """
    result = duckdb_conn.sql(query).df().iloc[0, 0]
    return result

def get_audit_type_by_date(duckdb_conn):
    query = f"""
        SELECT requested_standard, request_date, count(*) as total_requests 
        FROM requests 
        where  requested_standard IS NOT NULL
        GROUP BY requested_standard, request_date
        ORDER BY request_date
    """
    result = duckdb_conn.sql(query).df()
    return result


def get_audit_by_country(duckdb_conn):
    query = f"""
        SELECT supplier_site_country as country, count(*) as total_requests 
        FROM requests join suppliers on requests.requested_supplier_site_id = suppliers.supplier_site_id
        where requested_supplier_site_id IS NOT NULL
        GROUP BY 1
        ORDER BY total_requests DESC
    """
    result = duckdb_conn.sql(query).df()
    return result


def write_request_to_db(duckdb_conn, customer_id, location, request_date, request_type):
    location = get_supplier_site_id(duckdb_conn, location)
    duckdb_conn.execute(f"""
        INSERT INTO requests (customer_id, request_supplier_site_id, request_date, requested_standard)
        VALUES ('{customer_id}', '{location}', '{request_date}', '{request_type}')
    """)
    return duckdb_conn.commit()


def get_supplier_site_id(duckdb_conn, location):
    query = f"""
        SELECT supplier_site_id FROM suppliers WHERE supplier_site_location = '{location}' LIMIT 1
    """
    result = duckdb_conn.sql(query).df()
    if not result.empty:
        return result.iloc[0, 0]
    else:
        return None
    
def get_suppliers_name_and_location(duckdb_conn):
    query = f"""
        SELECT supplier_site_id, supplier_site_name, supplier_site_location FROM suppliers
    """
    result = duckdb_conn.sql(query).df()
    return result
    