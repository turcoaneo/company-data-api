# matcher/service.py

from typing import Optional, Dict, Any
import meilisearch


class MatcherService:
    def __init__(self, url="http://localhost:7700", index_name="companies"):
        self.client = meilisearch.Client(url)
        self.index = self.client.index(index_name)

    # ---------------------------------------------------------
    # 1) MATCH (best single result)
    # ---------------------------------------------------------
    def match(self, name=None, website=None, phone=None, facebook=None) -> Optional[Dict]:
        # 1) Try name first
        if name:
            hit = self._search_single(name, ["company_commercial_name",
                                             "company_legal_name",
                                             "company_all_available_names"])
            if hit:
                return hit

        # 2) Try domain
        if website:
            hit = self._search_single(website, ["domain"])
            if hit:
                return hit

        # 3) Try phone
        if phone:
            hit = self._search_single(phone, ["phones"])
            if hit:
                return hit

        # 4) Try socials
        if facebook:
            hit = self._search_single(facebook, ["socials"])
            if hit:
                return hit

        return None

    # ---------------------------------------------------------
    # 2) SEARCH (multiple results)
    # ---------------------------------------------------------
    def search(self, query: str, limit=10):
        return self.index.search(
            query,
            {
                "limit": limit,
                "sort": ["phones_count:desc", "socials_count:desc"]
            }
        )

    # ---------------------------------------------------------
    # 3) SUGGEST (autocomplete)
    # ---------------------------------------------------------
    def suggest(self, prefix: str, limit=5):
        return self.index.search(
            prefix,
            {
                "limit": limit,
                "attributesToSearchOn": [
                    "company_commercial_name",
                    "company_legal_name",
                    "company_all_available_names"
                ]
            }
        )

    # ---------------------------------------------------------
    # 4) Match all sample inputs
    # ---------------------------------------------------------
    def match_sample(self):
        from app.utils.path_util import get_project_root
        input_path = get_project_root() / "data/api-input-sample.csv"
        assert input_path.exists(), "Sample CSV missing"

        results = []

        with open(input_path, newline="", encoding="utf-8") as f:
            import csv
            reader: csv.DictReader = csv.DictReader(f)

            for row in reader:
                payload = {
                    "name": row.get("input name") or None,
                    "phone": row.get("input phone") or None,
                    "website": row.get("input website") or None,
                    "facebook": row.get("input_facebook") or None,
                }

                hit = self.match(**payload)
                results.append({"input": payload, "output": hit})

        return results

    # ---------------------------------------------------------
    # INTERNAL: weighted single search
    # ---------------------------------------------------------
    def _search_single(self, query: str, fields: list[str]) -> Optional[Dict[str, Any]]:
        result = self.index.search(
            query,
            {
                "limit": 1,
                "attributesToSearchOn": fields,
                "sort": ["phones_count:desc", "socials_count:desc"]
            }
        )
        return result["hits"][0] if result["hits"] else None
