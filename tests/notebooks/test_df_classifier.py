from notebooks.df_classifier import DFClassifier

feature_cols = [
    "num_internal_links",
    "entropy",
    "text_density",
    "heading_count",
    "external_links",
    "is_empty_html",
    "img_count",
    "script_count",
    "nav_present",
    "meta_count",
    "stylesheet_count",
    "has_body_content",
    "scarked_flag",
]


class TestDFClassifierMinimal:

    # -----------------------------
    # detect_body_content() tests
    # -----------------------------

    def test_detect_body_empty_html(self):
        clf = DFClassifier("example.com", "", feature_cols)
        assert clf.detect_body_content() == 0

    def test_detect_body_js_redirect(self):
        html = "<html><head><script>window.onload=function(){}</script></head></html>"
        clf = DFClassifier("ghost.com", html, feature_cols)
        assert clf.detect_body_content() == 0

    def test_detect_body_head_only(self):
        html = "<head><meta name='description' content='Test'></head>"
        clf = DFClassifier("ghost.com", html, feature_cols)
        assert clf.detect_body_content() == 0

    def test_detect_body_meaningless_tags(self):
        # <h1></h1> with NO text should NOT count as body content
        html = "<title></title><h1></h1>"
        clf = DFClassifier("ghost.com", html, feature_cols)
        assert clf.detect_body_content() == 0

    def test_detect_body_meaningful_tags(self):
        # <h1>Hello</h1> SHOULD count as body content
        html = "<h1>Hello</h1>"
        clf = DFClassifier("mysite.com", html, feature_cols)
        assert clf.detect_body_content() == 1

    def test_detect_body_real_body(self):
        html = "<body><p>Hello world</p></body>"
        clf = DFClassifier("mysite.com", html, feature_cols)
        assert clf.detect_body_content() == 1

    # -----------------------------
    # extract_features() tests
    # -----------------------------

    def test_empty_html(self):
        clf = DFClassifier("example.com", "", feature_cols)
        feats = clf.extract_features()
        assert feats["is_empty_html"] == 1
        assert feats["has_body_content"] == 0
        assert feats["scarked_flag"] == 1

    def test_js_redirect_only(self):
        html = "<html><head><script>window.onload=function(){}</script></head></html>"
        clf = DFClassifier("ghost.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["has_body_content"] == 0
        assert feats["scarked_flag"] == 1

    def test_head_only(self):
        html = "<head><meta name='description' content='Test'></head>"
        clf = DFClassifier("ghost.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["has_body_content"] == 0
        assert feats["scarked_flag"] == 1

    def test_meaningless_tags(self):
        html = "<title></title><h1></h1>"
        clf = DFClassifier("ghost.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["has_body_content"] == 0
        assert feats["scarked_flag"] == 1

    def test_real_body(self):
        html = "<body><h1>Hello</h1><p>World</p></body>"
        clf = DFClassifier("mysite.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["has_body_content"] == 1
        assert feats["scarked_flag"] == 0

    def test_registrar_ignored(self):
        html = "<title>Buy this domain</title>"
        clf = DFClassifier("sedo.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["scarked_flag"] == 0

    def test_build_feature_row(self):
        html = "<body><h1>Hello</h1></body>"
        row = DFClassifier.build_feature_row("abc.com", html, 1, feature_cols)
        for col in feature_cols:
            assert col in row
