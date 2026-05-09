# tests/utils/test_homepage_parser.py

from crawler.util.homepage_parser import parse_homepage

HTML = """
<html>
  <body>
    <a href="tel:+123456789">Call</a>
    <a href="https://facebook.com/test">FB</a>
  </body>
</html>
"""


class TestHomepageParser:

    def test_parse_homepage(self):
        result = parse_homepage("https://example.com", HTML)
        assert "+123456789" in result["phones"]
        assert any("facebook.com" in s for s in result["socials"])
