# notebooks/df_classifier.py

import re
from urllib.parse import urlparse

# noinspection PyPackageRequirements
from bs4 import BeautifulSoup

PARKED_KEYWORDS = [
    "buy this domain", "domain for sale", "parked", "aftermarket", "godaddy", "sedo", "afternic", "parkingcrew",
    "bodis", "this domain is available",
]

SCAM_KEYWORDS = [
    "verify your account", "urgent update", "security alert",
    "login required", "confirm your identity",
]

SOCIAL_DOMAINS = [
    "facebook.com", "instagram.com", "linkedin.com",
    "twitter.com", "x.com", "tiktok.com", "youtube.com",
]

PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}")
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


class DFClassifier:
    def __init__(self, domain: str, html: str):
        self.domain = domain
        self.html = html or ""
        self.soup = BeautifulSoup(self.html, "html.parser")

    # -----------------------------
    # Feature extractors
    # -----------------------------
    def extract_visible_text(self):
        for tag in self.soup(["script", "style", "noscript"]):
            tag.extract()
        # text = self.soup.get_text(" ", strip=True)
        text = self.soup.get_text(strip=True, types=tuple()).strip(" ")
        return text

    def count_internal_links(self):
        parsed = urlparse("https://" + self.domain)
        base_domain = parsed.netloc.split(":")[0]

        count = 0
        for a in self.soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/"):
                count += 1
            else:
                host = urlparse(href).hostname
                if host and base_domain in host:
                    count += 1
        return count

    def title_matches_domain(self, text):
        title = (self.soup.title.string or "").lower() if self.soup.title else ""
        domain_root = self.domain.split(".")[0].lower()
        return int(domain_root in title or domain_root in text.lower())

    @staticmethod
    def has_parked_keywords(text):
        t = text.lower()
        return int(any(k in t for k in PARKED_KEYWORDS))

    @staticmethod
    def has_scam_keywords(text):
        t = text.lower()
        return int(any(k in t for k in SCAM_KEYWORDS))

    def has_social(self):
        for a in self.soup.find_all("a", href=True):
            if any(s in a["href"] for s in SOCIAL_DOMAINS):
                return 1
        return 0

    @staticmethod
    def has_phone(text):
        return int(bool(PHONE_RE.search(text)))

    @staticmethod
    def has_email(text):
        return int(bool(EMAIL_RE.search(text)))

    # -----------------------------
    # Main extraction
    # -----------------------------
    def extract_features(self):
        text = self.extract_visible_text()
        words = text.split()

        return {
            "text_len": len(text),
            "num_words": len(words),
            "num_internal_links": self.count_internal_links(),
            "has_phone": self.has_phone(text),
            "has_email": self.has_email(text),
            "has_social": self.has_social(),
            "title_matches_domain": self.title_matches_domain(text),
            "has_parked_keywords": self.has_parked_keywords(text),
            "has_scam_keywords": self.has_scam_keywords(text),
            "is_empty_html": int(len(text) < 50),
        }

    # -----------------------------
    # Static helper: build DF row
    # -----------------------------
    @staticmethod
    def build_feature_row(domain: str, html: str, label: int):
        """
        Convenience method used in notebooks:
        - extracts semantic features
        - attaches domain + label
        - returns a clean dict for DataFrame rows
        """
        clf = DFClassifier(domain, html)
        feats = clf.extract_features()
        feats["domain"] = domain
        feats["label"] = label
        return feats
