# app/__init__.py

from fastapi import FastAPI
from matcher.api import matcher_router as matcher_router
from app.service.service_metrics import run_metrics
from app.utils.logger_util import get_logger


def create_app() -> FastAPI:
    app = FastAPI(
        title="Company Data API",
        version="0.1.0",
        description="Veridion tech challenge – company data matching API",
    )

    logger = get_logger("api")
    logger.debug("Starting app")

    @app.get("/scraper/metrics")
    def run_and_get_metrics():
        return run_metrics()

    @app.get("/scraper/history/summary")
    def scraper_history_summary():
        from app.service.service_history import get_history_summary
        return get_history_summary()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(matcher_router, prefix="/api")

    return app
