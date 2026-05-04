import pytest
from crawler.parser import parse_contacts

def test_parse_contacts_minimal():
    html = "<html><body><a href='tel:+40123456789'>Call</a></body></html>"
    result = parse_contacts(html)
    assert isinstance(result, dict)
