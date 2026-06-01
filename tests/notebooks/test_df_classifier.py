# test_df_classifier.py
from notebooks.df_classifier import DFClassifier


class TestDFClassifier:
    def test_empty_html(self):
        clf = DFClassifier("example.com", "")
        feats = clf.extract_features()
        assert feats["is_empty_html"] == 1
        assert feats["num_internal_links"] == 0

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

    def test_phone_detection(self):
        html = "<p>Call us at +1 (555) 123-4567</p>"
        clf = DFClassifier("my-biz.com", html)
        feats = clf.extract_features()
        assert feats["has_phone"] == 1

    def test_email_detection(self):
        html = "<p>Email: info@my-biz.com</p>"
        clf = DFClassifier("my-biz.com", html)
        feats = clf.extract_features()
        assert feats["has_email"] == 1

    def test_social_detection(self):
        html = '<a href="https://facebook.com/my-biz">FB</a>'
        clf = DFClassifier("my-biz.com", html)
        feats = clf.extract_features()
        assert feats["has_social"] == 1

    def test_parked_keywords(self):
        html = "<p>This domain is for sale on Sedo</p>"
        clf = DFClassifier("ghost.com", html)
        feats = clf.extract_features()
        assert feats["has_parked_keywords"] == 1

    def test_title_matches_domain(self):
        html = "<title>my-biz - Home</title>"
        clf = DFClassifier("my-biz.com", html)
        feats = clf.extract_features()
        assert feats["title_matches_domain"] == 1

    def test_build_feature_row_basic(self):
        html = "<title>my-biz - Home</title><p>Email: info@my-biz.com</p>"
        row = DFClassifier.build_feature_row("my-biz.com", html, 0)

        assert row["domain"] == "my-biz.com"
        assert row["label"] == 0
        assert row["has_email"] == 1
        assert row["title_matches_domain"] == 1

    def test_build_feature_row_empty_html(self):
        row = DFClassifier.build_feature_row("ghost.com", "", 1)

        assert row["domain"] == "ghost.com"
        assert row["label"] == 1
        assert row["is_empty_html"] == 1
        assert row["num_internal_links"] == 0
