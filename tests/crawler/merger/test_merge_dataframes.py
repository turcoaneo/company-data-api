# /tests/crawler/merger/test_merge_dataframes.py

# noinspection PyPackageRequirements
import pandas as pd
import pytest

from crawler.merge_results import merge_dataframes


class TestMergeDataframes:

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("wine.com", "wine.com"),
            ("www.wine.com", "wine.com"),
            ("WWW.WINE.COM", "wine.com"),
            ("w.wine.com", "w.wine.com"),  # must NOT strip the leading "w"
            ("ww.wine.com", "ww.wine.com"),  # must NOT strip "ww."
            ("www1.wine.com", "www1.wine.com"),  # must NOT strip "www1."
            ("www.w.wine.com", "w.wine.com"),  # only the first www. is removed
            ("www.www.wine.com", "www.wine.com"),  # again, only the first www.
        ]
    )
    def test_normalize_domain_series(self, raw, expected):
        df_input = pd.DataFrame({
            "domain": [raw],
            "company_commercial_name": ["Wine Co"]
        })

        df_results = pd.DataFrame({
            "domain": [expected],
            "phones": [["123"]]
        })

        merged = merge_dataframes(df_input, df_results)

        assert merged.loc[0, "domain"] == expected
        assert merged.loc[0, "company_commercial_name"] == "Wine Co"

    def test_merge_handles_www_in_input(self):
        df_input = pd.DataFrame({
            "domain": ["www.wine.com"],
            "company_commercial_name": ["Example Co"]
        })

        df_results = pd.DataFrame({
            "domain": ["wine.com"],
            "phones": [["123"]],
            "socials": [["fb.com/wine"]]
        })

        merged = merge_dataframes(df_input, df_results)

        assert merged.loc[0, "domain"] == "wine.com"
        assert merged.loc[0, "phones"] == ["123"]
        assert merged.loc[0, "socials"] == ["fb.com/wine"]

    def test_merge_handles_www_in_results(self):
        df_input = pd.DataFrame({
            "domain": ["hero.com"],
            "company_commercial_name": ["Hero Co"]
        })

        df_results = pd.DataFrame({
            "domain": ["www.hero.com"],
            "phones": [["123"]],
            "socials": [["fb.com/hero"]]
        })

        merged = merge_dataframes(df_input, df_results)

        assert merged.loc[0, "domain"] == "hero.com"
        assert merged.loc[0, "phones"] == ["123"]
        assert merged.loc[0, "socials"] == ["fb.com/hero"]

    def test_merge_includes_scraped_fields(self):
        df_input = pd.DataFrame({
            "domain": ["example.com"],
            "company_commercial_name": ["Example Co"]
        })

        df_results = pd.DataFrame({
            "domain": ["example.com"],
            "phones": [["123"]],
            "socials": [["fb.com/example"]]
        })

        merged = merge_dataframes(df_input, df_results)

        assert merged.loc[0, "phones"] == ["123"]
        assert merged.loc[0, "socials"] == ["fb.com/example"]

    def test_missing_fields_become_empty_lists(self):
        df_input = pd.DataFrame({"domain": ["example.com"]})
        df_results = pd.DataFrame({"domain": ["example.com"]})

        merged = merge_dataframes(df_input, df_results)

        assert merged.loc[0, "phones"] == []
        assert merged.loc[0, "socials"] == []
