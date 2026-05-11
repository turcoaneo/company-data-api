# tests/utils/test_text_phone_extractor.py

from selectolax.parser import HTMLParser

from crawler.util.text_phone_extractor import extract_text_phones


class TestTextPhoneExtractor:

    def test_simple_us_number(self):
        dom = HTMLParser("<p>Call us at (202) 714-2785</p>")
        result = extract_text_phones(dom)
        assert result == ["2027142785"]

    def test_multiple_numbers(self):
        dom = HTMLParser("""
            <div>
                (229) 436-9620<br>
                229-344-5037
            </div>
        """)
        result = extract_text_phones(dom)
        assert "2294369620" in result
        assert "2293445037" in result
        assert len(result) == 2

    def test_international_number(self):
        dom = HTMLParser("<p>Office: +49 (30) 1234 5678</p>")
        result = extract_text_phones(dom)
        assert result == ["+493012345678"]

    def test_reject_long_digit_only(self):
        dom = HTMLParser("""
            <div>
                id="block-yui_3_17_2_25_1516652858592_24920"
            </div>
        """)
        result = extract_text_phones(dom)
        assert result == []

    def test_ignore_script_and_style(self):
        dom = HTMLParser("""
        <html>
            <script>var x = "(415) 555-1234";</script>
            <style>.cls { content: "818-422-3831"; }</style>
            <p>Real: (415) 555-1234</p>
        </html>
        """)
        result = extract_text_phones(dom)
        assert result == ["4155551234"]

    def test_parenthesized_plus_prefix(self):
        dom = HTMLParser("<p>(+40) 123-456-789</p>")
        result = extract_text_phones(dom)
        assert result == ["+40123456789"]
