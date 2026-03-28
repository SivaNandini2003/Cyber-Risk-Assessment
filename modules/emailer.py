# modules/emailer.py
import os
from datetime import datetime
import pandas as pd

REPORTS_DIR = 'reports'
os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_pdf_report(df: pd.DataFrame, scan_time: str, output_path: str) -> str:
    """
    Simple PDF generator (stable version)
    """
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "CyberScan Report", ln=True, align="C")

    pdf.set_font("Arial", "", 10)
    pdf.cell(200, 8, f"Generated: {scan_time}", ln=True)

    pdf.ln(5)

    # Table header
    pdf.set_font("Arial", "B", 8)
    headers = ["IP", "Port", "Service", "Severity", "Risk"]
    for h in headers:
        pdf.cell(38, 8, h, border=1)
    pdf.ln()

    # Table rows
    pdf.set_font("Arial", "", 7)
    for _, row in df.iterrows():
        pdf.cell(38, 6, str(row.get("ip", "")), border=1)
        pdf.cell(38, 6, str(row.get("port", "")), border=1)
        pdf.cell(38, 6, str(row.get("service", "")), border=1)
        pdf.cell(38, 6, str(row.get("severity", "")), border=1)
        pdf.cell(38, 6, f"{row.get('risk_score', 0):.2f}", border=1)
        pdf.ln()

    pdf.output(output_path)
    return output_path