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


@matcher_router.post(
    "/match",
    summary="Match a company",
    description="Attempts to match a company using name, website, phone, or Facebook profile."
)
def match_company(req: MatchRequest):
    hit = service.match(req.name, req.website, req.phone, req.facebook)
    return hit or {"message": "No match found"}


@matcher_router.post(
    "/match-top",
    summary="Match a company using the TOP index",
    description="Attempts to match a company using the top-ranked Meili index."
)
def match_top(req: MatchRequest):
    hit = service.match_top(req.name, req.website, req.phone, req.facebook)
    return hit or {"message": "No match found"}


@matcher_router.post(
    "/match/sanitized",
    summary="Sanitized match",
    description="Match a company using sanitized inputs (ignores punctuation-only fields)."
)
def sanitized_match(req: MatchRequest):
    hit = service.sanitized_match(req.name, req.website, req.phone, req.facebook)
    return hit or {"message": "No match found"}


@matcher_router.post(
    "/match-top/sanitized",
    summary="Sanitized match using TOP index",
    description="Match a company using sanitized inputs against the TOP index."
)
def sanitized_match_top(req: MatchRequest):
    hit = service.sanitized_match_top(req.name, req.website, req.phone, req.facebook)
    return hit or {"message": "No match found"}


@matcher_router.get(
    "/search",
    summary="Search companies",
    description="Full‑text search across company names, domains, phones, and socials."
)
def search(q: str, limit: int = 10):
    return service.search(q, limit)


@matcher_router.get(
    "/suggest",
    summary="Suggest company names",
    description="Autocomplete suggestions based on company name prefixes."
)
def suggest(prefix: str, limit: int = 5):
    return service.suggest(prefix, limit)


@matcher_router.get(
    "/match/sample",
    summary="Run sample matcher benchmark",
    description="Runs the matcher against the sample CSV and returns match results."
)
def match_sample():
    return service.match_sample()


@matcher_router.get(
    "/match-top/sample",
    summary="Run sample matcher benchmark using TOP index",
    description="Runs the matcher against the sample CSV using the TOP index."
)
def match_sample_top():
    return service.match_sample_top()
