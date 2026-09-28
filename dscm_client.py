"""
BSNL DSCM franchisee API client for copper→FTTH subscriber migrations.
Franchise 307710 — Akola, Maharashtra (SSA: AKL, Exchange: AKLAKC).

All ding/ endpoints work without SESSION cookie — only orgId/areaId cookies needed.
For transactional endpoints (reconnect, activate, plan change) a fresh SESSION is
required. Get one via DSCMClient.login(plaintext_password) or by intercepting the
DSCM mobile app with Charles Proxy / HTTP Toolkit.

API base: https://wsc.cdr.bsnl.co.in/portal/drm/api
"""
import json
import sys
import os
import base64
import requests
from requests.exceptions import RequestException
from typing import Optional

try:
    from Crypto.Cipher import AES
    _AES_AVAILABLE = True
except ImportError:
    _AES_AVAILABLE = False

# Proxy CA bundle for this environment (cloud container)
_CA = os.environ.get("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
if not os.path.exists(_CA):
    _CA = True  # Use system CA

API_BASE = "https://wsc.cdr.bsnl.co.in/portal/drm/api"

# Franchise 307710 default context
DEFAULT_FRANCHISE = {
    "userId":  "307710",
    "orgId":   "307710",
    "areaId":  "178388",
    "exchangeCode": "AKLAKC",
}

# DSCM app AES-CBC encryption for passwords
_AES_KEY = b"4EGJ6D9CFFA2GG9A"
_AES_IV  = bytes([1, 2, 3, 4, 5, 6, 7, 8, 0, 0, 0, 0, 0, 0, 0, 0])


def encrypt_password(plaintext: str) -> str:
    """Encrypt DSCM password using AES-CBC (same as DSCM mobile app)."""
    if not _AES_AVAILABLE:
        raise RuntimeError("pycryptodome required: pip install pycryptodome")
    cipher = AES.new(_AES_KEY, AES.MODE_CBC, _AES_IV)
    pad_len = 16 - (len(plaintext) % 16)
    padded = plaintext.encode() + bytes([pad_len] * pad_len)
    return base64.b64encode(cipher.encrypt(padded)).decode()


class DSCMClient:
    """
    Client for BSNL DSCM DRM franchisee API.

    Usage:
        client = DSCMClient()
        results = client.search_customer(phone="09921326699")
        detail = client.get_subscriber_detail(subs_id="...")
    """

    def __init__(self, franchise: dict = None, session_cookie: str = None):
        self.franchise = franchise or DEFAULT_FRANCHISE
        self._session = requests.Session()
        self._session.verify = _CA
        self._session.headers.update({"Content-Type": "application/json"})
        # orgId/areaId cookies bypass SESSION requirement on ding/ endpoints
        self._session.cookies.set("userId", self.franchise["userId"])
        self._session.cookies.set("orgId",  self.franchise["orgId"])
        self._session.cookies.set("areaId", self.franchise["areaId"])
        if session_cookie:
            self._session.cookies.set("SESSION", session_cookie)

    def login(self, plaintext_password: str, login_name: str = None) -> Optional[str]:
        """
        Authenticate with DSCM API.
        Returns SESSION cookie string on success, None on failure.
        The password is AES-CBC encrypted using the DSCM app's key before sending.

        Note: The DRM login endpoint at /portal/drm/api/login queries the Oracle STAFF
        table. If 2000+ records match (no loginName filter), it returns an error.
        Provide the exact staff/franchise account name to narrow the query.
        """
        encrypted = encrypt_password(plaintext_password)
        resp = self._post("login", {
            "loginName": login_name or self.franchise["userId"],
            "loginPwd":  encrypted,
            "orgId":     self.franchise["orgId"],
        })
        if resp.get("code") == "200":
            data = resp.get("data") or {}
            session = data.get("sessionId") or data.get("session") or data.get("token")
            if session:
                self._session.cookies.set("SESSION", session)
            return session
        return None

    def _post(self, endpoint: str, body: dict) -> dict:
        url = f"{API_BASE}/{endpoint}"
        try:
            r = self._session.post(url, json=body, timeout=30)
            r.raise_for_status()
            return r.json()
        except RequestException as e:
            return {"error": str(e), "endpoint": endpoint}

    # ── Customer search ──────────────────────────────────────────────────────

    def search_customer(self, name: str = "", phone: str = "",
                        cert_nbr: str = "", cust_code: str = "") -> list[dict]:
        """Search customers. At least one filter required."""
        body = {"custName": name}
        if phone:
            body["phoneNbr"] = phone
        if cert_nbr:
            body["certNbr"] = cert_nbr
        if cust_code:
            body["custCode"] = cust_code
        resp = self._post("ding/custService/qryCustListBsnl", body)
        if resp.get("code") == "200":
            return (resp.get("data") or {}).get("custDtoList") or []
        return []

    def get_customer_detail(self, cust_id: str) -> Optional[dict]:
        """Get full customer record including addresses and subscriber list."""
        resp = self._post("ding/custService/qryCustDetailBsnl", {"custId": cust_id})
        if resp.get("code") == "200":
            return resp.get("data")
        return None

    # ── Subscriber / service ─────────────────────────────────────────────────

    def get_subscriber_detail(self, subs_id: str) -> Optional[dict]:
        """Full subscriber detail: plan, status, OLT port, addresses."""
        resp = self._post("ding/subsService/qrySubsDetailBsnl", {"subsId": subs_id})
        if resp.get("code") == "200":
            return resp.get("data")
        return None

    def check_service_area(self, phone: str = "",
                           org_id: str = None, area_id: str = None) -> dict:
        """
        Check if FTTH service is available for a number in this franchise area.
        Returns the raw response — code '200' means in-area.
        """
        oid = org_id or self.franchise["orgId"]
        aid = area_id or self.franchise["areaId"]
        url = (f"{API_BASE}/ding/channel/frServiceInfoCheck"
               f"?orgId={oid}&areaId={aid}")
        body = {}
        if phone:
            body["phoneNbr"] = phone
        try:
            r = self._session.post(url, json=body, timeout=60)
            r.raise_for_status()
            return r.json()
        except RequestException as e:
            return {"error": str(e)}

    def list_franchise_subscribers(self, page: int = 1,
                                   page_size: int = 50) -> dict:
        """
        List all FTTH subscribers bound to this franchise.
        Returns {"total": N, "list": [...]} or error dict.
        """
        resp = self._post("ding/channel/qryOrgBindSubsList", {
            "exchangeCode": self.franchise["exchangeCode"],
            "pageNo":   page,
            "pageSize": page_size,
        })
        if resp.get("code") == "200":
            data = resp.get("data") or {}
            page_dto = data.get("pageDto") or {}
            total = (page_dto.get("totalRecord") or
                     data.get("totalCount") or 0)
            subs = (data.get("orgSubsBindRelaDtoList") or
                    data.get("subsDtoList") or [])
            return {"total": total, "list": subs}
        return {"error": resp.get("message", "unknown"), "raw": resp}

    # ── Transactional (require valid SESSION) ─────────────────────────────────

    def reconnect_subscriber(self, subs_id: str, reason: str = "Customer request") -> dict:
        """Resume a suspended FTTH subscriber."""
        return self._post("ding/subsService/reconnectionBsnl", {
            "subsId": subs_id,
            "remark": reason,
        })

    def activate_subscriber(self, subs_id: str, **kwargs) -> dict:
        """Activate a new FTTH subscriber (requires fresh SESSION)."""
        body = {"subsId": subs_id, **kwargs}
        return self._post("ding/subsService/activationBsnl", body)

    def change_plan(self, subs_id: str, new_plan_id: str) -> dict:
        """Migrate subscriber to a different plan."""
        return self._post("ding/subsService/changePlanBsnl", {
            "subsId": subs_id,
            "planId": new_plan_id,
        })

    # ── High-level workflows ──────────────────────────────────────────────────

    def find_subscriber_by_phone(self, phone: str) -> Optional[dict]:
        """
        Given a landline or mobile number, find the subscriber record.
        Returns dict with keys: custId, custName, subsId, subsStatus, planName, ...
        """
        # Normalize: strip spaces/dashes
        clean = phone.replace(" ", "").replace("-", "")
        if clean.startswith("0"):
            clean = clean  # keep STD code
        results = self.search_customer(phone=clean)
        if not results:
            return None
        cust = results[0]
        cust_id = cust.get("custId")
        detail = self.get_customer_detail(cust_id) if cust_id else None
        if not detail:
            return cust
        subs_list = (detail.get("custSubsDtoList") or
                     detail.get("subsDtoList") or [])
        if subs_list:
            subs = subs_list[0]
            subs["custName"]   = cust.get("custName")
            subs["mobilePhone"] = cust.get("mobilePhone")
            subs["emailAddr"]  = cust.get("emailAddr")
            return subs
        return {**cust, "noSubs": True}

    def copper_to_ftth_check(self, phone: str) -> dict:
        """
        Pre-migration check for a copper subscriber.
        Returns a summary dict with status/blockers/next steps.
        """
        result = {
            "phone": phone,
            "in_service_area": None,
            "customer_found": None,
            "has_ftth": None,
            "blockers": [],
            "next_steps": [],
        }
        # 1. Service area check
        area_resp = self.check_service_area(phone=phone)
        result["service_area_raw"] = area_resp
        if area_resp.get("code") == "200":
            result["in_service_area"] = True
        else:
            result["in_service_area"] = False
            result["blockers"].append(f"Not in service area: {area_resp.get('message')}")

        # 2. Customer lookup
        subs = self.find_subscriber_by_phone(phone)
        if not subs:
            result["customer_found"] = False
            result["blockers"].append("Customer not found in DSCM — check mobile number")
            return result
        result["customer_found"] = True
        result["customer"] = subs

        # 3. Check if already FTTH
        subs_id = subs.get("subsId")
        if subs_id:
            result["has_ftth"] = True
            detail = self.get_subscriber_detail(subs_id)
            result["subscriber_detail"] = detail
            result["next_steps"].append(
                "Already FTTH — use reconnect_subscriber() if suspended")
        else:
            result["has_ftth"] = False
            result["next_steps"].append(
                "No FTTH subsId found — copper subscriber; proceed with migration")

        return result


# ── CLI ───────────────────────────────────────────────────────────────────────

def _pretty(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def main():
    import argparse
    p = argparse.ArgumentParser(
        description="BSNL DSCM franchisee API client (franchise 307710)")
    sub = p.add_subparsers(dest="cmd", required=True)

    # search
    s = sub.add_parser("search", help="Search customer by phone/name/cert")
    s.add_argument("--phone", default="")
    s.add_argument("--name",  default="")
    s.add_argument("--cert",  default="")

    # detail
    d = sub.add_parser("detail", help="Get subscriber detail by subsId")
    d.add_argument("subs_id")

    # check
    c = sub.add_parser("check",
        help="Full copper→FTTH pre-migration check by phone number")
    c.add_argument("phone")

    # list
    sub.add_parser("list", help="List all franchise FTTH subscribers (page 1)")

    # reconnect
    r = sub.add_parser("reconnect", help="Reconnect a suspended subscriber")
    r.add_argument("subs_id")
    r.add_argument("--session", default="", help="SESSION cookie value")

    # login
    lo = sub.add_parser("login", help="Login to DSCM and print SESSION cookie")
    lo.add_argument("password", help="Plaintext DSCM password (will be AES-encrypted)")
    lo.add_argument("--login-name", default="",
                    help="Staff/franchise account name (default: franchise orgId)")

    args = p.parse_args()
    client = DSCMClient(
        session_cookie=getattr(args, "session", "") or ""
    )

    if args.cmd == "search":
        _pretty(client.search_customer(
            name=args.name, phone=args.phone, cert_nbr=args.cert))

    elif args.cmd == "detail":
        _pretty(client.get_subscriber_detail(args.subs_id))

    elif args.cmd == "check":
        _pretty(client.copper_to_ftth_check(args.phone))

    elif args.cmd == "list":
        result = client.list_franchise_subscribers()
        print(f"Total subscribers: {result.get('total', 0)}")
        for s in (result.get("list") or [])[:10]:
            print(f"  {s.get('subsId','?'):>12}  {s.get('mobilePhone',''):>12}  "
                  f"{s.get('fullAddress','')[:50]}")

    elif args.cmd == "reconnect":
        if not args.session:
            print("ERROR: --session SESSION_COOKIE required for transactional ops")
            sys.exit(1)
        client = DSCMClient(session_cookie=args.session)
        _pretty(client.reconnect_subscriber(args.subs_id))

    elif args.cmd == "login":
        session = client.login(
            args.password,
            login_name=getattr(args, "login_name", "") or ""
        )
        if session:
            print(f"SESSION={session}")
        else:
            print("Login failed — check password and login-name")
            sys.exit(1)


if __name__ == "__main__":
    main()
