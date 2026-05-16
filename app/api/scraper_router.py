from fastapi import APIRouter

from app.service.service_history import get_history_summary
from app.service.service_metrics import run_metrics

scraper_router = APIRouter(
    prefix="/scraper",
    tags=["Scraper"],
)


@scraper_router.get("/metrics", summary="Get scraper metrics", description="Returns latest and top scraper metrics.")
def run_and_get_metrics():
    return run_metrics()


@scraper_router.get(
    "/history/summary",
    summary="Get scraper run history summary",
    description="Aggregated history of scraper runs (phones, socials, config, ISP, duration).",
)
def scraper_history_summary():
    return get_history_summary()
