# app/service/service_anomalies.py
from app.utils.env_vars import PATHS
from qa.contact_anomaly_classifier import classify_contacts_jsonl


def get_contact_anomalies(jsonl_path: str = None):
    """
    Returns only the high‑level anomalies:
    {
        "too_many_phones": [...],
        "too_many_socials": [...],
        "socials_mismatch": [...],
    }
    """
    # jsonl_path is optional; classifier has its own default
    report = classify_contacts_jsonl(jsonl_path) if jsonl_path else classify_contacts_jsonl()

    return {
        "too_many_phones": report.get("too_many_phones", []),
        "too_many_socials": report.get("too_many_socials", []),
        "socials_mismatch": report.get("socials_mismatch", []),
    }
