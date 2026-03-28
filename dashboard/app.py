import streamlit as st
import pandas as pd
import os, sys, random, time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.emailer import generate_pdf_report, send_alert_email

# SAFE IMPORTS
try:
    from modules.scanner import run_nmap_scan, parse_nmap_xml, check_virustotal
except:
    run_nmap_scan = parse_nmap_xml = check_virustotal = None

try:
    from modules.analyser import enrich_dataframe
except:
    enrich_dataframe = None

try:
    from modules.emailer import generate_pdf_report, send_alert_email
except:
    generate_pdf_report = send_alert_email = None

st.set_page_config(page_title="CyberScan Pro", layout="wide")

# ── DARK HACKER UI ─────────────────────
st.markdown("""
<style>
body {background-color:#0d1117; color:#00ffcc;}
.big-title {font-size:45px; color:#00ffcc; font-weight:bold;}
.sidebar .sidebar-content {background-color:#020617;}
.stButton>button {
    background-color:#00ffcc;
    color:black;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ── SIMPLE LOGIN STORAGE ─────────────────
USERS = {"admin":"admin123"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.markdown("<h1 class='big-title'>🔐 CyberScan Login</h1>", unsafe_allow_html=True)
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if USERS.get(user) == pwd:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# ── SIDEBAR ─────────────────────────────
with st.sidebar:
    st.title("🛡️ CyberScan")
    st.success(f"Logged in as {st.session_state.user}")
    st.divider()

    vt_key = st.text_input("🔑 VirusTotal API Key", type="password")

    sender = st.text_input("📧 Sender Email")
    password = st.text_input("App Password", type="password")
    receiver = st.text_input("Receiver Email")

# ── HEADER ─────────────────────────────
st.markdown("<div class='big-title'>🛡️ CyberScan Pro</div>", unsafe_allow_html=True)

targets_input = st.text_input("Targets (comma separated)", "scanme.nmap.org")
targets = [t.strip() for t in targets_input.split(",") if t.strip()]

mode = st.radio("Mode", ["⚡ Fast Demo", "🌐 Real Scan"])

# ── DEMO ─────────────────────────────
def demo():
    ips = ["192.168.1.1","10.0.0.1","8.8.8.8"]
    services = ["http","ssh","ftp","mysql","rdp"]

    data = []
    for _ in range(25):
        risk = random.uniform(1,10)
        data.append({
            "ip": random.choice(ips),
            "port": random.choice([22,80,21,3306,3389]),
            "service": random.choice(services),
            "risk_score": risk,
            "severity": "Critical" if risk>7 else "High" if risk>5 else "Medium",
            "country": random.choice(["US","IN","CN","RU"])
        })
    return pd.DataFrame(data)

# ── ANIMATION ─────────────────────────
def animation():
    bar = st.progress(0)
    txt = st.empty()
    for i in range(100):
        bar.progress(i+1)
        txt.text(random.choice(["Scanning...","Injecting packets...","Analyzing..."]))
        time.sleep(0.01)

# ── SESSION ─────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None

if "history" not in st.session_state:
    st.session_state.history = []

# ── RUN SCAN ─────────────────────────
if st.button("🚀 Run Scan"):

    animation()

    if mode == "⚡ Fast Demo":
        df = demo()

    else:
        try:
            rows = []
            for t in targets:
                xml = run_nmap_scan(t)
                rows.extend(parse_nmap_xml(xml))

            if not rows:
                df = demo()
            else:
                df_raw = pd.DataFrame(rows)

                # ── VT INTEGRATION ─────────
                vt_data = {}
                if vt_key and check_virustotal:
                    for ip in df_raw["ip"].unique():
                        vt_data[ip] = check_virustotal(ip, vt_key)

                df = enrich_dataframe(df_raw, vt_data) if enrich_dataframe else df_raw

        except:
            df = demo()

    st.session_state.df = df
    st.session_state.history.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "hosts": df["ip"].nunique(),
        "ports": len(df)
    })

    st.success("Scan Complete")

    # ── EMAIL SEND ─────────────────────
    if sender and password and receiver:
        sent = send_alert_email(
            sender,
            password,
            receiver,
            df,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        if sent == True:
            st.success("📧 Email sent successfully")
        elif sent == False:
            st.info("No critical/high alerts to send")
        else:
            st.error(f"❌ Email failed: {sent}")

# ── DISPLAY ─────────────────────────
df = st.session_state.df

if df is not None:

    st.subheader("📊 Dashboard")

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Hosts", df["ip"].nunique())
    c2.metric("Ports", len(df))
    c3.metric("Critical", len(df[df["severity"]=="Critical"]))
    c4.metric("High", len(df[df["severity"]=="High"]))
    c5.metric("Avg Risk", f"{df['risk_score'].mean():.1f}")

    import plotly.express as px

    st.plotly_chart(px.pie(df, names="severity"), use_container_width=True)
    st.plotly_chart(px.bar(df, x="service", color="severity"), use_container_width=True)

    st.dataframe(df, use_container_width=True)

    # CSV
    st.download_button("📥 Download CSV", df.to_csv(index=False), "scan.csv")

    # ── PDF ─────────────────────
    st.subheader("📄 Report")

    if st.button("Generate PDF Report"):
        file = f"report_{datetime.now().strftime('%H%M%S')}.pdf"

        if generate_pdf_report:
            generate_pdf_report(df, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), file)

            with open(file, "rb") as f:
                st.download_button("📥 Download PDF", f, file)
        else:
            st.error("PDF module missing")

    # ── HISTORY ─────────────────────
    st.subheader("📜 Scan History")
    st.table(pd.DataFrame(st.session_state.history))

else:
    st.info("Enter target and click Run Scan")