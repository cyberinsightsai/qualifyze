import streamlit as st
import tools.qdb as qdb

# Initialize the database
qdb.setup_database(qdb.duckdb_conn)

# Navigation
home = st.Page("pages/0_home.py", title="Home", icon="🏠")
document = st.Page("pages/1_document.py", title="Documentation", icon="📄")
request = st.Page("pages/2_request.py", title="Create a request", icon="📝")
dashboard = st.Page("pages/3_dashboard.py", title="Dashboard", icon="📊")

nav_bar = st.navigation([home, document, request, dashboard])

nav_bar.run()