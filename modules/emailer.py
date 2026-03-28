# modules/emailer.py
import os
import smtplib
from datetime import datetime
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# 📄 PDF GENERATION
# ─────────────────────────────────────────────
def generate_pdf_report(df: pd.DataFrame, scan_time: str, output_path: str) -> str:
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


# ─────────────────────────────────────────────
# 📧 EMAIL SENDER (FIXED)
# ─────────────────────────────────────────────
def send_alert_email(sender, password, receiver, df, scan_time):
    """
    Sends email with optional PDF attachment
    """

    try:
        # ✅ Send report if there are any results
        if len(df) == 0:
            print("No scan results → email skipped")
            return False

        # ── Email content ──
        msg = MIMEMultipart()
        msg["Subject"] = f"📊 CyberScan Report ({len(df)} findings)"
        msg["From"] = sender
        msg["To"] = receiver

        body = f"""
CyberScan Report

Scan Time: {scan_time}

Total Hosts: {df['ip'].nunique()}
Total Ports: {len(df)}

Critical: {len(df[df['severity']=='Critical'])}
High: {len(df[df['severity']=='High'])}
Medium: {len(df[df['severity']=='Medium'])}

Check attached report.
"""

        msg.attach(MIMEText(body, "plain"))

        # ── Generate PDF ──
        filename = f"report_{datetime.now().strftime('%H%M%S')}.pdf"
        pdf_path = os.path.join(REPORTS_DIR, filename)

        generate_pdf_report(df, scan_time, pdf_path)

        # ── Attach PDF ──
        with open(pdf_path, "rb") as f:
            part = MIMEApplication(f.read(), _subtype="pdf")
            part.add_header(
                "Content-Disposition",
                "attachment",
                filename=filename
            )
            msg.attach(part)

        # ── Send Email ──
        print("Connecting to Gmail SMTP...")

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()

        print("EMAIL SENT SUCCESS")
        return True

    except Exception as e:
        import traceback
        print("EMAIL ERROR:", e)
        print(traceback.format_exc())
        return str(e)