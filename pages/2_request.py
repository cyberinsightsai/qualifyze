import streamlit as st
import tools.qdb as qdb
import tools.utils as utils
import pandas as pd
import time

# function to validate the request from the customer point of view
def customer_validate_request(customer_id, supplier, request_date, request_type):
    #check that contains who, where and when
    if not customer_id or not supplier or not request_date:
        st.error("Please fill in all required fields: Customer ID, Supplier, and Request Date.")
        return False
    #check that request type is valid
    valid_request_types = ["GMP", "GVP", "GCP"]
    if request_type not in valid_request_types:
        st.error(f"Invalid request type. Please choose from: {', '.join(valid_request_types)}.")
        return False
    
    # check customer has enough credits
    # GMP = 1 credit, GVP = 2 credits, GCP = 3 credits
    required_credits = {"GMP": 1, "GVP": 2, "GCP": 3}
    customer_credits = utils.get_customer_credits(qdb.duckdb_conn, customer_id)

    if customer_credits < required_credits[request_type]:
        st.error(f"Customer does not have enough credits for {request_type}. Required: {required_credits[request_type]}, Available: {customer_credits}.")
        return False

    st.success("Request is valid and can be processed.")
    return True


def supplier_validate_request(supplier, request_date):
    # check supplier is not blacklisted
    if not utils.is_supplier_blacklisted(qdb.duckdb_conn, supplier, request_date):
        st.error("Supplier is blacklisted and cannot process requests.")
        return False
    else: 
        if not utils.is_supplier_available(qdb.duckdb_conn, supplier):
            st.error("Supplier is not available to process requests.")
            return False
        else:
            return True if  utils.write_request_to_db(qdb.duckdb_conn,customer_id, supplier, request_date, request_type) else False
 

## Body of the Streamlit app
st.title("Request Validator and Overview")

st.header("New Request")

sup_df = utils.get_suppliers_name_and_location(qdb.duckdb_conn)

# Check if suppliers are available
if sup_df.empty:
    st.error("No suppliers available. Please contact administrator.")
    st.stop()

with st.form("request_form"):
    customer_id = st.selectbox("Customer ID", [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010], index=None, placeholder="Select a customer ID")
    supplier = st.selectbox("Supplier", sup_df['supplier_site_name'], index=None, placeholder="Select a supplier")
    request_date = st.date_input("Request Date")
    request_type = st.selectbox("Request Type", ["GMP", "GVP", "GCP"], index=None, placeholder="Select a request type")
    submit_button = st.form_submit_button("Evaluate Request", help="Click to evaluate the request based on customer and supplier validations.")

if submit_button:
    st.write("Processing request...")
    with st.spinner("Validating...", show_time=True):
        time.sleep(2)

    if customer_validate_request(customer_id, supplier, request_date, request_type):
        st.write("Validating Supplier.")
        with st.spinner("Validating...", show_time=True):
            time.sleep(2)

        # Get supplier ID safely
        supplier_match = sup_df[sup_df['supplier_site_name'] == supplier]
        if supplier_match.empty:
            st.error("Supplier not found.")
        else:
            supplier_id = supplier_match['supplier_site_id'].values[0]
            if supplier_validate_request(supplier_id, request_date):
                st.success("Request has been successfully validated and recorded.")
            else:
                st.error("Supplier validation failed.")
    else:
        st.error("Customer validation failed.")

st.divider()

st.header("Bulk request load")
uploaded_file = st.file_uploader("Upload CSV file with requests", type=["csv"], help="Upload a CSV file containing multiple requests for bulk processing.")
if uploaded_file is not None:
    st.write("Processing bulk requests...")
    bulk_df = pd.read_csv(uploaded_file)
    successful_count = 0
    failed_count = 0
    for row in bulk_df.itertuples():
        customer_id = row.customer_id
        supplier_id = row.requested_supplier_site_id
        request_date = row.request_date
        request_type = row.requested_standard

        # Get supplier name from ID
        supplier_match = sup_df[sup_df['supplier_site_id'] == supplier_id]
        if supplier_match.empty:
            st.error(f"Supplier is not AVAILABLE for bulk request with ID: {supplier_id}")
            failed_count += 1
            continue
        
        supplier_name = supplier_match['supplier_site_name'].values[0]

        if not customer_validate_request(customer_id, supplier_name, request_date, request_type):
            st.error(f"Bulk request validation failed for Customer ID: {customer_id}, Supplier: {supplier_name}, Date: {request_date}, Type: {request_type}")
            failed_count += 1
            continue

        if not supplier_validate_request(supplier_id, request_date):
            st.error(f"Supplier validation failed for bulk request: Supplier ID: {supplier_id}, Date: {request_date}")
            failed_count += 1
            continue
        
        successful_count += 1
    
    st.write(f"Bulk request processing completed. Successful: {successful_count}, Failed: {failed_count}")

    


st.divider()

with st.expander("View All Requests"):
    st.dataframe(utils.get_all_requests(qdb.duckdb_conn))