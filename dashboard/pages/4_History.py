import streamlit as st
import os, sys

# 🔥 FIX PATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.database import load_history

st.title("📜 Scan History")

try:
    df = load_history()

    if df.empty:
        st.info("No scan history available")
    else:
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error loading history: {e}")