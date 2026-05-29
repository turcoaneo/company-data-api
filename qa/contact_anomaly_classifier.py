# qa/contact_anomaly_classifier.py

import json
import re
from collections import defaultdict

from app.utils.file_loader import FileLoader
from app.utils.logger_util import get_logger
from app.utils.timing_util import elapsed_time

YOUTUBE_DOMAINS = ("youtube.com", "youtu.be")

logger = get_logger()


def normalize_token(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def extract_tokens(domain: str, company_name: str | None) -> set[str]:
    tokens = set()

    # Domain tokens
    base = domain.split(".")[0]
    norm_base = normalize_token(base)
    tokens.add(norm_base)

    # Split on hyphens/underscores
    for part in re.split(r"[-_]", base):
        part_norm = normalize_token(part)
        if part_norm:
            tokens.add(part_norm)

    # Company name tokens
    if company_name:
        cleaned = normalize_token(company_name)
        tokens.add(cleaned)
        for part in company_name.split():
            part_norm = normalize_token(part)
            if part_norm:
                tokens.add(part_norm)

    return {t for t in tokens if len(t) >= 3}


def social_matches_company(social_url: str, tokens: set[str]) -> bool:
    s = normalize_token(social_url)
    return any(t in s for t in tokens)


def _is_youtube(url: str) -> bool:
    u = url.lower()
    return any(d in u for d in YOUTUBE_DOMAINS)


@elapsed_time("classify_contacts_jsonl")
def classify_contacts_jsonl(
        jsonl_path: str = "results/top_result.jsonl",
        threshold_phones: int = 5,
        threshold_socials: int = 5,
        report_path: str = "qa/classify_contacts_report.json",
):
    """
    Returns anomalies AND writes a detailed JSON report:
    {
        "too_many_phones": [...],
        "too_many_socials": [...],
        "socials_mismatch": [...],
        "details": {
            "domain.com": {
                "phones": [...],
                "socials": [...],
                "company_name": "...",
                "tokens": [...],
                "flags": ["too_many_phones", "socials_mismatch"]
            },
            ...,
        }
    }
    """
    anomalies = defaultdict(list)
    details = {}

    with FileLoader().open_file(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except Exception as e:
                print(f"Error parsing {obj}: {e}")
                continue

            domain = obj.get("domain") or obj.get("url")
            if not domain:
                continue

            phones = obj.get("phones") or []
            socials = obj.get("socials") or []
            company_name = obj.get("company_commercial_name") or ""

            tokens = extract_tokens(domain, company_name)
            flags = []

            # 1. Too many phones
            if len(phones) > threshold_phones:
                anomalies["too_many_phones"].append(domain)
                flags.append("too_many_phones")

            # 2. Too many socials
            if len(socials) > threshold_socials:
                anomalies["too_many_socials"].append(domain)
                flags.append("too_many_socials")

            # 3. Social mismatch
            mismatch = False
            for s in socials:
                if _is_youtube(s):
                    continue  # skip YouTube links entirely
                if not social_matches_company(s, tokens):
                    mismatch = True
                    break
            if mismatch:
                anomalies["socials_mismatch"].append(domain)
                flags.append("socials_mismatch")

            details[domain] = {
                "phones": phones,
                "socials": socials,
                "company_name": company_name,
                "tokens": sorted(tokens),
                "flags": flags,
            }

    # Write report
    report = dict(anomalies)
    report["details"] = details

    with FileLoader().open_file(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Contact anomaly report written to {report_path}")

    return report


if __name__ == "__main__":
    result = classify_contacts_jsonl()
    print(result.get("too_many_socials"))
    print(result.get("too_many_phones"))
