# main.py

from app import create_app
from app.utils.env_vars import APP_ENV
from app.utils.logger_util import get_logger
from app.utils.monitor_resources import start_monitor_daemon
from cron_jobs.scraper_job import start_scraper_loop

app = create_app()
logger = get_logger()

if __name__ == "__main__":
    exposed_port = 80 if APP_ENV in ["uat", "prod"] else 8000
    logger.info(f"APP_ENV = {APP_ENV}, binding to port {exposed_port}")

    # Optional: start scraper loop alongside FastAPI
    start_scraper_loop(interval_sec=5, is_looped=True)

    # Monitor resources
    start_monitor_daemon()

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=exposed_port)
