# test_df_classifier.py
from notebooks.df_classifier import DFClassifier


class TestDFClassifierMinimal:
    def test_empty_html(self):
        clf = DFClassifier("example.com", "")
        feats = clf.extract_features()
        assert feats["is_empty_html"] == 1
        assert feats["num_internal_links"] == 0
        assert feats["entropy"] == 0.0

    def test_internal_links(self):
        html = """
        <html><body>
        <a href="/about">About</a>
        <a href="https://example.com/contact">Contact</a>
        </body></html>
        """
        clf = DFClassifier("example.com", html)
        feats = clf.extract_features()
        assert feats["num_internal_links"] == 2

    def test_heading_count(self):
        html = "<h1>Welcome</h1><h2>About</h2>"
        clf = DFClassifier("mysite.com", html)
        feats = clf.extract_features()
        assert feats["heading_count"] == 2

    def test_external_links(self):
        html = """
        <a href="https://google.com">G</a>
        <a href="/local">Local</a>
        """
        clf = DFClassifier("mysite.com", html)
        feats = clf.extract_features()
        assert feats["external_links"] == 1

    def test_keyword_density(self):
        html = "<p>This domain is for sale on Sedo</p>"
        clf = DFClassifier("ghost.com", html)
        feats = clf.extract_features()
        assert feats["keyword_density"] > 0

    def test_build_feature_row(self):
        html = "<h1>Hello</h1>"
        row = DFClassifier.build_feature_row("abc.com", html, 1)
        assert row["domain"] == "abc.com"
        assert row["label"] == 1
        assert "entropy" in row
        assert "text_density" in row
        assert "heading_count" in row
