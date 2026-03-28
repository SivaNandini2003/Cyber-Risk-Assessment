import subprocess
import xml.etree.ElementTree as ET
import os

SCAN_DIR = "scan_results"
os.makedirs(SCAN_DIR, exist_ok=True)

def run_nmap_scan(target: str, fast: bool = True) -> str:
    """
    Optimized Nmap scan:
    fast=True  → quick scan (recommended)
    fast=False → deep scan (slower)
    """
    xml_file = os.path.join(SCAN_DIR, f'{target}.xml')

    if fast:
        cmd = ['nmap', '-Pn', '-T4', '--top-ports', '100', '-oX', xml_file, target]
    else:
        cmd = ['nmap', '-Pn', '-sV', '-T3', '-oX', xml_file, target]

    subprocess.run(cmd, capture_output=True)
    return xml_file


def parse_nmap_xml(xml_file):
    if not os.path.exists(xml_file):
        return []

    try:
        root = ET.parse(xml_file).getroot()
    except:
        return []

    rows = []

    for host in root.findall('host'):
        ip = host.find('address').get('addr', 'unknown')

        for port in host.findall('.//port'):
            state = port.find('state').get('state', 'unknown')

            if state not in ['open', 'filtered']:
                continue

            service = port.find('service')

            rows.append({
                'ip': ip,
                'port': port.get('portid'),
                'service': service.get('name', 'unknown') if service is not None else 'unknown',
                'state': state
            })

    return rows