#!/usr/bin/env python3
"""
Teevra NMS Client — BSNL FTTH Subscriber Lookup
Works without Teevra account via /bsnl-teevra/ unauthenticated endpoints.
"""

import sys
import json
import subprocess
import re

BASE_URL = "https://teevra.bsnl.in/bsnl-teevra"
CACERT = "/root/.ccr/ca-bundle.crt"
BEARER = "test123"


def _strip_html(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def query_subscriber(landline: str, circle: str = "MH", ssa: str = "AKL") -> dict:
    """
    Look up FTTH subscriber by landline number.
    landline: STD + number, e.g. "07242992349" (0724 Akola prefix)
    Returns dict with customer_name, address, mobile, plan, port etc.
    """
    cmd = [
        "curl", "-sk", "-X", "POST",
        f"{BASE_URL}/detail_ftth01.php",
        "-H", f"Authorization: Bearer {BEARER}",
        "-H", "Content-Type: application/x-www-form-urlencoded",
        "--data-urlencode", f"userid={landline}",
        "--data-urlencode", f"circle={circle}",
        "--data-urlencode", f"ssa={ssa}",
        "--data-urlencode", "access_level=1",
        "--data-urlencode", "username=client",
        "--data-urlencode", "random_key=abc123",
        "--data-urlencode", "device_id=0000",
    ]
    if CACERT:
        cmd += ["--cacert", CACERT]

    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        data = json.loads(out.strip().lstrip(b"\t "))
        return data
    except Exception as e:
        return {"success": False, "error_log": str(e)}


def query_subscriber_ipbased(landline: str, oltip: str = "10.215.58.58",
                              circle: str = "MH", ssa: str = "AKL") -> dict:
    """
    Look up FTTH subscriber by landline + OLT IP.
    """
    cmd = [
        "curl", "-sk", "-X", "POST",
        f"{BASE_URL}/detail_ftth_ipbased.php",
        "-H", f"Authorization: Bearer {BEARER}",
        "-H", "Content-Type: application/x-www-form-urlencoded",
        "--data-urlencode", f"userid={landline}",
        "--data-urlencode", f"oltip={oltip}",
        "--data-urlencode", "username=client",
        "--data-urlencode", "random_key=abc123",
        "--data-urlencode", "device_id=0000",
    ]
    if CACERT:
        cmd += ["--cacert", CACERT]

    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        data = json.loads(out.strip().lstrip(b"\t "))
        return data
    except Exception as e:
        return {"success": False, "error_log": str(e)}


def print_subscriber_report(data: dict, landline: str):
    if not data.get("success"):
        err = data.get("error_log", "Unknown error")
        print(f"  ✗  {_strip_html(err)}")
        return

    def cell(key): return _strip_html(data.get(key, "--"))

    print(f"  Customer    : {cell('customer_name')}")
    print(f"  Address     : {cell('customer_address')}")
    print(f"  Mobile      : {cell('customer_mobile')}")
    print(f"  Landline    : {cell('ftth_tele')}")
    print(f"  FTTH User   : {cell('ftth_userid')}")
    print(f"  Account     : {cell('ftth_Account')}")
    print(f"  Plan        : {cell('ftth_planname')}")
    print(f"  Bandwidth   : {cell('ftth_bandwidth')}")
    print(f"  OLT Port    : {cell('ftth_port')}  (VLAN/ONU)")
    print(f"  OLT Link    : {cell('ftth_link')}")
    print(f"  ONT TX Pwr  : {cell('ftth_ont_tx_power')}")
    print(f"  ONT RX Pwr  : {cell('ftth_ont_rx_power')}")
    print(f"  BNG Status  : {cell('ftth_bngstatus')}")
    print(f"  BNG Speed   : {cell('ftth_bngspeed')}")
    if data.get("error_log"):
        print(f"  Note        : {_strip_html(data['error_log'])}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 teevra_nms_client.py <landline> [<landline2> ...]")
        print("       landline: full number with STD code, e.g. 07242992349")
        print("\nExamples:")
        print("  python3 teevra_nms_client.py 07242992349")
        print("  python3 teevra_nms_client.py 07242992349 07242459222 07243001234")
        sys.exit(1)

    numbers = sys.argv[1:]
    for num in numbers:
        print(f"\n{'='*60}")
        print(f"Landline: {num}")
        print(f"{'='*60}")
        data = query_subscriber(num)
        print_subscriber_report(data, num)


if __name__ == "__main__":
    main()
