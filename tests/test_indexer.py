from matcher.indexer import InMemoryIndex
from matcher.scorer import score


def test_index_and_score():
    idx = InMemoryIndex()
    idx.add({"name": "Test Company", "domain": "example.com"})
    s = score(idx.all()[0], {"name": "Test Company"})
    assert isinstance(s, float)
