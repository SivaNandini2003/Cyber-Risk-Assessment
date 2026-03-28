# 🛡️ CyberScan Pro

🚀 Advanced Cybersecurity Risk Assessment System  
A powerful tool for network scanning, vulnerability analysis, and real-time security monitoring.

---

## 📌 Features

- 🔐 Login Authentication
- 🌐 Network Scanning (Nmap)
- 📊 Risk Analysis Engine
- 📈 Interactive Dashboard (Charts & KPIs)
- 🌍 Geo-IP Mapping
- 📧 Email Alerts for High Risk
- 📄 PDF Report Generation
- 📥 CSV Export
- ⚡ Fast Demo Mode for quick testing

---

## 🧠 How It Works

1. User enters target (IP / Domain)
2. System runs Nmap scan
3. Extracts open ports & services
4. Analyzes risk using scoring logic
5. Displays results in dashboard
6. Sends alerts & generates reports

---

## 🏗️ Project Structure

```
cyberscan/
│
├── dashboard/
│   ├── app.py
│   └── pages/
│       ├── 2_Analysis.py
│       ├── 3_Scan_Data.py
│       └── 4_History.py
│
├── modules/
│   ├── scanner.py
│   ├── analyser.py
│   ├── database.py
