from fastapi import FastAPI

from app.utils.env_vars import APP_ENV


def create_app() -> FastAPI:
    from fastapi import FastAPI
    from matcher.api import router as matcher_router
    from app.utils.logger_util import get_logger

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

    app.include_router(matcher_router, prefix="/api")
    return app
