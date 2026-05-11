from selectolax.parser import HTMLParser
from crawler.util.semantic_filter import semantic_filter_tel


class TestSemanticFilterTel:

    def test_simple_positive(self):
        html = """
        <div>
            <p>Contact us at <a href="tel:1234567890">1234567890</a></p>
        </div>
        """
        dom = HTMLParser(html)
        result = semantic_filter_tel(dom)
        assert result == ["1234567890"]

    def test_simple_negative(self):
        html = """
        <div>
            <p>State Farm customer service:
               <a href="tel:8005551212">800-555-1212</a>
            </p>
        </div>
        """
        dom = HTMLParser(html)
        result = semantic_filter_tel(dom)
        assert result == []  # dropped

    def test_mixed_positive_and_negative(self):
        html = """
        <div>
            <p>Contact our office:
               <a href="tel:3178733230">(317) 873-3230</a>
            </p>
            <p>External:
               <a href="tel:8557337333">855-733-7333</a>
            </p>
        </div>
        """
        dom = HTMLParser(html)
        result = semantic_filter_tel(dom)
        assert "3178733230" in result
        assert "8557337333" not in result
        assert len(result) == 1

    def test_nested_positive(self):
        html = """
        <div>
            <section>
                <div>
                    <p>Call our team:
                       <a href="tel:2027142785">202-714-2785</a>
                    </p>
                </div>
            </section>
        </div>
        """
        dom = HTMLParser(html)
        result = semantic_filter_tel(dom)
        assert result == ["2027142785"]

    def test_nested_negative(self):
        html = """
        <div>
            <section>
                <div>
                    <p>Legal disclaimer:
                       <a href="tel:9998887777">999-888-7777</a>
                    </p>
                </div>
            </section>
        </div>
        """
        dom = HTMLParser(html)
        result = semantic_filter_tel(dom)
        assert result == []

    def test_multiple_tel_links(self):
        html = """
        <div>
            <p>Contact:
               <a href="tel:1111111111">111-111-1111</a>
            </p>
            <p>Support:
               <a href="tel:2222222222">222-222-2222</a>
            </p>
        </div>
        """
        dom = HTMLParser(html)
        result = semantic_filter_tel(dom)
        assert "1111111111" in result
        assert "2222222222" in result
        assert len(result) == 2

    def test_tel_with_no_context(self):
        html = """
        <div>
            <a href="tel:3333333333">333-333-3333</a>
        </div>
        """
        dom = HTMLParser(html)
        result = semantic_filter_tel(dom)
        # neutral context → score = 0 → keep
        assert result == ["3333333333"]

    def test_tel_in_footer_disclaimer(self):
        html = """
        <footer>
            <p>Privacy policy:
               <a href="tel:4444444444">444-444-4444</a>
            </p>
        </footer>
        """
        dom = HTMLParser(html)
        result = semantic_filter_tel(dom)
        assert result == []  # dropped

    def test_tel_with_parent_but_no_grandparent(self):
        html = """
        <div>
            <a href="tel:5555555555">555-555-5555</a>
        </div>
        """
        dom = HTMLParser(html)
        result = semantic_filter_tel(dom)
        assert result == ["5555555555"]

    def test_tel_with_missing_text(self):
        html = """
        <div>
            <a href="tel:6666666666"></a>
        </div>
        """
        dom = HTMLParser(html)
        result = semantic_filter_tel(dom)
        # no text but no negative context → keep
        assert result == ["6666666666"]

    def test_tel_with_positive_keyword_in_grandparent(self):
        html = """
        <div>
            <section>
                <p>Our company</p>
                <a href="tel:7777777777">777-777-7777</a>
            </section>
        </div>
        """
        dom = HTMLParser(html)
        result = semantic_filter_tel(dom)
        assert result == ["7777777777"]

    def test_tel_with_negative_keyword_in_grandparent(self):
        html = """
        <div>
            <section>
                <p>Insurance claims</p>
                <a href="tel:8888888888">888-888-8888</a>
            </section>
        </div>
        """
        dom = HTMLParser(html)
        result = semantic_filter_tel(dom)
        assert result == []
