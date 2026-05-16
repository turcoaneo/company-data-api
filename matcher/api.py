from fastapi import APIRouter
from pydantic import BaseModel
from .indexer import InMemoryIndex
from .scorer import score

router = APIRouter()
index = InMemoryIndex()


class MatchQuery(BaseModel):
    name: str | None = None
    domain: str | None = None
    phone: str | None = None
    facebook: str | None = None


@router.post("/match")
def match_company(query: MatchQuery):
    best = None
    best_score = -1.0
    for item in index.all():
        s = score(item, query.dict())
        if s > best_score:
            best_score = s
            best = item
    return {"score": best_score, "match": best}
