## load in streamlit the markdown file located in documentation/CASE_STUDY_DOCUMENTATION.md
import streamlit as st
from pathlib import Path

st.title("✅ Delivery Document ✅")

with open("documentation/CASE_STUDY_DOCUMENTATION.md", "r") as f:
    doc_md = f.read()

st.markdown(doc_md)
