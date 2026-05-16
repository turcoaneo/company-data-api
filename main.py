# main.py

from multiprocessing import Process
from app import create_app
from app.utils.env_vars import APP_ENV, SCRAPER_CONFIG
from app.utils.logger_util import get_logger
from app.utils.monitor_resources import start_monitor_daemon
from cron_jobs.scraper_job import start_scraper_loop

import uvicorn

app = create_app()


def start_scraper_process(interval_sec: int = 1200, is_looped: bool = True):
    p = Process(
        target=start_scraper_loop,
        kwargs={"interval_sec": interval_sec, "is_looped": is_looped},
        daemon=False,
    )
    p.start()
    return p


if __name__ == "__main__":
    exposed_port = 80 if APP_ENV in ["uat", "prod"] else 8000
    logger = get_logger("main_app_and_cron")
    logger.info(f"APP_ENV = {APP_ENV}, binding to port {exposed_port}")

    # Run scraper in a separate process
    looped = SCRAPER_CONFIG["looped"]
    interval_seconds = int(SCRAPER_CONFIG["interval"])
    scraper_proc = start_scraper_process(interval_sec=interval_seconds, is_looped=looped)

    # Monitor resources (still safe)
    start_monitor_daemon()

    uvicorn.run(app, host="0.0.0.0", port=exposed_port)
