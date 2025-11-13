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


def write_request_to_db(duckdb_conn, customer_id, supplier, request_date, request_type):
    supplier_name_and_location = get_suppliers_name_and_location(duckdb_conn)
    # find the match of supplier name to get location
    supplier_id = supplier_name_and_location[supplier_name_and_location['supplier_site_name'] == supplier]['supplier_site_id'].values[0]

    duckdb_conn.execute(f"""
        INSERT INTO requests (customer_id, requested_supplier_site_id, request_date, requested_standard)
        VALUES ('{customer_id}', '{supplier_id}', '{request_date}', '{request_type}')
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
        SELECT supplier_site_id, supplier_site_name, supplier_site_country FROM suppliers  where supplier_site_availability = true
    """
    result = duckdb_conn.sql(query).df()
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


def get_audits_by_date(duckdb_conn):
    query = f"""
        SELECT date_trunc('day', request_date) as ds, count(*) as y 
        FROM requests 
        where  requested_standard IS NOT NULL
        GROUP BY ds
        ORDER BY ds
    """
    result = duckdb_conn.sql(query).df()
    return result

def avg_timeof_resolution(duckdb_conn):
    query = f"""
        select 
        round(avg(consumed_date-reserved_date),1) as avg_timeof_resolution
        from FACT_REQUESTS
        where consumed_date is not null
    """
    result = duckdb_conn.sql(query).df().iloc[0, 0]
    return result

def get_credits_by_customer(duckdb_conn):
    query = f"""
        select 
        round(avg(available_credits),1) as avg_credits_by_customer
        from (
            select customer_id, count(credit_id) as available_credits
            from credits
            where credit_state = 'available'
            group by customer_id
        )
    """
    result = duckdb_conn.sql(query).df().iloc[0, 0]
    return result


def get_90d_requests(duckdb_conn):
    query = f"""
        select 
            credit_state
        from FACT_REQUESTS
        where  request_date >= current_date - interval '90' day
    """
    result = duckdb_conn.sql(query).df()
    return result

def get_valid_requests(duckdb_conn):
    query = f"""
        select 
        count(*) as valid_requests
        from FACT_REQUESTS
        where credit_state = 'reserved' and request_date >= current_date - interval '30' day
    """
    result = duckdb_conn.sql(query).df().iloc[0, 0]
    return result

def get_finished_requests(duckdb_conn):
    query = f"""
        select 
        count(*) as finished_requests
        from FACT_REQUESTS
        where credit_state = 'consumed' and request_date >= current_date - interval '30' day
    """
    result = duckdb_conn.sql(query).df().iloc[0, 0]
    return result


def is_supplier_available(duckdb_conn, supplier_site_id):
    query = f"""
        SELECT supplier_site_availability FROM suppliers WHERE supplier_site_id = '{supplier_site_id}' LIMIT 1
    """
    result = duckdb_conn.sql(query).df()
    if not result.empty:
        return result.iloc[0, 0]
    else:
        return False
    
def is_supplier_blacklisted(duckdb_conn, supplier_site_id, request_date):
    query = f"""
        SELECT * FROM blacklist WHERE supplier_site_id = '{supplier_site_id}' AND blacklist_since <= '{request_date}' AND blacklist_until >= '{request_date}' LIMIT 1
    """
    result = duckdb_conn.sql(query).df()
    if not result.empty:
        return result.iloc[0, 0]
    else:
        return False