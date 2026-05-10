import pytest

from crawler.parser import Parser


class TestParserUnit:

    # -----------------------------
    # TEL: links
    # -----------------------------
    def test_parse_tel_links(self):
        hrefs = ["tel:+401234", "https://x.com", "tel:12345"]
        result = Parser.parse_tel_links(hrefs)
        assert result == ["+401234", "12345"]

    # -----------------------------
    # Plain text phones
    # -----------------------------
    @pytest.mark.parametrize("html,expected", [
        ("<p>Call +40 123 456 789</p>", ["+40 123 456 789"]),
        ("<div>Phone: 021-555-3333</div>", ["021-555-3333"]),
        ("<span>(021)5553333</span>", ["(021)5553333"]),
    ])
    def test_parse_text_phones(self, html, expected):
        result = Parser.parse_text_phones(html)
        for phone in expected:
            assert phone in result


    # -----------------------------
    # Social links
    # -----------------------------
    def test_parse_socials(self):
        html = """
        <html>
            <body>
            <div class="sqs-block-button-container">
                <a href='https://facebook.com/company'>Facebook</a>
            </div>
            <div class="social">
                <a href='https://linkedin.com/company/test'>LinkedIn</a>
            </div>
            <div class="social-unknown">
                <a href='https://example.com'>LinkedIn</a>
            </div>
            </body>
        </html>
        """
        from selectolax.parser import HTMLParser
        tree = HTMLParser(html)
        result = Parser.parse_socials(tree)
        assert any("facebook.com" in s for s in result)
        assert any("linkedin.com" in s for s in result)

    # -----------------------------
    # Merge unique
    # -----------------------------
    def test_merge_unique(self):
        values = ["a", "b", "a", "c"]
        result = Parser.merge_unique(values)
        assert result == ["a", "b", "c"]
