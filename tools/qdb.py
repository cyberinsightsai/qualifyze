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

    # create a fact table for OLAP purposes
    duckdb_conn.sql("""
            CREATE view if not exists FACT_REQUESTS AS
                WITH request_base AS (
                    SELECT
                        r.id_request,
                        r.request_date,
                        r.requested_standard,
                        r.requested_supplier_site_id,
                        r.requested_audit_id,
                        r.audit_scope,
                        r.contact_information,
                        r.quality_officer_id,
                        r.customer_id
                    FROM requests r
                ),

                -- Choose the single most relevant credit per request
                credit_ranked AS (
                    SELECT
                        c.credit_id,
                        c.customer_id AS credit_customer_id,
                        c.credit_state,
                        c.reserved_date,
                        c.consumed_date,
                        c.id_request,
                        ROW_NUMBER() OVER (
                            PARTITION BY c.id_request
                            ORDER BY COALESCE(c.consumed_date, c.reserved_date) DESC NULLS LAST,
                                    c.credit_id
                        ) AS rn
                    FROM credits c
                ),
                credit_best AS (
                    SELECT *
                    FROM credit_ranked
                    WHERE rn = 1
                ),

                -- Blacklist status of supplier site as-of the request date
                blacklist_match AS (
                    SELECT
                        sb.supplier_site_id,
                        sb.blacklist_since,
                        sb.blacklist_until
                    FROM blacklist sb
                ),

                -- Supplier site attributes (from SUPPLIERS per your ER)
                supplier_site AS (
                    SELECT
                        s.supplier_site_id,
                        s.supplier_site_name,
                        s.supplier_site_country,
                        s.supplier_site_address,
                        s.supplier_site_availability
                    FROM suppliers s
                ),

                -- Final select: join all parts
                final_rows AS (
                    SELECT
                        rb.id_request,
                        rb.request_date,
                        rb.requested_standard,
                        rb.requested_supplier_site_id,
                        rb.requested_audit_id,
                        rb.audit_scope,
                        rb.contact_information,
                        rb.quality_officer_id,

                        -- Customer (dimension attributes included to simplify)
                        rb.customer_id,

                        -- Supplier (organization-level)
                        rb.requested_supplier_site_id,

                        -- Supplier site
                        ss.supplier_site_id AS supplier_site_id_resolved,
                        ss.supplier_site_name,
                        ss.supplier_site_country,
                        ss.supplier_site_address,
                        ss.supplier_site_availability,

                        -- Blacklist snapshot as-of request date
                        CASE
                            WHEN EXISTS (
                                SELECT 1
                                FROM blacklist_match bm
                                WHERE bm.supplier_site_id = COALESCE(ss.supplier_site_id, rb.requested_supplier_site_id)
                                AND rb.request_date BETWEEN bm.blacklist_since
                                                        AND COALESCE(bm.blacklist_until, rb.request_date)
                            ) THEN 1 ELSE 0
                        END AS is_currently_blacklisted,

                        -- Credit linked to this request (if any)
                        cb.credit_id,
                        cb.credit_state,
                        cb.reserved_date,
                        cb.consumed_date,

                        -- Simple additive metrics
                        1 AS request_count,
                        CASE WHEN rb.requested_audit_id IS NOT NULL AND rb.requested_audit_id <> '' THEN TRUE ELSE FALSE END AS has_audit_id
                    FROM request_base rb
                    LEFT JOIN supplier_site ss
                        ON ss.supplier_site_id = rb.requested_supplier_site_id
                        OR ss.supplier_site_id = rb.requested_supplier_site_id
                    LEFT JOIN credit_best cb
                        ON cb.id_request = rb.id_request
                )
                SELECT * FROM final_rows
    """)
    print("FACT_REQUEST table created.")

    duckdb_conn.commit()