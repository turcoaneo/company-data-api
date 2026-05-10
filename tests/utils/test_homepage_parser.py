# tests/utils/test_homepage_parser.py

from crawler.util.homepage_parser import parse_homepage

HTML = """
<html>
  <body>
    <a href="tel:+123456789">Call</a>
    <p>+134567890"</p>
    <div class="sqs-block-button-container">
        <a href='https://facebook.com/company'>Facebook</a>
    </div>
  </body>
</html>
"""


class TestHomepageParser:

    def test_parse_homepage(self):
        result = parse_homepage("https://example.com", HTML)
        assert "+123456789" in result["phones"]
        assert any("facebook.com" in s for s in result["socials"])
