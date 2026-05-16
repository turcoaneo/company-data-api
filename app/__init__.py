from fastapi import FastAPI
from matcher.api import matcher_router
from app.api.scraper_router import scraper_router
from app.utils.logger_util import get_logger


def create_app() -> FastAPI:
    app = FastAPI(
        title="Company Data API",
        version="0.1.0",
        description="Veridion tech challenge – company data matching & scraper metrics API",
        openapi_tags=[
            {"name": "Scraper", "description": "Scraper metrics, history, and cron job details."},
            {"name": "Matcher", "description": "Company data matching endpoints."},
            {"name": "Health", "description": "Service health checks."},
        ],
    )

    logger = get_logger("api")
    logger.debug("Starting app")

    @app.get("/health", tags=["Health"], summary="Health check")
    def health():
        return {"status": "ok"}

    app.include_router(scraper_router)
    app.include_router(matcher_router)

    return app
