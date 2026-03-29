import streamlit as st
import pandas as pd
import os, sys

# PATH FIX
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

st.title("📜 Scan History")

# ── GET HISTORY ─────────────────────
history = st.session_state.get("history", [])

# ── FIX: convert list → DataFrame ───
history_df = pd.DataFrame(history)

# ── DISPLAY ─────────────────────────
if history_df.empty:
    st.info("No scan history yet")
else:
    st.dataframe(history_df, use_container_width=True)