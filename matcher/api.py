# matcher/api.py

from fastapi import APIRouter
from pydantic import BaseModel
from .service import MatcherService

matcher_router = APIRouter(prefix="/api", tags=["Matcher"])
service = MatcherService()


class MatchRequest(BaseModel):
    name: str | None = None
    website: str | None = None
    phone: str | None = None
    facebook: str | None = None


@matcher_router.post("/match")
def match_company(req: MatchRequest):
    hit = service.match(req.name, req.website, req.phone, req.facebook)
    return hit or {"message": "No match found"}


@matcher_router.get("/search")
def search(q: str, limit: int = 10):
    return service.search(q, limit)


@matcher_router.get("/suggest")
def suggest(prefix: str, limit: int = 5):
    return service.suggest(prefix, limit)
