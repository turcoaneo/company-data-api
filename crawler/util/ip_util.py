# crawler/util/ip_util.py

import requests


def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=3).text.strip()
    except Exception as e:
        from app.utils.logger_util import get_logger
        logger = get_logger()
        logger.error(f"Cannot return IP: {e}")
        return "unknown"


def get_isp_info():
    """
    Returns a dict: {"ip": "...", "org": "...", "asn": "..."}
    Uses ipinfo.io which provides ASN + ISP org for free.
    """
    try:
        data = requests.get("https://ipinfo.io/json", timeout=3).json()
        return {
            "ip": data.get("ip", "unknown"),
            "org": data.get("org", "unknown"),  # e.g. "AS12345 RCS-RDS"
            "asn": data.get("asn", "unknown"),  # sometimes present
        }
    except Exception as e:
        from app.utils.logger_util import get_logger
        logger = get_logger()
        logger.error(f"Cannot return ISP info: {e}")
        return {"ip": "unknown", "org": "unknown", "asn": "unknown"}
