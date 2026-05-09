# tests/utils/test_semantic_extractor.py

from crawler.util.semantic_extractor import extract_semantic_links

HTML = """
<html>
  <body>
    <a href="/contact">Contact</a>
    <a href="/about-us">About</a>
    <a href="/blog/post">Blog</a>
    <a href="/file.pdf">PDF</a>
  </body>
</html>
"""


class TestSemanticExtractor:

    def test_extract_semantic_links(self):
        links = extract_semantic_links("https://example.com", HTML)
        assert "https://example.com/contact" in links
        assert "https://example.com/about-us" in links
        assert len(links) == 2
