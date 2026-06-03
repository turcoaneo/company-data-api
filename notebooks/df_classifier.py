# notebooks/df_classifier.py

import math
from collections import Counter
from urllib.parse import urlparse
# noinspection PyPackageRequirements
from bs4 import BeautifulSoup

PARKED_KEYWORDS = [
    "buy this domain", "domain for sale", "parked", "aftermarket",
    "godaddy", "sedo", "afternic", "parkingcrew", "bodis",
    "this domain is available", "get this domain",
]

SCAM_KEYWORDS = [
    "verify your account", "urgent update", "security alert",
    "login required", "confirm your identity",
]

REGISTRAR_DOMAINS = [
    "sedo.com", "godaddy.com", "afternic.com",
    "parkingcrew.com", "bodis.com", "namecheap.com"
]


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
    # Extract ALL text sources
    # -----------------------------------------------------
    def extract_all_text(self):
        parts = [self.extract_visible_text()]

        # visible text

        # title
        if self.soup.title and self.soup.title.string:
            parts.append(self.soup.title.string)

        # meta tags
        for m in self.soup.find_all("meta"):
            if m.get("content"):
                parts.append(m["content"])

        # noscript
        for ns in self.soup.find_all("noscript"):
            parts.append(ns.get_text(strip=True, types=tuple()).strip(" "))

        return " ".join(parts).lower()

    # -----------------------------------------------------
    # Visible text
    # -----------------------------------------------------
    def extract_visible_text(self):
        soup_copy = BeautifulSoup(str(self.soup), "html.parser")
        for tag in soup_copy(["script", "style", "noscript"]):
            tag.extract()
        return soup_copy.get_text(strip=True, types=tuple()).strip(" ")

    # -----------------------------------------------------
    # NEW: Robust body-content detector
    # -----------------------------------------------------
    def detect_body_content(self):
        html_lower = self.html.lower()

        # 1. If HTML literally contains a <body> tag
        if "<body" in html_lower:
            body = self.soup.body
            if body:
                text = body.get_text(strip=True)
                if text:
                    return 1
            return 0

        # 2. No <body> tag → check meaningful tags WITH text
        meaningful_tags = ["p", "h1", "h2", "h3", "div", "section", "article"]
        for tag in meaningful_tags:
            el = self.soup.find(tag)
            if el and el.get_text(strip=True):
                return 1

        # 3. No meaningful content
        return 0

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
        return int(any(k in text for k in PARKED_KEYWORDS))

    @staticmethod
    def has_scam_keywords(text):
        return int(any(k in text for k in SCAM_KEYWORDS))

    def is_registrar_domain(self):
        return int(any(r in self.domain for r in REGISTRAR_DOMAINS))

    # -----------------------------------------------------
    # Main extraction
    # -----------------------------------------------------
    def extract_features(self):
        all_text = self.extract_all_text()
        visible_text = self.extract_visible_text()

        words = visible_text.split()
        text_len = len(visible_text)
        num_words = len(words)

        entropy = text_entropy(visible_text)
        text_density = num_words / text_len if text_len > 0 else 0.0
        heading_count = len(self.soup.find_all(["h1", "h2", "h3"]))

        # external links
        external_links = 0
        for a in self.soup.find_all("a", href=True):
            host = urlparse(a["href"]).hostname
            if host and self.domain not in host:
                external_links += 1

        # NEW: robust body detector
        has_body_content = self.detect_body_content()

        # NEW unified flag
        if self.is_registrar_domain():
            scarked_flag = 0
        else:
            scarked_flag = int(
                self.has_parked_keywords(all_text) or
                self.has_scam_keywords(all_text) or
                (has_body_content == 0)
            )

        # structural features
        img_count = len(self.soup.find_all("img"))
        script_count = len(self.soup.find_all("script"))
        nav_present = int(bool(self.soup.find("nav")))
        meta_count = len(self.soup.find_all("meta"))
        stylesheet_count = len(self.soup.find_all("link", rel="stylesheet"))

        return {
            self.feature_cols[0]: entropy,
            self.feature_cols[1]: text_density,
            # self.feature_cols[2]: self.count_internal_links(),
            # self.feature_cols[3]: heading_count,
            # self.feature_cols[4]: external_links,
            # self.feature_cols[5]: int(text_len < 50),
            # self.feature_cols[6]: img_count,
            # self.feature_cols[7]: script_count,
            # self.feature_cols[8]: nav_present,
            # self.feature_cols[9]: meta_count,
            # self.feature_cols[10]: stylesheet_count,
            # self.feature_cols[11]: has_body_content,
            # self.feature_cols[12]: scarked_flag,
            self.feature_cols[2]: has_body_content,
            self.feature_cols[3]: scarked_flag,
        }

    @staticmethod
    def build_feature_row(domain: str, html: str, label: int, feature_cols: list[str]):
        clf = DFClassifier(domain, html, feature_cols)
        feats = clf.extract_features()
        feats["domain"] = domain
        feats["label"] = label
        return feats
