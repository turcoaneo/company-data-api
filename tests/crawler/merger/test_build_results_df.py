# /tests/crawler/merger/test_load_input_df.py
from crawler.merge_results import build_results_df


class TestBuildResultsDf:

    def test_build_results_df_basic(self):
        results = [
            {"url": "https://example.com", "phones": ["123"]},
            {"url": "test.com", "emails": ["a@test.com"]},
        ]

        df = build_results_df(results)

        assert list(df.columns) == ["url", "phones", "emails", "domain"]
        assert df.loc[0, "domain"] == "example.com"
        assert df.loc[1, "domain"] == "test.com"

    def test_missing_url(self):
        results = [{"phones": ["123"]}]
        df = build_results_df(results)

        assert df.loc[0, "url"] is None
        assert df.loc[0, "domain"] == ""
