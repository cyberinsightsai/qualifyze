import duckdb
import streamlit as st


@st.cache_resource
def get_duckdb_conn():
    duckdb_conn = duckdb.connect("data/qdb.duckdb", read_only=False)

    return duckdb_conn


def get_customer_credits(duckdb_conn, customer_id):
    """Get available credits for a customer. Returns 0 if customer not found or on error."""
    if not customer_id:
        return 0

    try:
        query = """
            SELECT count(credit_id) FROM credits WHERE customer_id = ? and credit_state = 'available'
        """
        result = duckdb_conn.execute(query, [customer_id]).df()
        if result.empty:
            return 0
        return int(result.iloc[0, 0])
    except Exception as e:
        print(f"Error getting customer credits: {e}")
        return 0


def get_total_requests(duckdb_conn):
    """Get total number of requests. Returns 0 on error."""
    try:
        query = """
            SELECT count(*) FROM requests
        """
        result = duckdb_conn.sql(query).df()
        if result.empty:
            return 0
        return int(result.iloc[0, 0])
    except Exception as e:
        print(f"Error getting total requests: {e}")
        return 0
    
def get_all_requests(duckdb_conn):
    """Get total number of requests. Returns 0 on error."""
    try:
        query = """
            SELECT * FROM requests
        """
        result = duckdb_conn.sql(query).df()
        return result
    except Exception as e:
        print(f"Error getting total requests: {e}")
        return 0

def get_total_customers(duckdb_conn):
    """Get total number of distinct customers. Returns 0 on error."""
    try:
        query = """
            SELECT count(DISTINCT customer_id) FROM credits
        """
        result = duckdb_conn.sql(query).df()
        if result.empty:
            return 0
        return int(result.iloc[0, 0])
    except Exception as e:
        print(f"Error getting total customers: {e}")
        return 0

def get_audit_type_by_date(duckdb_conn):
    """Get audit requests grouped by standard and date. Returns empty DataFrame on error."""
    try:
        query = """
            SELECT requested_standard, request_date, count(*) as total_requests
            FROM requests
            WHERE requested_standard IS NOT NULL
            GROUP BY requested_standard, request_date
            ORDER BY request_date
        """
        result = duckdb_conn.sql(query).df()
        return result
    except Exception as e:
        print(f"Error getting audit type by date: {e}")
        import pandas as pd
        return pd.DataFrame()


def get_audit_by_country(duckdb_conn):
    """Get audit requests grouped by country. Returns empty DataFrame on error."""
    try:
        query = """
            SELECT supplier_site_country as country, count(*) as total_requests
            FROM requests JOIN suppliers ON requests.requested_supplier_site_id = suppliers.supplier_site_id
            WHERE requested_supplier_site_id IS NOT NULL
            GROUP BY 1
            ORDER BY total_requests DESC
        """
        result = duckdb_conn.sql(query).df()
        return result
    except Exception as e:
        print(f"Error getting audit by country: {e}")
        import pandas as pd
        return pd.DataFrame()


def write_request_to_db(duckdb_conn, customer_id, supplier, request_date, request_type):
    """Write a request to the database. Returns True on success, False on failure."""
    if not all([customer_id, supplier, request_date, request_type]):
        print("Error: Missing required parameters for write_request_to_db")
        return False

    try:
        # Find the id of supplier
        supplier_name_and_location = get_suppliers_name_and_location(duckdb_conn)
        supplier_id = int(supplier_name_and_location[supplier_name_and_location['supplier_site_name'] == supplier]['supplier_site_id'].values[0])

        
        if supplier_id is None:
            print(f"Error: Supplier '{supplier}' not found")
            return False

        query = """
            INSERT INTO requests (customer_id, requested_supplier_site_id, request_date, requested_standard)
            VALUES (?, ?, ?, ?)
        """
        duckdb_conn.execute(query, [int(customer_id), supplier_id, request_date, request_type])
        duckdb_conn.commit()
        return True
    except Exception as e:
        print(f"Error writing request to database: {e}")
        print(query, customer_id, supplier_id, request_date, request_type)
        return False


def get_supplier_site_id(duckdb_conn, location):
    """Get supplier site ID by location. Returns None if not found or on error."""
    if not location:
        return None

    try:
        query = """
            SELECT supplier_site_id FROM suppliers WHERE supplier_site_location = ? LIMIT 1
        """
        result = duckdb_conn.execute(query, [location]).df()
        if not result.empty:
            return result.iloc[0, 0]
        else:
            return None
    except Exception as e:
        print(f"Error getting supplier site ID: {e}")
        return None

def get_suppliers_name_and_location(duckdb_conn):
    """Get all available suppliers with their names and locations. Returns empty DataFrame on error."""
    try:
        query = """
            SELECT supplier_site_id, supplier_site_name, supplier_site_country
            FROM suppliers
            WHERE supplier_site_availability = true
        """
        result = duckdb_conn.sql(query).df()
        return result
    except Exception as e:
        print(f"Error getting suppliers name and location: {e}")
        import pandas as pd
        return pd.DataFrame()
    

