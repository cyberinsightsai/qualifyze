import streamlit as st

## Body of the Streamlit app
st.title("✅ Qualifyze Case Study ✅")
st.markdown('''
            
            **Welcome to the Qualifyze Request Validation and Overview Application.**

            ''')
st.write("You can access either by the navigation bar or the buttons below.")
st.divider()
col1, col2, col3 = st.columns(3,border=True)
with col1:
    st.write("A document explaining the case study approach")
    if st.button("Delivery Document"):
        st.switch_page("pages/1_document.py")
with col2:
    st.write("Generate a new Request to validate supplier compliance")
    if st.button("Generate a new Request"):
        st.switch_page("pages/2_request.py")
with col3:
    st.write("Overview Dashboard with insights from the data")
    if st.button("Overview Dashboard"):
        st.switch_page("pages/3_dashboard.py")
