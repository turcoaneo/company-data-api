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
        html = """
        <head>
            <meta name="description" content="Test">
            <title>Buy this domain</title>
        </head>
        """
        clf = DFClassifier("ghost.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["has_body_content"] == 0
        assert feats["scarked_flag"] == 1

    def test_registrar_ignored(self):
        html = "<title>Buy this domain</title>"
        clf = DFClassifier("sedo.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["scarked_flag"] == 0

    def test_real_body(self):
        html = "<body><h1>Hello</h1><p>World</p></body>"
        clf = DFClassifier("mysite.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["has_body_content"] == 1
        assert feats["scarked_flag"] == 0

    def test_real_body_without_body_tag(self):
        # meaningful tags but no <body> tag
        html = "<div>Hello</div><h1>World</h1>"
        clf = DFClassifier("mysite.com", html, feature_cols)
        feats = clf.extract_features()
        assert feats["has_body_content"] == 1
        assert feats["scarked_flag"] == 0

    def test_build_feature_row(self):
        html = "<body><h1>Hello</h1></body>"
        row = DFClassifier.build_feature_row("abc.com", html, 1, feature_cols)
        for col in feature_cols:
            assert col in row
