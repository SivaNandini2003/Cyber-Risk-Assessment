import streamlit as st
import plotly.express as px
import os, sys, requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

st.set_page_config(layout="wide")

st.markdown("""
<style>
.big-title {font-size:28px; font-weight:bold; color:#00ffcc;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='big-title'>🔍 Security Analysis</div>", unsafe_allow_html=True)

df = st.session_state.get("df")

if df is None:
    st.warning("Run scan first")
    st.stop()

# ── SAFE COLUMNS FIX (IMPORTANT) ─────────────────────
if "exposure_score" not in df.columns:
    df["exposure_score"] = df["risk_score"]

if "threat_score" not in df.columns:
    df["threat_score"] = df["risk_score"]

# ── METRICS ─────────────────────────────
st.subheader("📊 Risk Overview")

c1,c2,c3 = st.columns(3)
c1.metric("Avg Risk", f"{df['risk_score'].mean():.1f}")
c2.metric("Max Risk", f"{df['risk_score'].max():.1f}")
c3.metric("Unique Hosts", df["ip"].nunique())

# ── SCATTER ─────────────────────────────
st.subheader("📈 Risk Heatmap")

fig = px.scatter(
    df,
    x="exposure_score",
    y="threat_score",
    size="risk_score",
    color="severity",
    hover_data=["ip","port","service"],
)
st.plotly_chart(fig, use_container_width=True)

# ── FAST MAP (COUNTRY BASED) ────────────
st.subheader("🌍 Quick Map")

df["lat"] = df["country"].map({
    "US":37,"IN":20,"CN":35,"RU":60
}).fillna(10)

df["lon"] = df["country"].map({
    "US":-95,"IN":78,"CN":104,"RU":100
}).fillna(0)

st.map(df[["lat","lon"]])

# ── REAL GEO MAP (ADVANCED) ─────────────
st.subheader("🌍 Live Attack Map")

@st.cache_data(show_spinner=False)
def get_location(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=2).json()
        return res.get("lat", 0), res.get("lon", 0)
    except:
        return 0, 0

map_df = df.copy()
coords = map_df["ip"].apply(get_location)
map_df["lat"] = coords.apply(lambda x: x[0])
map_df["lon"] = coords.apply(lambda x: x[1])

st.map(map_df[["lat","lon"]])