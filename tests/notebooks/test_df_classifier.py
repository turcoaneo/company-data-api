# test_df_classifier.py
from notebooks.df_classifier import DFClassifier

feature_cols = [
    "num_internal_links",
    "entropy",
    "text_density",
    "heading_count",
    "external_links",
    "keyword_density",
    "is_empty_html",
    "img_count",
    "script_count",
    "nav_present",
]


class TestDFClassifierMinimal:
    def test_empty_html(self):
        clf = DFClassifier("example.com", "", feature_cols)
        feats = clf.extract_features()
        assert feats["is_empty_html"] == 1
        assert feats["num_internal_links"] == 0
        assert feats["entropy"] == 0.0
        assert feats["img_count"] == 0
        assert feats["script_count"] == 0
        assert feats["nav_present"] == 0

    def test_internal_links(self):
        html = """
        <html><body>
        <a href="/about">About</a>
        <a href="https://example.com/contact">Contact</a>
        </body></html>
        """
        clf = DFClassifier("example.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["num_internal_links"] == 2

    def test_heading_count(self):
        html = "<h1>Welcome</h1><h2>About</h2>"
        clf = DFClassifier("mysite.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["heading_count"] == 2

    def test_external_links(self):
        html = """
        <a href="https://google.com">G</a>
        <a href="/local">Local</a>
        """
        clf = DFClassifier("mysite.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["external_links"] == 1

    def test_keyword_density(self):
        html = "<p>This domain is for sale on Sedo</p>"
        clf = DFClassifier("ghost.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["keyword_density"] > 0

    def test_img_count(self):
        html = "<img src='a.jpg'><img src='b.png'>"
        clf = DFClassifier("mysite.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["img_count"] == 2

    def test_script_count(self):
        html = "<script>console.log(1)</script><script></script>"
        clf = DFClassifier("mysite.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["script_count"] == 2

    def test_nav_present(self):
        html = "<nav><ul><li>Home</li></ul></nav>"
        clf = DFClassifier("mysite.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["nav_present"] == 1

    def test_build_feature_row(self):
        html = "<h1>Hello</h1><img src='x.jpg'><nav></nav>"
        row = DFClassifier.build_feature_row("abc.com", html, 1, feature_cols)
        assert row["domain"] == "abc.com"
        assert row["label"] == 1
        assert "entropy" in row
        assert "img_count" in row
        assert "script_count" in row
        assert "nav_present" in row
