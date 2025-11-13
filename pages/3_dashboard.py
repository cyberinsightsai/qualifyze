import streamlit as st
import tools.utils as utils
import tools.qdb as qdb
from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt

st.header("Dashboard Metrics")
st.markdown('''
            **Welcome to the Qualifyze Dashboard Overview.**
            ''')
st.markdown('''
            Here you can find insights and summaries of customer requests and credits.
            Use the navigation menu to switch between the Request Validation page and the Dashboard overview.
            ''')



l_90d_req = utils.get_90d_requests(qdb.duckdb_conn)

if not l_90d_req.empty:
    st.subheader("Last 90 days Funnel from a total of " + str(len(l_90d_req)) + " requests")
    # from the l_90d_req get the open, validated and finished requests
    value_counts = l_90d_req['credit_state'].value_counts().to_dict() if 'credit_state' in l_90d_req.columns else {}
    array_of_states = [
        len(l_90d_req),
        value_counts.get('reserved', 0),
        value_counts.get('consumed', 0)
    ]
    fig1, ax1 = plt.subplots()
    ax1.pie(array_of_states, labels=['Open','Reserved', 'Consumed'], autopct='%1.1f%%', startangle=90, radius=2)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig1, width=500)
else:
    st.info("No requests found in the last 90 days.")


st.divider()

st.subheader("Requests & Customer")
left, right = st.columns(2)
with left:
    st.metric(label="Total Requests", value=utils.get_total_requests(qdb.duckdb_conn), border=True)
with right:
    st.metric(label="Total Customers", value=utils.get_total_customers(qdb.duckdb_conn), border=True)

st.subheader("Resolution & Consumption")
left2, right2 = st.columns(2)
with left2:
    st.metric(label="Avg time of resolution (in days)", value=utils.avg_timeof_resolution(qdb.duckdb_conn), border=True)
with right2:
    st.metric(label="Avg Credits by Customer", value=utils.get_credits_by_customer(qdb.duckdb_conn), border=True)

st.divider()

st.subheader("Requests by Type and Date")
audit_type_by_date = utils.get_audit_type_by_date(qdb.duckdb_conn)
if not audit_type_by_date.empty:
    st.scatter_chart(audit_type_by_date, x="request_date", y="total_requests", color="requested_standard")
else:
    st.info("No data available for requests by type and date.")

st.divider()

st.subheader("Requests by Country")
audit_by_country = utils.get_audit_by_country(qdb.duckdb_conn)
if not audit_by_country.empty:
    st.bar_chart(audit_by_country, x="country", y="total_requests", sort="total_requests", horizontal=True)
else:
    st.info("No data available for requests by country.")



st.divider()


st.subheader("Trend in next 30 days and weekly behavior")
audits_by_day = utils.get_audits_by_date(qdb.duckdb_conn)

if not audits_by_day.empty and len(audits_by_day) > 2:
    try:
        # Train Prophet
        m = Prophet()
        m.fit(audits_by_day)

        # Make future dataframe and forecast
        future = m.make_future_dataframe(periods=30, freq='d')
        forecast = m.predict(future)
        st.write(m.plot_components(forecast))
        # there can't be negative requests
        forecast.loc[forecast['yhat'] < 0, 'yhat'] = 0
        forecast.loc[forecast['yhat_lower'] < 0, 'yhat_lower'] = 0
        # show only the forcasted values from now on
        forecast = forecast[forecast['ds'] >= audits_by_day['ds'].max()]

        st.subheader("Forecast for next month")
        st.area_chart(pd.DataFrame({
                "forecast": forecast.set_index("ds")["yhat"],
                "lowest": forecast.set_index("ds")["yhat_lower"],
                "highest": forecast.set_index("ds")["yhat_upper"]
            }), use_container_width=True)
    except Exception as e:
        st.error(f"Error generating forecast: {e}")
else:
    st.info("Not enough data to generate forecast. Need at least 3 data points.")
