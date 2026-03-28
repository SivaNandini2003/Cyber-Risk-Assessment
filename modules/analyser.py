import pandas as pd

def enrich_dataframe(df):
    def calc_risk(row):
        if row['service'] in ['telnet', 'ftp']:
            return 9
        elif row['service'] in ['ssh', 'http']:
            return 5
        else:
            return 2

    df['risk_score'] = df.apply(calc_risk, axis=1)

    def severity(score):
        if score >= 8:
            return 'Critical'
        elif score >= 5:
            return 'High'
        elif score >= 3:
            return 'Medium'
        else:
            return 'Low'

    df['severity'] = df['risk_score'].apply(severity)

    return df


def build_host_summary(df):
    summary = df.groupby('ip').agg({
        'port': 'count',
        'risk_score': 'max',
        'severity': lambda x: x.value_counts().index[0]
    }).reset_index()

    summary.columns = ['ip', 'open_ports', 'max_risk', 'overall_severity']
    return summary


def generate_summary(df, host_sum=None):
    if df.empty:
        return {
            'total_hosts': 0,
            'total_ports': 0,
            'crit_hosts': 0,
            'high_hosts': 0,
            'max_risk': 0,
            'posture': 'LOW'
        }

    max_risk = float(df['risk_score'].max())

    if any(df['severity'] == 'Critical'):
        posture = "CRITICAL"
    elif any(df['severity'] == 'High'):
        posture = "HIGH RISK"
    else:
        posture = "LOW"

    return {
        'total_hosts': df['ip'].nunique(),
        'total_ports': len(df),
        'crit_hosts': int((df['severity'] == 'Critical').sum()),
        'high_hosts': int((df['severity'] == 'High').sum()),
        'max_risk': max_risk,
        'posture': posture
    }