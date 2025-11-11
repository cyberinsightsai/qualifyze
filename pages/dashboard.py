import streamlit as st
import tools.utils as utils
import tools.qdb as qdb

st.header("Dashboard Metrics")
st.markdown('''
            **Welcome to the Qualifyze Dashboard Overview.**
            ''')
st.markdown('''
            Here you can find insights and summaries of customer requests and credits.
            Use the navigation menu to switch between the Request Validation page and the Dashboard overview.
            ''')



st.subheader("Total Requests")
left, right = st.columns(2)
with left:
    st.metric(label="Total Requests", value=utils.get_total_requests(qdb.duckdb_conn), border=True)
with right:
    st.metric(label="Total Customers", value=utils.get_total_customers(qdb.duckdb_conn), border=True)

st.divider()

st.subheader("Requests by Type and Date")
audit_type_by_date = utils.get_audit_type_by_date(qdb.duckdb_conn)
st.scatter_chart(audit_type_by_date, x="request_date", y="total_requests", color="requested_standard")

st.divider()

st.subheader("Requests by Country")
audit_by_country = utils.get_audit_by_country(qdb.duckdb_conn)
st.bar_chart(audit_by_country, x="country", y="total_requests", sort="total_requests", horizontal=True)