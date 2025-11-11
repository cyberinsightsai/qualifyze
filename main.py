import streamlit as st
import tools.qdb as qdb
import tools.utils as utils

# Initialize the database
qdb.setup_database(qdb.duckdb_conn)




## Body of the Streamlit app
st.title("✅ Qualifyze Case Study ✅")

st.markdown('''
            
            **Welcome to the Qualifyze Request Validation and Overview Application.**

            Use the navigation menu to switch between the Request Validation page and the Dashboard overview.
            ''')

if st.button("Generate a new Request"):
    st.switch_page("pages/request.py")
if st.button("Overview Dashboard"):
    st.switch_page("pages/dashboard.py")