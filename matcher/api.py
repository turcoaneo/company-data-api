import meilisearch
from fastapi import APIRouter
from pydantic import BaseModel

from .indexer import InMemoryIndex

matcher_router = APIRouter(
    prefix="/api",
    tags=["Matcher"],
)

in_mem_index = InMemoryIndex()  # to be used later

client = meilisearch.Client("http://localhost:7700")
index = client.index("companies")


class MatchRequest(BaseModel):
    name: str | None = None
    website: str | None = None
    phone: str | None = None
    facebook: str | None = None


@matcher_router.post("/match")
def match_company(req: MatchRequest):
    query_parts = []

    if req.name:
        query_parts.append(req.name)

    if req.website:
        query_parts.append(req.website)

    if req.phone:
        query_parts.append(req.phone)

    if req.facebook:
        query_parts.append(req.facebook)

    query = " ".join(query_parts)

    result = index.search(query, {"limit": 1})

    if result["hits"]:
        return result["hits"][0]

    return {"message": "No match found"}
