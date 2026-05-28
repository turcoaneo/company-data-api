# matcher/service.py

import meilisearch


class MatcherService:
    def __init__(self, url=None, index_name=None, top_index_name=None):
        # Import env vars lazily (safe for tests)
        if url is None or index_name is None or top_index_name is None:
            from app.utils.env_vars import MEILI
            url = url or MEILI["url"]
            index_name = index_name or MEILI["index"]
            top_index_name = top_index_name or MEILI["top_index"]

        self.client = meilisearch.Client(url)
        self.index = self.client.index(index_name)
        self.top_index = self.client.index(top_index_name)

    # ---------------------------------------------------------
    # MATCH (default index)
    # ---------------------------------------------------------
    def match(self, name=None, website=None, phone=None, facebook=None):
        return self._match_against_index(
            self.index, name=name, website=website, phone=phone, facebook=facebook
        )

    # ---------------------------------------------------------
    # MATCH TOP (top index)
    # ---------------------------------------------------------
    def match_top(self, name=None, website=None, phone=None, facebook=None):
        return self._match_against_index(
            self.top_index, name=name, website=website, phone=phone, facebook=facebook
        )

    # ---------------------------------------------------------
    # INTERNAL: generic match logic
    # ---------------------------------------------------------
    def _match_against_index(self, index, name=None, website=None, phone=None, facebook=None):
        if name:
            hit = self._search_single(index, name, [
                "company_commercial_name",
                "company_legal_name",
                "company_all_available_names",
            ])
            if hit:
                return hit

        if website:
            hit = self._search_single(index, website, ["domain"])
            if hit:
                return hit

        if phone:
            hit = self._search_single(index, phone, ["phones"])
            if hit:
                return hit

        if facebook:
            hit = self._search_single(index, facebook, ["socials"])
            if hit:
                return hit

        return None

    # ---------------------------------------------------------
    # SAMPLE MATCH (default index)
    # ---------------------------------------------------------
    def match_sample(self):
        return self._match_sample_against_index(self.index)

    # ---------------------------------------------------------
    # SAMPLE MATCH (top index)
    # ---------------------------------------------------------
    def match_sample_top(self):
        return self._match_sample_against_index(self.top_index)

    # ---------------------------------------------------------
    # INTERNAL: sample matching for any index
    # ---------------------------------------------------------
    def _match_sample_against_index(self, index):
        from app.utils.env_vars import PATHS
        from pathlib import Path
        input_path = Path(PATHS["path_api_input"])
        assert input_path.exists(), "Sample CSV missing"

        import csv
        results = []

        from app.utils.file_loader import FileLoader
        with FileLoader().open_file(str(input_path), "r", newline="", encoding="utf-8") as f:
            reader: csv.DictReader = csv.DictReader(f)
            for row in reader:
                payload = {
                    "name": row.get("input name") or None,
                    "phone": row.get("input phone") or None,
                    "website": row.get("input website") or None,
                    "facebook": row.get("input_facebook") or None,
                }
                hit = self._match_against_index(index, **payload)
                results.append({"input": payload, "output": hit})

        return results

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------
    def search(self, query: str, limit=10):
        return self.index.search(
            query,
            {"limit": limit, "sort": ["phones_count:desc", "socials_count:desc"]},
        )

    # ---------------------------------------------------------
    # SUGGEST
    # ---------------------------------------------------------
    def suggest(self, prefix: str, limit=5):
        return self.index.search(
            prefix,
            {
                "limit": limit,
                "attributesToSearchOn": [
                    "company_commercial_name",
                    "company_legal_name",
                    "company_all_available_names",
                ],
            },
        )

    # ---------------------------------------------------------
    # INTERNAL SEARCH
    # ---------------------------------------------------------
    @staticmethod
    def _search_single(index, query_param: str, fields: list[str]):
        result = index.search(
            query_param,
            {
                "limit": 1,
                "attributesToSearchOn": fields,
                "sort": ["phones_count:desc", "socials_count:desc"],
            },
        )
        return result["hits"][0] if result["hits"] else None

    # ---------------------------------------------------------
    # NORMALIZATION
    # ---------------------------------------------------------
    @staticmethod
    def _normalize_field(value: str | None) -> str | None:
        """Return None for empty, whitespace, or punctuation-only values."""
        if not value:
            return None
        cleaned = value.strip()
        # If no alphanumeric characters → treat as None
        import re
        if not re.search(r"[A-Za-z0-9]", cleaned):
            return None
        return cleaned

    # ---------------------------------------------------------
    # SANITIZED MATCH (default index)
    # ---------------------------------------------------------
    def sanitized_match(self, name=None, website=None, phone=None, facebook=None):
        return self.sanitized_match_against_index(
            self.index,
            name=name,
            website=website,
            phone=phone,
            facebook=facebook,
        )

    # ---------------------------------------------------------
    # SANITIZED MATCH (top index)
    # ---------------------------------------------------------
    def sanitized_match_top(self, name=None, website=None, phone=None, facebook=None):
        return self.sanitized_match_against_index(
            self.top_index,
            name=name,
            website=website,
            phone=phone,
            facebook=facebook,
        )

    # ---------------------------------------------------------
    # INTERNAL: sanitized generic match logic
    # ---------------------------------------------------------
    def sanitized_match_against_index(self, index, name=None, website=None, phone=None, facebook=None):
        name = self._normalize_field(name)
        website = self._normalize_field(website)
        phone = self._normalize_field(phone)
        facebook = self._normalize_field(facebook)

        return self._match_against_index(
            index,
            name=name,
            website=website,
            phone=phone,
            facebook=facebook,
        )
