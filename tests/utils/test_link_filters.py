# tests/utils/test_link_filters.py

from crawler.util.link_filters import is_semantic, is_garbage, is_low_signal


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
