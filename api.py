
# api.py — CyberScan API (Final Version)

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import List, Optional
import os

# ── APP INIT ─────────────────────────────
app = FastAPI(
    title="CyberScan API",
    version="1.0",
    description="API for CyberScan Network Risk Analysis"
)

# ── API KEY ─────────────────────────────
API_KEY = os.environ.get("CYBERSCAN_API_KEY", "admin123")

def verify_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

# ── MEMORY STORAGE ─────────────────────
SCAN_DATA = []

# ── DATA MODEL (MATCH YOUR DF) ──────────
class ScanRecord(BaseModel):
    ip: str
    port: str
    service: str
    state: Optional[str] = "open"
    risk_score: float
    severity: str
    country: Optional[str] = "Unknown"

# ── ROOT ───────────────────────────────
@app.get("/")
def root():
    return {
        "status": "CyberScan API running",
        "records": len(SCAN_DATA)
    }

# ── LOAD DATA (FROM STREAMLIT) ─────────
@app.post("/load", dependencies=[Depends(verify_key)])
def load_data(records: List[ScanRecord]):
    global SCAN_DATA
    SCAN_DATA = [r.dict() for r in records]

    return {
        "message": "Data loaded successfully",
        "records": len(SCAN_DATA),
        "hosts": len({r["ip"] for r in SCAN_DATA})
    }

# ── GET RESULTS ────────────────────────
@app.get("/results", dependencies=[Depends(verify_key)])
def get_results(severity: Optional[str] = None):

    if not SCAN_DATA:
        raise HTTPException(status_code=404, detail="No scan data found")

    data = SCAN_DATA

    if severity:
        data = [r for r in data if r["severity"].lower() == severity.lower()]

    return {
        "count": len(data),
        "results": data
    }

# ── KPI ANALYSIS ───────────────────────
@app.get("/analysis", dependencies=[Depends(verify_key)])
def analysis():

    if not SCAN_DATA:
        raise HTTPException(status_code=404, detail="No data")

    total_hosts = len({r["ip"] for r in SCAN_DATA})
    total_ports = len(SCAN_DATA)

    severity_count = {}
    for r in SCAN_DATA:
        sev = r["severity"]
        severity_count[sev] = severity_count.get(sev, 0) + 1

    risks = [r["risk_score"] for r in SCAN_DATA]

    return {
        "total_hosts": total_hosts,
        "total_ports": total_ports,
        "max_risk": max(risks),
        "avg_risk": round(sum(risks)/len(risks), 2),
        "severity_distribution": severity_count
    }

# ── HOST DETAILS ───────────────────────
@app.get("/host/{ip}", dependencies=[Depends(verify_key)])
def host_details(ip: str):

    data = [r for r in SCAN_DATA if r["ip"] == ip]

    if not data:
        raise HTTPException(status_code=404, detail="Host not found")

    return {
        "ip": ip,
        "records": data,
        "count": len(data)
    }