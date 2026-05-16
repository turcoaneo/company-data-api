from fastapi import FastAPI

from app.api.scraper_router import scraper_router
from app.utils.logger_util import get_logger
from matcher.api import matcher_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Company Data API",
        version="0.1.0",
        description="Veridion tech challenge – company data matching API",
    )

    logger = get_logger("api")
    logger.debug("Starting app")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Attach routers
    app.include_router(scraper_router)
    app.include_router(matcher_router, prefix="/api")

    return app
