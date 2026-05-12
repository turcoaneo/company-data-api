# tests/utils/test_link_filters.py

from selectolax.parser import HTMLParser
from crawler.util.link_filters import is_semantic, is_garbage, is_low_signal
from crawler.util.semantic_extractor import is_semantic_by_ancestry


class TestLinkFilters:

    def test_semantic(self):
        assert is_semantic("/contact")
        assert is_semantic("/about-us")
        assert not is_semantic("/products")

    def test_garbage(self):
        assert is_garbage("file.pdf")
        assert is_garbage("image.JPG")
        assert not is_garbage("/contact")

    def test_low_signal(self):
        assert is_low_signal("/blog/post")
        assert is_low_signal("/news")
        assert not is_low_signal("/contact")

    # -----------------------------
    # NEW TESTS FOR ANCESTRY LOGIC
    # -----------------------------

    def test_semantic_by_ancestry_inside(self):
        html = """
        <div>            
            <a href="/general-8"><p>About Us</p></a>
        </div>
        """
        dom = HTMLParser(html)
        a = dom.css_first("a")
        assert is_semantic_by_ancestry(a) is True

    def test_semantic_by_ancestry_positive(self):
        html = """
        <div>
            <p>About Us</p>
            <a href="/general-8">Visit</a>
        </div>
        """
        dom = HTMLParser(html)
        a = dom.css_first("a")
        assert is_semantic_by_ancestry(a) is True

    def test_semantic_by_ancestry_negative(self):
        html = """
        <div>
            <p>Gallery</p>
            <a href="/general-8">Visit</a>
        </div>
        """
        dom = HTMLParser(html)
        a = dom.css_first("a")
        assert is_semantic_by_ancestry(a) is False

    def test_semantic_by_ancestry_nested(self):
        html = """
        <div>
            <div>
                <div>
                    <span>Contact Information</span>
                    <a href="/random-page">Click</a>
                </div>
            </div>
        </div>
        """
        dom = HTMLParser(html)
        a = dom.css_first("a")
        assert is_semantic_by_ancestry(a) is True

    def test_semantic_by_ancestry_no_text(self):
        html = """
        <div>
            <div>
                <a href="/random-page">Click</a>
            </div>
        </div>
        """
        dom = HTMLParser(html)
        a = dom.css_first("a")
        assert is_semantic_by_ancestry(a) is False
