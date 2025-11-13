import streamlit as st
import tools.qdb as qdb
import tools.utils as utils
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
    print(required_credits[request_type])
    print(utils.get_customer_credits(qdb.duckdb_conn,customer_id))
    if not utils.get_customer_credits(qdb.duckdb_conn,customer_id) > required_credits[request_type]:
        st.error(f"Customer does not have enough credits for {request_type}. Required: {required_credits[request_type]}.")
        return False

    st.success("Request is valid and can be processed.")
    return True if  utils.write_request_to_db(qdb.duckdb_conn,customer_id, supplier, request_date, request_type) else False


def supplier_validate_request(supplier, request_date):
    # check supplier is not blacklisted
    if utils.is_supplier_blacklisted(qdb.duckdb_conn, supplier, request_date):
        st.error("Supplier is blacklisted and cannot process requests.")
        return False
    else: 
        if not utils.is_supplier_available(qdb.duckdb_conn, supplier):
            st.error("Supplier is not available to process requests.")
            return False
        else:
            return True
 

## Body of the Streamlit app
st.title("Request Validator and Overview")

st.header("New Request")

sup_df = utils.get_suppliers_name_and_location(qdb.duckdb_conn)

sup_id = sup_df[sup_df['supplier_site_name'] == 'Site 001']['supplier_site_id'].values[0]


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
        if supplier_validate_request(sup_df[sup_df['supplier_site_name']== supplier]['supplier_site_id'].values[0], request_date):
            st.success("Request has been successfully validated and recorded.") 
        else:
            st.error("Supplier validation failed.")
    else:
        st.error("Customer validation failed.")