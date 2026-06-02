# notebooks/df_classifier.py

import math
from collections import Counter
from urllib.parse import urlparse
# noinspection PyPackageRequirements
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
    def __init__(self, domain: str, html: str, feature_cols: list[str]):
        self.domain = domain
        self.html = html or ""
        self.feature_cols = feature_cols
        self.soup = BeautifulSoup(self.html, "html.parser")

    # -----------------------------------------------------
    # Visible text
    # -----------------------------------------------------
    def extract_visible_text(self):
        # Work on a copy, so we don't destroy script tags needed for counting
        soup_copy = BeautifulSoup(str(self.soup), "html.parser")
        for tag in soup_copy(["script", "style", "noscript"]):
            tag.extract()
        return soup_copy.get_text(strip=True, types=tuple()).strip(" ")

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
    # Main extraction — MINIMAL + NEW STRUCTURAL FEATURES
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

        # NEW FEATURES
        img_count = len(self.soup.find_all("img"))
        script_count = len(self.soup.find_all("script"))
        nav_present = int(bool(self.soup.find("nav")))

        return {
            self.feature_cols[0]: self.count_internal_links(),
            self.feature_cols[1]: entropy,
            self.feature_cols[2]: text_density,
            self.feature_cols[3]: heading_count,
            self.feature_cols[4]: external_links,
            self.feature_cols[5]: keyword_density,
            self.feature_cols[6]: int(text_len < 50),

            # NEW structural features
            self.feature_cols[7]: img_count,
            self.feature_cols[8]: script_count,
            self.feature_cols[9]: nav_present,
        }

    # -----------------------------------------------------
    # Static helper for DataFrame rows
    # -----------------------------------------------------
    @staticmethod
    def build_feature_row(domain: str, html: str, label: int, feature_cols: list[str]) -> dict[str, int | float]:
        clf = DFClassifier(domain, html, feature_cols)
        feats = clf.extract_features()
        feats["domain"] = domain
        feats["label"] = label
        return feats
