## load in streamlit the markdown file located in documentation/CASE_STUDY_DOCUMENTATION.md
import streamlit as st

st.title("✅ Delivery Document ✅")

try:
    with open("documentation/CASE_STUDY_DOCUMENTATION.md", "r") as f:
        doc_md = f.read()
    st.markdown(doc_md)
except FileNotFoundError:
    st.error("Documentation file not found. Please contact administrator.")
except Exception as e:
    st.error(f"Error loading documentation: {e}")
