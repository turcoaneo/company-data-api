# app/api/scraper_router.py

from fastapi import APIRouter

from app.service.service_history import get_history_summary
from app.service.service_metrics import run_metrics

scraper_router = APIRouter(prefix="/scraper")


@scraper_router.get("/metrics")
def run_and_get_metrics():
    return run_metrics()


@scraper_router.get("/history/summary")
def scraper_history_summary():
    return get_history_summary()
