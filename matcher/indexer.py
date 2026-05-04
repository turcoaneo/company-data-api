from typing import List, Dict

class InMemoryIndex:
    def __init__(self):
        self._items: List[Dict] = []

    def add(self, item: dict) -> None:
        self._items.append(item)

    def all(self) -> List[dict]:
        return self._items
