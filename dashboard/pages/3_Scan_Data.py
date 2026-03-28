
import streamlit as st
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
df=st.session_state.get("df")
st.title("Scan Data")
if df is None:
    st.info("No data")
else:
    sev=st.selectbox("Severity",["All","Critical","High","Medium","Low"])
    if sev!="All":
        df=df[df["severity"]==sev]
    st.dataframe(df)