def get_audit_type_by_date(duckdb_conn):
    """Get audit requests grouped by standard and date. Returns empty DataFrame on error."""
    try:
        query = """
            SELECT requested_standard, request_date, count(*) as total_requests
            FROM requests
            WHERE requested_standard IS NOT NULL
            GROUP BY requested_standard, request_date
            ORDER BY request_date
        """
        result = duckdb_conn.sql(query).df()
        return result
    except Exception as e:
        print(f"Error getting audit type by date: {e}")
        import pandas as pd
        return pd.DataFrame()


def get_audits_by_date(duckdb_conn):
    """Get audit requests grouped by date for time series analysis. Returns empty DataFrame on error."""
    try:
        query = """
            SELECT date_trunc('day', request_date) as ds, count(*) as y
            FROM requests
            WHERE requested_standard IS NOT NULL
            GROUP BY ds
            ORDER BY ds
        """
        result = duckdb_conn.sql(query).df()
        return result
    except Exception as e:
        print(f"Error getting audits by date: {e}")
        import pandas as pd
        return pd.DataFrame()

def avg_timeof_resolution(duckdb_conn):
    """Get average time of resolution in days. Returns 0 on error or if no data."""
    try:
        query = """
            SELECT
            round(avg(consumed_date-reserved_date),1) as avg_timeof_resolution
            FROM FACT_REQUESTS
            WHERE consumed_date IS NOT NULL
        """
        result = duckdb_conn.sql(query).df()
        if result.empty or result.iloc[0, 0] is None:
            return 0
        return float(result.iloc[0, 0])
    except Exception as e:
        print(f"Error getting average time of resolution: {e}")
        return 0

def get_credits_by_customer(duckdb_conn):
    """Get average available credits per customer. Returns 0 on error or if no data."""
    try:
        query = """
            SELECT
            round(avg(available_credits),1) as avg_credits_by_customer
            FROM (
                SELECT customer_id, count(credit_id) as available_credits
                FROM credits
                WHERE credit_state = 'available'
                GROUP BY customer_id
            )
        """
        result = duckdb_conn.sql(query).df()
        if result.empty or result.iloc[0, 0] is None:
            return 0
        return float(result.iloc[0, 0])
    except Exception as e:
        print(f"Error getting credits by customer: {e}")
        return 0


def get_90d_requests(duckdb_conn):
    """Get all requests from the last 90 days. Returns empty DataFrame on error."""
    try:
        query = """
            SELECT
                credit_state
            FROM FACT_REQUESTS
            WHERE request_date >= current_date - interval '90' day
        """
        result = duckdb_conn.sql(query).df()
        return result
    except Exception as e:
        print(f"Error getting 90 day requests: {e}")
        import pandas as pd
        return pd.DataFrame()

def get_valid_requests(duckdb_conn):
    """Get count of valid (reserved) requests from last 30 days. Returns 0 on error."""
    try:
        query = """
            SELECT
            count(*) as valid_requests
            FROM FACT_REQUESTS
            WHERE credit_state = 'reserved' and request_date >= current_date - interval '30' day
        """
        result = duckdb_conn.sql(query).df()
        if result.empty:
            return 0
        return int(result.iloc[0, 0])
    except Exception as e:
        print(f"Error getting valid requests: {e}")
        return 0

def get_finished_requests(duckdb_conn):
    """Get count of finished (consumed) requests from last 30 days. Returns 0 on error."""
    try:
        query = """
            SELECT
            count(*) as finished_requests
            FROM FACT_REQUESTS
            WHERE credit_state = 'consumed' and request_date >= current_date - interval '30' day
        """
        result = duckdb_conn.sql(query).df()
        if result.empty:
            return 0
        return int(result.iloc[0, 0])
    except Exception as e:
        print(f"Error getting finished requests: {e}")
        return 0


def is_supplier_available(duckdb_conn, supplier_site_id):
    """Check if supplier is available. Returns False if not available or on error."""
    if not supplier_site_id:
        return False

    try:
        query = """
            SELECT supplier_site_availability FROM suppliers WHERE supplier_site_id = ? LIMIT 1
        """
        result = duckdb_conn.execute(query, [int(supplier_site_id)]).df()

        if not result.empty:
            return bool(result.iloc[0, 0])
        else:
            return False
    except Exception as e:
        print(f"Error checking supplier availability: {e}")
        return False

def is_supplier_blacklisted(duckdb_conn, supplier_site_id, request_date):
    """Check if supplier is blacklisted on the given date. Returns False if not blacklisted or on error."""
    if not supplier_site_id or not request_date:
        return False

    try:
        query = """
            SELECT COUNT(*) as count FROM blacklist
            WHERE supplier_site_id = ?
            AND blacklist_since <= ?
            AND blacklist_until >= ?
            LIMIT 1
        """
        
        result = duckdb_conn.execute(query, [int(supplier_site_id), request_date, request_date]).df()
        
        if not result.empty:
            return int(result.iloc[0, 0]) == 0
        else:
            return False
    except Exception as e:
        print(f"Error checking supplier blacklist status: {e}")
        return False
    
def check_table_exists(duckdb_conn, table_name, schema='main'):
    """Check if a table exists in the database. Returns True if exists, False otherwise."""
    try:
            return duckdb_conn.execute(
                """
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = ?
                AND table_name = ?
                LIMIT 1
                """,
                [schema.lower(), table_name.lower()]
            ).fetchone() is not None
    except Exception as e:
        print(f"Error checking if table exists: {e}")
        return False