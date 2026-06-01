# notebooks/df_classifier.py

import math
from collections import Counter
from urllib.parse import urlparse
from bs4 import BeautifulSoup

PARKED_KEYWORDS = [
    "buy this domain", "domain for sale", "parked", "aftermarket",
    "godaddy", "sedo", "afternic", "parkingcrew", "bodis",
    "this domain is available",
]

SCAM_KEYWORDS = [
    "verify your account", "urgent update", "security alert",
    "login required", "confirm your identity",
]


# ---------------------------------------------------------
# Utility: Shannon entropy
# ---------------------------------------------------------
def text_entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


class DFClassifier:
    def __init__(self, domain: str, html: str):
        self.domain = domain
        self.html = html or ""
        self.soup = BeautifulSoup(self.html, "html.parser")

    # -----------------------------------------------------
    # Visible text
    # -----------------------------------------------------
    def extract_visible_text(self):
        for tag in self.soup(["script", "style", "noscript"]):
            tag.extract()
        return self.soup.get_text(strip=True, types=tuple()).strip(" ")

    # -----------------------------------------------------
    # Internal links
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # Keyword detectors
    # -----------------------------------------------------
    @staticmethod
    def has_parked_keywords(text):
        t = text.lower()
        return int(any(k in t for k in PARKED_KEYWORDS))

    @staticmethod
    def has_scam_keywords(text):
        t = text.lower()
        return int(any(k in t for k in SCAM_KEYWORDS))

    # -----------------------------------------------------
    # Main extraction — MINIMAL HOMEPAGE‑ROBUST FEATURES
    # -----------------------------------------------------
    def extract_features(self):
        text = self.extract_visible_text()
        words = text.split()
        text_len = len(text)
        num_words = len(words)

        entropy = text_entropy(text)
        text_density = num_words / text_len if text_len > 0 else 0.0
        heading_count = len(self.soup.find_all(["h1", "h2", "h3"]))

        # external links = links NOT pointing to this domain
        external_links = 0
        for a in self.soup.find_all("a", href=True):
            host = urlparse(a["href"]).hostname
            if host and self.domain not in host:
                external_links += 1

        parked = self.has_parked_keywords(text)
        scam = self.has_scam_keywords(text)
        keyword_density = (parked + scam) / (num_words + 1)

        return {
            "num_internal_links": self.count_internal_links(),
            "entropy": entropy,
            "text_density": text_density,
            "heading_count": heading_count,
            "external_links": external_links,
            "keyword_density": keyword_density,
            "is_empty_html": int(text_len < 50),
        }

    # -----------------------------------------------------
    # Static helper for DataFrame rows
    # -----------------------------------------------------
    @staticmethod
    def build_feature_row(domain: str, html: str, label: int):
        clf = DFClassifier(domain, html)
        feats = clf.extract_features()
        feats["domain"] = domain
        feats["label"] = label
        return feats
