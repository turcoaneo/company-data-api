# tests/utils/test_text_phone_extractor.py

from selectolax.parser import HTMLParser

from crawler.util.text_phone_extractor import extract_text_phones


class TestTextPhoneExtractor:

    def test_simple_text_dot_phone(self):
        dom = HTMLParser("""
        <p class='font_8 wixui-rich-text__text' style='font-size:15px; line-height:2.5em;'>
        <span style='font-family:lato-light,lato,sans-serif;' class='wixui-rich-text__text'>
        <span style='font-size:20px;' class='wixui-rich-text__text'>470.489.4379</span>
        </span>
        </p>""")
        result = extract_text_phones(dom)
        assert result == ["4704894379"]

    def test_simple_call_us_number(self):
        dom = HTMLParser("<span class=\"backcolor_16 wixui-rich-text__text\">Call 315-339-9038 or email&nbsp;</span>")
        result = extract_text_phones(dom)
        assert result == ["3153399038"]

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

    def test_reject_fake_contact(self):
        dom = HTMLParser("""
            <a href="https://carrettausa.com?referrerPage=ContactUs&refPgId=519758413&SearchTerms=562342590&PCUrl=1">
            <span class="lnkTxt ">562342590</span></a>
        """)
        result = extract_text_phones(dom)
        assert result == []

    def test_reject_fake_link(self):
        dom = HTMLParser("""
            <a href="https://carrettausa.com/ContactUs/?referrerPage=Home&refPgId=519758426&PCUrl=1"  target="_self">
            <span class="lnkTxt ">Contact Us</span>
        """)
        result = extract_text_phones(dom)
        assert result == []

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
